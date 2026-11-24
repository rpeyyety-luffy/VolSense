"""
charts.py - Person 1 (Data)

Functions that take our data table and RETURN a Plotly figure.
Returning (not showing) the figure lets Streamlit place it on the page.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def vix_nifty_chart(df):
    """Nifty on top, VIX below, sharing the same dates."""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("Nifty 50", "India VIX"), vertical_spacing=0.08)
    fig.add_trace(go.Scatter(x=df.index, y=df["Nifty"], name="Nifty 50"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["VIX"], name="India VIX",
                             line=dict(color="crimson")), row=2, col=1)
    fig.update_layout(height=550, showlegend=False, margin=dict(t=40, b=20))
    return fig


# TODO(Person 1): add more chart functions, e.g.
#   vix_history_chart(df)            - VIX with calm (13) / fearful (20) lines
#   feature_importance_chart(model)  - together with Person 2
