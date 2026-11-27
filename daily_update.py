"""
daily_update.py - Stage 5 of VolSense.

One command that does the whole pipeline and saves the result for the website:
  fresh data -> features -> prediction + Gemini explanation -> public/prediction.json

GitHub Actions (Stage 7) will run this every weekday at 4:30 PM IST (after market close).
Run it with:  python3 daily_update.py
"""

import os
import json                       # turns a Python dictionary into a JSON text file
from datetime import datetime
from zoneinfo import ZoneInfo     # time zones; "Asia/Kolkata" = India time (IST)

from data import build_dataset, save_dataset
from features import build_features, save_features
from agent import explain_prediction, FALLBACK_TEXT

OUTPUT_JSON = os.path.join("public", "prediction.json")


def load_previous():
    """Read yesterday's prediction.json if it exists, else return None."""
    if not os.path.exists(OUTPUT_JSON):
        return None  # first run ever: there is no previous file
    try:
        with open(OUTPUT_JSON) as f:  # "with" closes the file automatically afterwards
            return json.load(f)        # JSON text -> Python dictionary
    except (json.JSONDecodeError, OSError):
        return None  # WHY: a broken old file must not stop today's update


def keep_last_good_explanation(result, previous):
    """Option A: if Gemini failed today, reuse the last good explanation, labelled with its date."""
    if result["explanation"] != FALLBACK_TEXT:
        result["explanation_date"] = result["date"]  # fresh explanation for today
        result["explanation_is_fresh"] = True
        return result

    # Gemini failed today. Do we have an older real explanation to fall back on?
    if previous and previous.get("explanation") and previous["explanation"] != FALLBACK_TEXT:
        result["explanation"] = previous["explanation"]
        # WHY keep the OLD date: the website must honestly say which day it's from
        result["explanation_date"] = previous.get("explanation_date")
    else:
        result["explanation_date"] = None  # nothing good to reuse; fallback text stays
    result["explanation_is_fresh"] = False
    return result


def main():
    print("Step 1/4: downloading fresh data ...")
    save_dataset(build_dataset())

    print("\nStep 2/4: building features ...")
    save_features(build_features())

    print("\nStep 3/4: predicting + asking Gemini ...")
    result = explain_prediction()
    result = keep_last_good_explanation(result, load_previous())

    # When this update ran, in India time, e.g. "2026-11-27 16:35 IST"
    result["updated_at"] = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M IST")

    print("\nStep 4/4: saving ...")
    os.makedirs("public", exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:  # "w" = write (replace the old file)
        json.dump(result, f, indent=2)  # indent=2: neat, readable, one item per line

    fresh = "fresh" if result["explanation_is_fresh"] else f"reused from {result['explanation_date']}"
    print(f"Saved {OUTPUT_JSON}: VIX {result['prediction']} "
          f"({result['probability_up']:.0%} chance of rise), explanation {fresh}")


if __name__ == "__main__":
    main()
