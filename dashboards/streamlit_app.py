# dashboards/streamlit_app.py

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta

API_BASE = "http://api:8000"

# -------------------------------------------------------
# Page Config
# -------------------------------------------------------
st.set_page_config(
    page_title="GlobalPulse Analytics",
    page_icon="",
    layout="wide"
)

# -------------------------------------------------------
# Sidebar Navigation + Date Filters
# -------------------------------------------------------
st.sidebar.title("Dashboard Navigation")

page = st.sidebar.radio("Go to", [
    "Overview",
    "Daily Sentiment",
    "Keywords",
    "Sources",
    "Entities"
])

st.sidebar.markdown("---")
st.sidebar.subheader("Date Range")

range_type = st.sidebar.selectbox(
    "Select Range",
    ["All Time", "1 Day", "7 Days", "30 Days", "90 Days", "180 Days", "YTD", "Custom Date"]
)

def build_params():
    """Convert sidebar selection into API query params."""
    today = date.today()

    if range_type == "All Time":
        return ""

    if range_type == "1 Day":
        return f"?days=1"

    if range_type == "7 Days":
        return f"?days=7"

    if range_type == "30 Days":
        return f"?days=30"

    if range_type == "90 Days":
        return f"?days=90"

    if range_type == "180 Days":
        return f"?days=180"

    if range_type == "YTD":
        cutoff = date(today.year, 1, 1)
        return f"?after={cutoff}"

    if range_type == "Custom Date":
        custom = st.sidebar.date_input("Start Date", today - timedelta(days=7))
        return f"?after={custom}"

    return ""

QUERY_PARAMS = build_params()

# -------------------------------------------------------
# Utility: Fetch from API
# -------------------------------------------------------
def fetch(url):
    try:
        return requests.get(f"{API_BASE}{url}{QUERY_PARAMS}", timeout=20).json()
    except Exception:
        return None

# -------------------------------------------------------
# Custom Colors
# -------------------------------------------------------
COLOR_POS = "#4CAF50"
COLOR_NEG = "#F44336"
COLOR_NEU = "#2196F3"
COLOR_ERR = "#9E9E9E"

# -------------------------------------------------------
# Card Component
# -------------------------------------------------------
def stat_card(label, value, color):
    st.markdown(
        f"""
        <div style="
            padding:20px;
            border-radius:12px;
            background-color:#1e1e1e;
            border-left:6px solid {color};
            margin-bottom:12px;">
            <h4 style="margin:0;color:white;">{label}</h4>
            <h2 style="margin:0;color:{color};">{value}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------------
# MAIN TITLE
# -------------------------------------------------------
st.title("GlobalPulse — Analytics Dashboard")
st.markdown("### Real-time insights from global news: sentiment, keywords, sources, and entities.")

# -------------------------------------------------------
# PAGES
# -------------------------------------------------------

# ------------------ OVERVIEW ------------------
if page == "Overview":
    st.subheader("Sentiment Overview")

    sent = fetch("/analytics/sentiment-summary")
    if sent:
        c1, c2, c3, c4 = st.columns(4)
        with c1: stat_card("Positive", sent["positive"], COLOR_POS)
        with c2: stat_card("Negative", sent["negative"], COLOR_NEG)
        with c3: stat_card("Neutral", sent["neutral"], COLOR_NEU)
        with c4: stat_card("Errors", sent["error"], COLOR_ERR)

        pie_data = pd.DataFrame({
            "Sentiment": ["Positive", "Negative", "Neutral", "Error"],
            "Count": [sent["positive"], sent["negative"], sent["neutral"], sent["error"]]
        })

        fig = px.pie(
            pie_data,
            values="Count",
            names="Sentiment",
            color="Sentiment",
            color_discrete_map={
                "Positive": COLOR_POS,
                "Negative": COLOR_NEG,
                "Neutral": COLOR_NEU,
                "Error": COLOR_ERR
            },
            title="Sentiment Distribution"
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Could not load sentiment summary.")

# ------------------ DAILY SENTIMENT ------------------
# ------------------ DAILY SENTIMENT ------------------
if page == "Daily Sentiment":
    st.subheader("Daily Sentiment Trend")

    # Use the SAME query params as the rest of the dashboard
    daily = fetch("/analytics/daily-sentiment")

    if daily:
        rows = [{"date": d, **vals} for d, vals in daily.items()]
        df = pd.DataFrame(rows).sort_values("date")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["date"], y=df["positive"], mode="lines+markers", name="Positive", line=dict(color=COLOR_POS)))
        fig.add_trace(go.Scatter(x=df["date"], y=df["negative"], mode="lines+markers", name="Negative", line=dict(color=COLOR_NEG)))
        fig.add_trace(go.Scatter(x=df["date"], y=df["neutral"], mode="lines+markers", name="Neutral", line=dict(color=COLOR_NEU)))

        fig.update_layout(
            title="Sentiment Over Time",
            xaxis_title="Date",
            yaxis_title="Count",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Could not load daily sentiment.")

# ------------------ KEYWORDS ------------------
if page == "Keywords":
    st.subheader("Most Common Keywords")

    keywords = fetch("/analytics/keyword-frequency")

    if keywords:
        df_kw = pd.DataFrame(keywords)
        fig = px.bar(
            df_kw.head(40),
            x="word",
            y="count",
            title="Top Keywords",
            text_auto=True,
            color="count",
            color_continuous_scale="Blues"
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Unable to load keywords.")

# ------------------ SOURCES ------------------
if page == "Sources":
    st.subheader("Sentiment by News Source")

    source_data = fetch("/analytics/source-sentiment")

    if source_data:
        rows = [{"source": s, **vals} for s, vals in source_data.items()]
        df_src = pd.DataFrame(rows)

        fig = px.bar(
            df_src,
            x="source",
            y=["positive", "negative", "neutral"],
            title="Sentiment by Source",
            barmode="group",
            color_discrete_map={
                "positive": COLOR_POS,
                "negative": COLOR_NEG,
                "neutral": COLOR_NEU
            }
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Could not load source sentiment.")

# ------------------ ENTITIES ------------------
if page == "Entities":
    st.subheader("Trending Entities")

    ENTITY_COLORS = {
        "person": "#FF6B6B",
        "organization": "#6C5CE7",
        "location": "#00CEC9",
        "product": "#FDCB6E",
        "other": "#4A90E2"
    }

    entities = fetch("/analytics/top-entities")

    if entities:
        df = pd.DataFrame(entities)
        df = df[df["count"] > 1].head(100)  # only show top 28 with count > 1

        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Displayed Entities", len(df))
        with c2: st.metric("Unique Entities (Displayed)", df["entity"].nunique())
        with c3: st.metric("Top Category (Displayed)", df["type"].value_counts().idxmax())

        cols = st.columns(4)
        for i, row in enumerate(df.to_dict("records")):
            with cols[i % 4]:
                st.markdown(
                    f"""
                    <div style="
                        padding:15px;
                        margin-bottom:10px;
                        border-radius:10px;
                        background-color:#1e1e1e;
                        border-left:4px solid {ENTITY_COLORS.get(row['type'], '#4A90E2')};
                    ">
                        <span style="font-size:18px;font-weight:600;color:{ENTITY_COLORS.get(row['type'], '#4A90E2')};">
                            {row['entity']}
                        </span><br>
                        <span style="color:#BBBBBB;font-size:14px;">
                            {row['type'].title()} • {row['count']} mentions
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.error("Could not load entity data.")