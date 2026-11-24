"""
daily_update.py - Person 2 (ML), used in Week 3

Runs the model, asks Gemini for a summary, and saves public/prediction.json
for the Vercel website. GitHub Actions runs this every weekday.

Run:  python daily_update.py
"""

import json
from model import predict_today
from agent import explain

OUTPUT = "public/prediction.json"

if __name__ == "__main__":
    pred = predict_today()
    pred["summary"] = explain(pred)
    with open(OUTPUT, "w") as f:
        json.dump(pred, f, indent=2)
    print("Saved", OUTPUT)
    print(pred)
