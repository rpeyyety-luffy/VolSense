"""
app.py - Person 3 (App)

The Streamlit dashboard. It only DISPLAYS things - all logic lives in
features.py, model.py and agent.py.

Run:  streamlit run app.py
"""

import streamlit as st

from features import get_data
from model import predict_today
from agent import explain, ask_agent
from charts import vix_nifty_chart

st.set_page_config(page_title="VolSense", page_icon="📈", layout="wide")


# cache_data = download once, reuse for 1 hour (makes the app fast)
@st.cache_data(ttl=3600)
def load():
    return get_data(), predict_today()


df, pred = load()

# ---- Header ----
st.title("VolSense")
st.caption("Know if the market will be calm or stormy, before it happens.")
st.info("India VIX is the market's 'fear meter': higher means traders expect bigger swings. "
        "VolSense is a risk-awareness tool, not financial advice.")

# ---- Today's numbers ----
c1, c2, c3, c4 = st.columns(4)
c1.metric("India VIX", pred["vix"])
c2.metric("Nifty 50", f"{pred['nifty']:,.0f}")
c3.metric("Next 5 days", "VIX ↑ rise" if pred["direction"] == "rise" else "VIX ↓ fall")
c4.metric("Confidence", f"{pred['confidence']:.0%}")

st.subheader("What this means")
st.write(explain(pred))

# ---- Charts ----
st.subheader("History")
st.plotly_chart(vix_nifty_chart(df), use_container_width=True)

# ---- Track record ----
st.subheader("How good is the model?")
a1, a2 = st.columns(2)
a1.metric("Model accuracy (test years)", f"{pred['test_accuracy']:.0%}")
a2.metric("Baseline (always guessing)", f"{pred['baseline_accuracy']:.0%}")
# TODO(Person 2/3): feature-importance chart and track-record chart

# ---- AI chat ----
st.subheader("Ask VolSense AI")
if "messages" not in st.session_state:
    st.session_state.messages = []  # keeps chat history between reruns

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

question = st.chat_input("e.g. Is this a calm week for option sellers?")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)
    answer = ask_agent(question, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
