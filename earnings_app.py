"""Earnings Report Alert System - Streamlit dashboard."""
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Data folder sits next to this script, so it works on Kaggle and locally
DATA_DIR = Path(__file__).parent / "data"

st.set_page_config(page_title="Earnings Report Alert System", layout="wide")


@st.cache_data
def load_data():
    backtest = pd.read_csv(DATA_DIR / "full_backtest.csv")
    fresh = pd.read_csv(DATA_DIR / "fresh_earnings.csv")
    company_perf = pd.read_csv(DATA_DIR / "company_performance.csv")
    with open(DATA_DIR / "summary_stats.json") as f:
        stats = json.load(f)
    return backtest, fresh, company_perf, stats


def fmt(value, suffix=""):
    """Format a number for display, showing N/A for missing values."""
    return "N/A" if pd.isna(value) else f"{value:.2f}{suffix}"


backtest_df, fresh_df, company_perf_df, stats = load_data()

st.title("📈 Earnings Report Alert System")
st.caption(
    f"Based on {stats['total_reports']:,} historical earnings reports across "
    f"{stats['total_companies']} S&P 500 companies · Last updated: {stats['last_updated']}"
)
st.warning(
    "⚠️ Not investment advice. Results are historical averages, are not adjusted "
    "for overall market movement, and may not repeat in the future."
)

# ============================================================
# Section 1: Historical reaction from the backtest
# ============================================================
st.header("📊 Historical Reaction (5 Trading Days)")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Beats that rose", f"{stats['beat_success_rate_5d']}%",
            help="Share of earnings beats where the price was higher after 5 trading days")
col2.metric("Avg change after beat", f"{stats['beat_avg_change_5d']:+.2f}%")
col3.metric("Misses that rose", f"{stats['miss_success_rate_5d']}%",
            help="Share of earnings misses where the price was higher after 5 trading days")
col4.metric("Avg change after miss", f"{stats['miss_avg_change_5d']:+.2f}%")

st.caption(f"Sample size: {stats['beat_sample_size']:,} beats, {stats['miss_sample_size']:,} misses")

st.divider()

# ============================================================
# Section 2: Latest earnings reports with advice
# ============================================================
st.header("🚨 Latest Earnings Reports (Last 3 Days)")

DECISION_STYLE = {"BUY": st.success, "SELL": st.error, "HOLD": st.info, "NO ESTIMATE": st.warning}

if fresh_df.empty:
    st.info("No earnings reports released in the last 3 days. Earnings are seasonal (quarterly), check back later.")
else:
    for _, row in fresh_df.sort_values("days_since").iterrows():
        with st.container(border=True):
            left, right = st.columns([2, 1])
            with left:
                st.subheader(row["ticker"])
                st.write(f"**EPS estimate:** {fmt(row['eps_estimate'])} | **Reported EPS:** {fmt(row['eps_reported'])}")
                st.write(f"**Surprise:** {fmt(row['surprise_pct'], '%')}")
                st.caption(f"Announced: {row['earnings_date']}")
            with right:
                show = DECISION_STYLE.get(row["decision"], st.info)
                show(f"**{row['decision']}**\n\n{row['note']}")

st.divider()

# ============================================================
# Section 3: Companies by average historical reaction
# ============================================================
st.header("🏢 Companies by Average 5-Day Reaction")

tab1, tab2 = st.tabs(["📈 Top 15", "📉 Bottom 15"])
with tab1:
    top15 = company_perf_df.nlargest(15, "avg_reaction_5d")
    fig1 = px.bar(top15, x="ticker", y="avg_reaction_5d", color="avg_reaction_5d",
                  color_continuous_scale=["gray", "green"],
                  title="Highest average reaction after earnings",
                  labels={"avg_reaction_5d": "Avg 5-day change (%)"})
    st.plotly_chart(fig1, width="stretch")
with tab2:
    bottom15 = company_perf_df.nsmallest(15, "avg_reaction_5d")
    fig2 = px.bar(bottom15, x="ticker", y="avg_reaction_5d", color="avg_reaction_5d",
                  color_continuous_scale=["red", "gray"],
                  title="Lowest average reaction after earnings",
                  labels={"avg_reaction_5d": "Avg 5-day change (%)"})
    st.plotly_chart(fig2, width="stretch")

st.divider()

# ============================================================
# Section 4: Full filterable backtest log
# ============================================================
st.header("📋 Full Backtest Log")

options = ["All"] + sorted(backtest_df["ticker"].unique().tolist())
selected = st.selectbox("Filter by company (optional):", options)
view_df = backtest_df if selected == "All" else backtest_df[backtest_df["ticker"] == selected]

st.dataframe(
    view_df[["ticker", "earnings_date", "timing", "surprise_pct",
             "pct_change_1d", "pct_change_3d", "pct_change_5d"]],
    width="stretch",
)
