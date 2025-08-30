#!/usr/bin/env python
# src/research_crew/main.py
# import sys, pathlib
# sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # adds .../src

from datetime import date
from pathlib import Path
import streamlit as st
from research_crew.crew import ResearchCrew
from research_crew.state_store import get_topic, set_topic
import research_crew
import yfinance as yf
import plotly.graph_objs as go
import re

OUTPUT_DIR = Path(research_crew.__file__).resolve().parent / "output"
current_year = date.today().year

st.set_page_config(page_title="Research Crew", layout="wide")
st.title("🔎 Research Crew")

# ---- Inputs ----
topic = st.text_input("Topic", placeholder="e.g., Apple Inc.")
colA, colB = st.columns([1,1])
with colA:
    use_cache = st.checkbox("Use cache if available", value=True)
with colB:
    run_btn = st.button("Run Research", type="primary", use_container_width=True)

# Keep results across reruns
if "report_md" not in st.session_state:
    st.session_state.report_md = None
if "from_cache" not in st.session_state:
    st.session_state.from_cache = False

# ---- On click ----
if run_btn:
    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    # 1) Try cache
    if use_cache:
        cached = get_topic(topic.strip())
        if cached and cached.get("report_md"):
            st.session_state.report_md = cached["report_md"]
            st.session_state.from_cache = True
        else:
            with st.spinner("Running ResearchCrew…"):
                res = ResearchCrew().crew().kickoff(inputs={"topic": topic.strip(),"year":current_year})
            # 2) Robust parsing: prefer tasks_output[-1].raw; fallback to res.raw
            report_md = None
            try:
                if getattr(res, "tasks_output", None):
                    last = res.tasks_output[-1]
                    report_md = getattr(last, "raw", None)
                if not report_md and hasattr(res, "raw"):
                    report_md = res.raw
            except Exception:
                report_md = str(res)
            st.session_state.report_md = report_md or "No report generated."
            st.session_state.from_cache = False
            # Save to cache
            set_topic(topic.strip(), {"report_md": st.session_state.report_md})
    else:
        with st.spinner("Running ResearchCrew…"):
            res = ResearchCrew().crew().kickoff(inputs={"topic": topic.strip(),"year":current_year})
        report_md = None
        try:
            if getattr(res, "tasks_output", None):
                last = res.tasks_output[-1]
                report_md = getattr(last, "raw", None)
            if not report_md and hasattr(res, "raw"):
                report_md = res.raw
        except Exception:
            report_md = str(res)
        st.session_state.report_md = report_md or "No report generated."
        st.session_state.from_cache = False

def get_ticker_from_report(report_md: str) -> str | None:
    m = re.search(r"ticker:\s*([A-Za-z\.^]+)", report_md)
    return m.group(1).upper() if m else None

# ---- Render ----
if st.session_state.report_md:
    st.success("Loaded from cache." if st.session_state.from_cache else "Generated new report.")
    st.markdown(st.session_state.report_md)

    # Build the expected file path for this topic
    safe_topic = topic.strip().replace(" ", "_")
    report_path = OUTPUT_DIR / f"{safe_topic}_Research_Brief.md"

    if report_path.exists():
        st.download_button(
            "Download Research Brief",
            data=report_path.read_bytes(),
            file_name=report_path.name,   # e.g. google_Research_Brief.md
            mime="text/markdown",
            use_container_width=True,
        )
    else:
        # fallback to in-memory version
        st.download_button(
            "Download report.md",
            data=st.session_state.report_md,
            file_name=f"report_{safe_topic or 'report'}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    symbol = get_ticker_from_report(st.session_state.report_md)
    if symbol:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1y")
        if not hist.empty:
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=hist.index,
                                        open=hist['Open'], high=hist['High'],
                                        low=hist['Low'], close=hist['Close'],
                                        name='Price'))
            fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume', yaxis='y2'))
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=50).mean(), name='50-day MA'))
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=200).mean(), name='200-day MA'))
            fig.update_layout(
                title=f"{symbol} Stock Analysis",
                yaxis_title='Price',
                yaxis2=dict(title='Volume', overlaying='y', side='right'),
                xaxis_rangeslider_visible=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No historical data available for {symbol}")

