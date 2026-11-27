"""
agent.py - Stage 4 of VolSense.

The Random Forest (model.py) DECIDES the prediction.
Gemini only EXPLAINS it in simple words for option buyers and sellers.

Needs: GEMINI_API_KEY in the .env file (never in this code).
Run it with:  python3 agent.py
"""

import os
import time                      # time.sleep(seconds) = pause the program
import pandas as pd
from dotenv import load_dotenv   # reads the .env file
from google import genai         # Google's official Gemini library
from google.genai import errors  # Gemini's error types, so we can read the error code

from model import predict_today

FEATURES_CSV = os.path.join("data", "features.csv")
MAIN_MODEL = "gemini-3.5-flash-lite"  # tried first - has worked every time in our tests
BACKUP_MODEL = "gemini-3.6-flash"     # tried only if the main model keeps failing
RETRY_CODES = (429, 503)              # 429 = too many requests, 503 = busy -> temporary
WAIT_SECONDS = [2]                    # 1 retry after 2s -> 2 attempts per model
FALLBACK_TEXT = "Explanation is unavailable right now. The prediction itself is still valid."


def load_api_key():
    """Read GEMINI_API_KEY from .env. Stop with a clear message if it's missing."""
    load_dotenv()  # copies NAME=value lines from .env into the program's settings
    key = os.getenv("GEMINI_API_KEY")  # gives None if the name isn't found
    if not key:  # catches both None (missing) and "" (empty after the =)
        raise ValueError("GEMINI_API_KEY not found. Put it in the .env file.")
    return key  # WHY never print it: printed text can end up in screenshots or logs


def signal_strength(probability_up):
    """Turn the probability into 'weak' / 'moderate' / 'strong'."""
    # abs() removes the minus sign: 0.465 -> |0.465 - 0.5| = 0.035
    distance = abs(probability_up - 0.5)
    # WHY: our model's edge is modest (AUC 0.58), so near-50% calls must be called weak
    if distance < 0.05:
        return "weak"       # between 45% and 55%
    elif distance < 0.10:
        return "moderate"   # 40-45% or 55-60%
    else:
        return "strong"     # below 40% or above 60%


def get_market_context():
    """Read today's row from features.csv and pick 4 numbers a trader understands."""
    data = pd.read_csv(FEATURES_CSV, index_col="Date", parse_dates=True)
    latest = data.iloc[-1]  # iloc[-1] = the last row = the most recent day
    # float(): plain Python numbers (easy to put in JSON later). * 100: fraction -> percent
    return {
        "vix": round(float(latest["vix_close"]), 2),
        "vix_vs_avg20_pct": round(float(latest["vix_vs_avg20"]) * 100, 1),
        "vix_change_5d_pct": round(float(latest["vix_change_5d"]) * 100, 1),
        "nifty_return_5d_pct": round(float(latest["nifty_return_5d"]) * 100, 1),
    }


def build_prompt(prediction, context, strength):
    """Write the instructions + facts we send to Gemini."""
    direction = "rise" if prediction["prediction"] == "UP" else "fall"
    # Triple quotes """...""" = a string over many lines. The f in front fills in {values}.
    # :.0% shows 0.465 as "47%". :+.1f shows 12.3 as "+12.3" (always with a sign).
    return f"""You are explaining a volatility forecast to Indian retail option traders.

FACTS (use only these numbers, do not invent any others):
- Model prediction: India VIX is more likely to {direction} over the next 5 trading days.
- Probability that VIX rises: {prediction["probability_up"]:.0%}
- Signal strength: {strength}
- India VIX today: {context["vix"]}
- VIX compared with its 20-day average: {context["vix_vs_avg20_pct"]:+.1f}%
- VIX change over the last 5 days: {context["vix_change_5d_pct"]:+.1f}%
- Nifty 50 change over the last 5 days: {context["nifty_return_5d_pct"]:+.1f}%

TASK: In 4 to 6 short sentences of simple English, explain what this means
for option BUYERS and for option SELLERS over the next 5 trading days.

RULES:
- Do not change or argue with the prediction.
- If the signal strength is weak, clearly say the outlook is uncertain.
- Explain any options word you use (for example "premium") in a few words.
- No bullet points and no headings.
- End with exactly this sentence: Educational, not financial advice.
"""


def try_one_model(client, model_name, prompt):
    """Try ONE model: 1 first attempt + 1 retry per WAIT_SECONDS entry. Return text or None."""
    # WHY: number of tries comes from WAIT_SECONDS, so the two can never disagree.
    max_attempts = len(WAIT_SECONDS) + 1  # len([2]) = 1 wait -> 1 + 1 = 2 attempts
    for attempt in range(max_attempts):   # attempt = 0, 1
        try:
            response = client.models.generate_content(model=model_name, contents=prompt)
            print(f"Answer from {model_name}")
            return response.text.strip()  # success -> leave the function straight away
        except errors.APIError as error:
            print(f"{model_name} failed with code {error.code}")
            # WHY: only busy/too-many errors are temporary. A 404 or 401 won't fix itself.
            if error.code not in RETRY_CODES or attempt == max_attempts - 1:
                return None  # give up on this model (last try, or error that won't fix itself)
            wait = WAIT_SECONDS[attempt]  # attempt 0 -> 2s
            print(f"Waiting {wait} seconds, then trying again...")
            time.sleep(wait)
        except Exception as error:
            # e.g. no internet, or Gemini sent back no text. Not worth retrying.
            print(f"{model_name} failed: {error}")
            return None


def ask_gemini(prompt):
    """Try the main model, then the backup. Never crash the program."""
    try:
        client = genai.Client(api_key=load_api_key())  # connect using our secret key
    except Exception as error:
        print(f"Gemini setup failed: {error}")  # e.g. key missing from .env
        return FALLBACK_TEXT

    for model_name in [MAIN_MODEL, BACKUP_MODEL]:  # main first, backup second
        text = try_one_model(client, model_name, prompt)
        if text:  # got a real answer -> done, don't try the backup
            return text

    # WHY: both models failed - the prediction must still reach the website.
    # The website (Stage 5-6) can still show UP/DOWN, just without the explanation.
    return FALLBACK_TEXT


def explain_prediction():
    """Main function: prediction + market numbers + Gemini explanation, in one dictionary."""
    prediction = predict_today()                       # Stage 3: the model decides
    context = get_market_context()                     # today's numbers
    strength = signal_strength(prediction["probability_up"])
    prompt = build_prompt(prediction, context, strength)

    result = dict(prediction)   # copy, so we don't change predict_today's dictionary
    result.update(context)      # update() adds all keys from context into result
    result["strength"] = strength
    result["explanation"] = ask_gemini(prompt)         # Gemini only explains
    return result


if __name__ == "__main__":
    result = explain_prediction()
    print(f"Date: {result['date']}   Model: {result['model']}")
    print(f"Prediction: VIX {result['prediction']}  "
          f"(chance VIX rises: {result['probability_up']:.0%}, {result['strength']} signal)")
    print(f"India VIX today: {result['vix']}")
    print("\nGemini explains:\n" + result["explanation"])
