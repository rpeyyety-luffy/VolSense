# About us
We are 3 first-year Computer Science students: [Person 1], [Person 2], [Person 3].
We know basic Python only. We are learning pandas, scikit-learn, Streamlit and Gemini.
We must be able to explain every line to hackathon judges.

# How to teach us
- Before any code, explain the plan in simple English, step by step.
- Write at most 40 lines at a time, then stop and wait.
- Put a short comment above each important line saying WHY, not just what.
- No advanced Python tricks (lambda chains, decorators, list-comprehension puzzles) unless you explain them first.
- After each piece, ask us one question to check we understood.
- When something fails, give hints first, not the fix, unless we say "just fix it".

# Project
VolSense: predicts whether India VIX rises or falls over the next 5 trading days
and explains it with a Gemini agent. Hackathon: Build & Grow AI (FinTech).
Stack: Python, pandas, scikit-learn, Plotly, Streamlit, google-genai.
Later: HTML/CSS/JS page in public/ on Vercel reading public/prediction.json.
We use a Mac: python3, source venv/bin/activate.

# Contract between files (never change without telling the team)
- features.py -> get_data(): table with Date index, VIX, Nifty, feature columns, target
- model.py    -> predict_today(): dict with date, vix, nifty, direction, confidence,
                 test_accuracy, baseline_accuracy
- public/prediction.json has the same keys as predict_today(), plus "summary"

# Rules
- Split data by time, never randomly.
- Features may only use data available on that day. Only target uses shift(-5).
- Never put the Gemini API key in code. It lives in .env (local) or Secrets (online).
- Files marked "FAKE VERSION" are placeholders; replace them, keep the same output shape.
