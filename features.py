"""
features.py - Stage 2 of VolSense.

Reads data/market_data.csv (made by data.py), creates features (clues for the model)
and the target (the answer), and saves data/features.csv.

RULE: every feature uses only today and past days. Only the target looks ahead (shift(-5)).

Run it with:  python3 features.py
"""

import os
import pandas as pd

INPUT_CSV = os.path.join("data", "market_data.csv")
OUTPUT_CSV = os.path.join("data", "features.csv")
DAYS_AHEAD = 5  # we predict VIX 5 trading days into the future

# The list of clue columns. model.py will import this list, so both files agree.
FEATURE_COLS = [
    "vix_change_1d",
    "vix_change_5d",
    "vix_vs_avg20",
    "nifty_return_1d",
    "nifty_return_5d",
    "nifty_range",
    "nifty_volatility_20d",
]


def load_data():
    """Read the CSV from Stage 1. parse_dates turns the Date text into real dates."""
    return pd.read_csv(INPUT_CSV, index_col="Date", parse_dates=True)


def add_features(data):
    """Add the clue columns. Each one only looks at today and the past."""
    vix = data["vix_close"]
    nifty = data["nifty_close"]

    # pct_change(1) = (today - yesterday) / yesterday. 0.08 means +8%.
    data["vix_change_1d"] = vix.pct_change(1)
    data["vix_change_5d"] = vix.pct_change(5)  # compared with 5 days AGO (past, safe)

    # Today's VIX vs its average of the last 20 days (including today).
    # +0.30 = VIX is 30% above normal -> it often falls back (mean reversion).
    data["vix_vs_avg20"] = vix / vix.rolling(20).mean() - 1

    data["nifty_return_1d"] = nifty.pct_change(1)
    data["nifty_return_5d"] = nifty.pct_change(5)

    # How far Nifty swung inside today, as a fraction of the close.
    data["nifty_range"] = (data["nifty_high"] - data["nifty_low"]) / nifty

    # Standard deviation of the last 20 daily returns = how jumpy Nifty has been.
    data["nifty_volatility_20d"] = data["nifty_return_1d"].rolling(20).std()

    return data


def add_target(data):
    """target = 1 if VIX is higher 5 trading days later, else 0. The ONLY look-ahead."""
    # shift(-5) pulls the value from 5 rows BELOW (the future) up into today's row.
    future_vix = data["vix_close"].shift(-DAYS_AHEAD)

    # True/False -> 1.0/0.0. We use float (not int) so the column can also hold NaN.
    target = (future_vix > data["vix_close"]).astype(float)

    # WHY: for the last 5 days the future is unknown (future_vix is NaN).
    # Without this line, "NaN > number" is False, so they'd wrongly get target 0.
    # .where(condition) keeps values where condition is True, puts NaN elsewhere.
    data["target"] = target.where(future_vix.notna())

    # Note: we do NOT save future_vix as a column - that would leak the answer.
    return data


def build_features():
    """Load -> add features -> add target -> drop the warm-up rows."""
    data = load_data()
    data = add_features(data)
    data = add_target(data)

    # WHY: the first ~20 rows have NaN features (not enough history for rolling(20)).
    # We drop only rows with missing FEATURES - the last 5 rows (missing target only)
    # stay, because predict_today() in Stage 3 needs today's features.
    data = data.dropna(subset=FEATURE_COLS)
    return data


def save_features(data):
    """Save to CSV and print a summary so we can sanity-check."""
    data.to_csv(OUTPUT_CSV)

    labelled = data.dropna(subset=["target"])  # rows where we know the answer
    print(f"Saved {len(data)} rows to {OUTPUT_CSV}")
    print(f"Rows with a known target (for training/testing): {len(labelled)}")
    print(f"Rows without a target (recent days, for predicting): {len(data) - len(labelled)}")
    print(f"Share of days where VIX went UP 5 days later: {labelled['target'].mean():.1%}")
    print(data[FEATURE_COLS + ["target"]].tail(7).round(4))


if __name__ == "__main__":
    features = build_features()
    save_features(features)
