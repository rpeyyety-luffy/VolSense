"""
data.py - Stage 1 of VolSense.

Downloads India VIX and Nifty 50 daily data since 2015 and saves one clean CSV.
Data path: NSE calculates the numbers -> Yahoo Finance stores the history ->
the yfinance library fetches it into a pandas table for us.

Run it with:  python3 data.py
"""

import os                 # to build file paths and create the data/ folder
import yfinance as yf     # "as yf" is just a short nickname, so we type less
import pandas as pd       # pandas = tables (DataFrames) in Python

# ---- Settings: kept at the top so they're easy to find and change ----
START_DATE = "2015-01-01"
VIX_TICKER = "^INDIAVIX"  # India VIX - the "fear index" we want to predict
NIFTY_TICKER = "^NSEI"    # Nifty 50 - helper data, because VIX reacts to Nifty moves
DATA_FOLDER = "data"
CSV_PATH = os.path.join(DATA_FOLDER, "market_data.csv")  # "data/market_data.csv"


def download_one(ticker):
    """Download daily price history for one ticker and return it as a DataFrame."""
    print(f"Downloading {ticker} from Yahoo Finance ...")

    df = yf.download(
        ticker,
        start=START_DATE,
        progress=False,           # hide the loading bar, keeps output clean
        auto_adjust=True,         # say it explicitly; indexes have no dividends anyway
        multi_level_index=False,  # WHY: simple column names like "Close",
                                  # not pairs like ("Close", "^INDIAVIX")
    )

    # WHY: if Yahoo sends nothing (no internet, Yahoo down), stop right here
    # with a clear message instead of crashing later with a confusing error.
    if df.empty:
        raise ValueError(f"No data received for {ticker}. Check your internet and try again.")

    return df


def build_dataset():
    """Download both tickers, keep the useful columns, and join them by date."""
    vix = download_one(VIX_TICKER)
    nifty = download_one(NIFTY_TICKER)

    # Keep only the columns we need, and rename them so we know which is which.
    # WHY: both tables have a column called "Close" - after joining we'd mix them up.
    vix = vix[["Close"]].rename(columns={"Close": "vix_close"})
    nifty = nifty[["Close", "High", "Low"]].rename(
        columns={"Close": "nifty_close", "High": "nifty_high", "Low": "nifty_low"}
    )

    # Join side by side using the date. how="inner" keeps only dates present in BOTH.
    data = vix.join(nifty, how="inner")

    # WHY: a row with a missing value can't be used for training, so drop it.
    data = data.dropna()

    data = data.sort_index()   # make sure dates go oldest -> newest
    data.index.name = "Date"   # name the date column in the CSV
    return data


def save_dataset(data):
    """Save the table to CSV and print a short summary so we can check it."""
    os.makedirs(DATA_FOLDER, exist_ok=True)  # exist_ok=True: no error if folder exists
    data.to_csv(CSV_PATH)

    print(f"Saved {len(data)} rows to {CSV_PATH}")
    print(f"From {data.index[0].date()} to {data.index[-1].date()}")
    print(data.tail())  # last 5 rows, to eyeball that numbers look sensible


# WHY: this block runs only when you type "python3 data.py".
# If another file does "import data" (features.py later), it will NOT re-download.
if __name__ == "__main__":
    dataset = build_dataset()
    save_dataset(dataset)
