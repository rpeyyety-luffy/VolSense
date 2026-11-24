# VolSense

**Know if the market will be calm or stormy, before it happens.**

VolSense predicts whether **India VIX** (the market's "fear meter") will rise or fall over the next
5 trading days, and a **Gemini AI agent** explains what that means for option buyers and sellers.

Built for the **Build & Grow AI Hackathon** (FinTech track).

> ⚠️ VolSense is a risk-awareness tool, not financial advice.

---

## How it works

```
yfinance data → features.py → model.py → agent.py (Gemini) → app.py (Streamlit)
                                   ↓
                           daily_update.py → public/prediction.json → Vercel website
```

## Project structure

| File / folder | Owner | What it does |
|---|---|---|
| `features.py` | Person 1 | Downloads VIX + Nifty data, builds features and target |
| `charts.py` | Person 1 | Plotly chart functions |
| `model.py` | Person 2 | Trains the model, `predict_today()` |
| `agent.py` | Person 3 | Gemini explanation + agent with tools |
| `app.py` | Person 3 | Streamlit dashboard |
| `daily_update.py` | Person 2 | Writes `public/prediction.json` every weekday |
| `public/` | Person 1 | Static website for Vercel (HTML/CSS/JS) |
| `scripts/` | All | One-off scripts (data download test) |
| `notebooks/` | All | Experiments (not used by the app) |
| `data/` | — | Downloaded CSVs (not uploaded to GitHub) |

## The contract (don't change without telling the team)

- `features.get_data()` → pandas table with `Date` index, `VIX`, `Nifty`, feature columns, `target`
- `model.predict_today()` → dictionary:

```python
{
    "date": "2026-12-10",
    "vix": 14.2,
    "nifty": 24350.5,
    "direction": "rise",      # "rise" or "fall"
    "confidence": 0.64,       # 0 to 1
    "test_accuracy": 0.61,    # 0 to 1
    "baseline_accuracy": 0.54
}
```

- `public/prediction.json` has the same keys as `predict_today()`, plus `"summary"` (Gemini's text).

## Setup (Mac)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then paste your Gemini key into .env
streamlit run app.py
```

## Team

- Person 1: [name] — Data + Frontend
- Person 2: [name] — ML
- Person 3: [name] — AI + App

## License

MIT
