"""
Step 1 - Download India VIX + Nifty 50 data and plot it.

Install once:
    pip install yfinance pandas plotly

Run:
    python step1_download_vix.py
"""

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

START_DATE = "2015-01-01"


def download(ticker):
    """Download daily closing prices for one ticker."""
    data = yf.Ticker(ticker).history(start=START_DATE)
    closes = data["Close"]
    closes.index = closes.index.tz_localize(None).normalize()  # clean dates
    return closes


print("Downloading data... (takes a few seconds)")
vix = download("^INDIAVIX")   # India VIX - the "fear meter"
nifty = download("^NSEI")     # Nifty 50 - the market itself

# Put both in one table, keep only days where both exist
df = pd.DataFrame({"VIX": vix, "Nifty": nifty}).dropna()
df.to_csv("vix_nifty_data.csv")  # share this file with teammates
print(f"Saved {len(df)} days of data to vix_nifty_data.csv\n")

# ---- Quick facts ----
print("Latest date     :", df.index[-1].date())
print("Latest VIX      :", round(df["VIX"].iloc[-1], 2))
print("Latest Nifty    :", round(df["Nifty"].iloc[-1], 2))
print("Average VIX     :", round(df["VIX"].mean(), 2))
print("Highest VIX     :", round(df["VIX"].max(), 2), "on", df["VIX"].idxmax().date())
print("Lowest VIX      :", round(df["VIX"].min(), 2), "on", df["VIX"].idxmin().date())

calm = (df["VIX"] < 13).mean() * 100
fear = (df["VIX"] > 20).mean() * 100
print(f"\nDays calm (VIX < 13)   : {calm:.1f}%")
print(f"Days fearful (VIX > 20): {fear:.1f}%")

# ---- Chart: Nifty on top, VIX below ----
fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    subplot_titles=("Nifty 50 (the market)", "India VIX (the fear meter)"),
                    vertical_spacing=0.08)

fig.add_trace(go.Scatter(x=df.index, y=df["Nifty"], name="Nifty 50"), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["VIX"], name="India VIX",
                         line=dict(color="crimson")), row=2, col=1)

# Reference lines on the VIX chart
fig.add_hline(y=13, line_dash="dot", line_color="green",
              annotation_text="calm", row=2, col=1)
fig.add_hline(y=20, line_dash="dot", line_color="orange",
              annotation_text="fearful", row=2, col=1)

fig.update_layout(height=700, title="Nifty 50 vs India VIX", showlegend=False)
fig.show()  # opens in your browser - zoom in on March 2020!
