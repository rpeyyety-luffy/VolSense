# About me
I'm a first-year Computer Science (Data Science) student at VIT Pune.
I know basic Python only. Right now I'm building alone; 2 teammates join later.
I must be able to explain every line to hackathon judges.

# How to teach me
- Before any code, explain the plan in simple English, step by step.
- Write at most 40 lines at a time, then stop and wait.
- Comment important lines with WHY, not just what.
- No advanced Python tricks unless you explain them first.
- After each piece, ask me one question to check I understood.
- When something fails, give hints first, not the fix, unless I say "just fix it".
- I use a Mac: python3, source venv/bin/activate.

# Project: VolSense
Predicts whether India VIX will rise or fall over the next 5 trading days,
and Gemini explains what it means for option buyers and sellers.
Hackathon: Build & Grow AI (FinTech). Deployed on Vercel (volsense.vercel.app).
No Streamlit. Python does the AI; the website only displays results.

# Build stages (in order)
1. data.py      - download India VIX (^INDIAVIX) + Nifty 50 (^NSEI) since 2015, save CSV
2. features.py  - features + target (1 if VIX higher 5 trading days later)
3. model.py     - baseline, Logistic Regression, Random Forest; predict_today()
4. agent.py     - Gemini explains the prediction; later a chat agent with tools
5. daily_update.py - writes public/prediction.json
6. public/      - HTML/CSS/JS website on Vercel reading prediction.json
7. .github/workflows/daily.yml - runs daily_update.py every weekday 4:30 PM IST
8. api/chat.py  - Vercel Python function for live chat with Gemini

# Rules
- Split data by time, never randomly.
- Features may only use data available on that day. Only target uses shift(-5).
- Never put the Gemini API key in code. It lives in .env (local) or Secrets (online).

# Progress
- Stage 1 done: data.py saves data/market_data.csv (vix_close, nifty_close/high/low).
- Stage 2 done: features.py saves data/features.csv (7 features + target; last 5 rows have NaN target).
- Stage 3 done: model.py. Train 2015-2022, test 2023-2026 (5-day gap).
  Random Forest is best: test AUC 0.581, accuracy 54.3% vs baseline 50.9%.
  predict_today() returns {date, prediction, probability_up, model}.
  It retrains on all labelled data every run (random_state=42, so same result each run). No .pkl is saved.
- Stage 4 done: agent.py. Main model gemini-3.5-flash-lite, backup gemini-3.6-flash,
  2 attempts per model (2s wait) on 503/429, then fallback text (never crashes).
  explain_prediction() returns the prediction + market numbers + strength + explanation in one dictionary.
  Not committed to git yet (agent.py, requirements.txt).