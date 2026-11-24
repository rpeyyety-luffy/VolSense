"""
features.py - Person 1 (Data)

Job: download India VIX + Nifty 50 data and build the table the model learns from.

CONTRACT: get_data() returns a pandas DataFrame with
    index   : Date
    columns : VIX, Nifty, <feature columns>, target

Right now get_data() is a FAKE VERSION that makes random numbers in the
right shape, so Person 2 and Person 3 can start working today.
Replace it step by step (see the TODO list below), keeping the same output.
"""

import numpy as np
import pandas as pd

START_DATE = "2015-01-01"

# Names of the feature columns the model will use.
# Person 1 and Person 2 must agree on this list.
FEATURE_COLUMNS = [
    "vix_change_1d",
    "vix_change_5d",
    "vix_vs_20d_avg",
    "nifty_return_1d",
    "nifty_return_5d",
    "nifty_volatility_10d",
]


def get_data():
    """FAKE VERSION - returns made-up data in the contract shape."""
    # TODO(Person 1), replace this whole function, one step at a time:
    #   1. Download ^INDIAVIX and ^NSEI closing prices with yfinance (see scripts/step1_download_vix.py)
    #   2. Put them in one table with columns VIX and Nifty; drop days where either is missing
    #   3. Add each column in FEATURE_COLUMNS (pct_change, rolling mean, rolling std)
    #   4. Add target: 1 if VIX is higher 5 trading days later, else 0  -> uses shift(-5)
    #   5. dropna() and return the table
    #   Rule: features may only use data from that day or earlier. Only target looks ahead.
    dates = pd.bdate_range(START_DATE, periods=2500)
    rng = np.random.default_rng(42)
    df = pd.DataFrame(index=dates)
    df.index.name = "Date"
    df["VIX"] = (15 + rng.normal(0, 2, len(dates))).clip(9, 40)
    df["Nifty"] = 8000 + rng.normal(0, 50, len(dates)).cumsum()
    for col in FEATURE_COLUMNS:
        df[col] = rng.normal(0, 1, len(dates))
    df["target"] = rng.integers(0, 2, len(dates))
    return df


if __name__ == "__main__":
    # Run `python features.py` to check the output quickly.
    data = get_data()
    print(data.head())
    print("Shape:", data.shape)
