# dashboard/streamlit_app.py
from __future__ import annotations

import os
import time
import pandas as pd
import psycopg2
import streamlit as st
import altair as alt

# Configuration (defaults to Docker stack values)
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5433"))  
PG_DB = os.getenv("PG_DB", "credit_risk")
PG_USER = os.getenv("PG_USER", "credit")
PG_PASSWORD = os.getenv("PG_PASSWORD", "risk")

REFRESH_SECONDS = float(os.getenv("DASH_REFRESH", "3"))


def get_conn():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
    )


def load_data(limit: int = 5000):
    """Load latest data and calculate KPIs"""
    conn = get_conn()
    try:
        # Latest window for charts/tables
        df = pd.read_sql(
            f"""
            SELECT
              event_time,
              loan_id,
              purpose,
              term,
              loan_amnt,
              annual_inc,
              dti,
              int_rate_pct,
              revol_util_pct,
              delinq_2yrs,
              inq_last_6mths,
              credit_history_years,
              emp_length_yrs,
              dti_band,
              util_band,
              rate_band,
              early_warning_flag,
              risk_tier,
              reasons
            FROM risk_scored
            ORDER BY event_time DESC
            LIMIT {int(limit)};
            """,
            conn,
        )

        # KPIs
        total = pd.read_sql("SELECT COUNT(*) AS n FROM risk_scored;", conn)["n"].iloc[0]
        watchlist = pd.read_sql(
            "SELECT COUNT(*) AS n FROM risk_scored WHERE risk_tier='Watchlist';",
            conn,
        )["n"].iloc[0]

        elevated = pd.read_sql(
            "SELECT COUNT(*) AS n FROM risk_scored WHERE risk_tier='Elevated';",
            conn,
        )["n"].iloc[0]

        low = pd.read_sql(
            "SELECT COUNT(*) AS n FROM risk_scored WHERE risk_tier='Low';",
            conn,
        )["n"].iloc[0]

        # Recent rate (last 5 minutes)
        rate_df = pd.read_sql(
            """
            SELECT COUNT(*) AS n
            FROM risk_scored
            WHERE event_time >= NOW() - INTERVAL '5 minutes';
            """,
            conn,
        )
        last5_count = int(rate_df["n"].iloc[0])
        eps = last5_count / (5 * 60)

        return df, int(total), int(watchlist), int(elevated), int(low), float(eps)

    finally:
        conn.close()


def main():
    st.set_page_config(
        page_title="Credit Risk Monitoring (Real-Time)",
        page_icon="📉",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📈 Credit Risk Monitoring (Real-Time Demo)")
    st.markdown("Live streaming analysis of loan applications from Kafka → Redpanda → PostgreSQL")

    # Sidebar controls
    with st.sidebar:
        st.header("Controls")
        limit = st.slider("Rows to load (latest)", 500, 20000, 5000, step=500)
        refresh = st.slider("Auto-refresh (seconds)", 1, 10, int(REFRESH_SECONDS))
        show_raw = st.toggle("Show raw table", value=False)
        
        st.divider()
        st.caption(f"Database: {PG_HOST}:{PG_PORT}/{PG_DB}")
        st.caption("Tip: Keep the producer + consumer running in terminals.")

    # Load data
    with st.spinner("Loading data..."):
        try:
            df, total, watchlist_count, elevated_count, low_count, eps = load_data(limit=limit)
        except Exception as e:
            st.error(f"Failed to load data: {e}")
            st.stop()

    # Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Scored Events", f"{total:,}", delta=None)
    col2.metric("Watchlist", f"{watchlist_count:,}", delta_color="inverse")
    col3.metric("Elevated", f"{elevated_count:,}", delta_color="off")
    col4.metric("Low", f"{low_count:,}", delta_color="normal")
    col5.metric("Throughput (5m)", f"{eps:.2f} eps")

    if df.empty:
        st.warning("No data found. Please start the producer and consumer.")
        st.stop()

    # Ensure timestamps are datetime
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    
    st.divider()

    # Charts Row
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Risk Distribution (Latest Window)")
        
        if not df.empty:
            tier_chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('risk_tier', sort=['Watchlist', 'Elevated', 'Low'], title='Risk Tier'),
                y=alt.Y('count()', title='Count'),
                color=alt.Color('risk_tier', 
                               scale=alt.Scale(domain=['Watchlist', 'Elevated', 'Low'], 
                                             range=['#ff4b4b', '#ffa07a', '#22c55e']),
                               legend=None),
                tooltip=['risk_tier', 'count()']
            ).properties(height=300)
            st.altair_chart(tier_chart, use_container_width=True)

    with right_col:
        st.subheader("Watchlist Volume Over Time")
        
        if not df.empty:
            # Create 1-minute buckets for trend
            timeline_df = df.copy()
            timeline_df['time_bucket'] = timeline_df['event_time'].dt.floor('1min')
            
            # Filter for just watchlist or show all stacked
            trend_chart = alt.Chart(timeline_df).mark_line(point=True).encode(
                x=alt.X('time_bucket', title='Time (1 min buckets)'),
                y=alt.Y('count()', title='Events'),
                color=alt.Color('risk_tier', 
                               scale=alt.Scale(domain=['Watchlist', 'Elevated', 'Low'], 
                                             range=['#ff4b4b', '#ffa07a', '#22c55e'])),
                tooltip=['time_bucket', 'risk_tier', 'count()']
            ).properties(height=300)
            
            st.altair_chart(trend_chart, use_container_width=True)

    # Watchlist Table
    st.subheader(f"🚨 Latest Watchlist Events ({watchlist_count} Total)")
    
    wl_df = df[df["risk_tier"] == "Watchlist"]
    if wl_df.empty:
        st.info("No Watchlist events in the current loaded window.")
    else:
        display_cols = [
            "event_time", "loan_id", "risk_tier", "loan_amnt", "annual_inc", 
            "dti", "revol_util_pct", "delinq_2yrs", "reasons"
        ]
        st.dataframe(
            wl_df[display_cols].head(50),
            use_container_width=True,
            column_config={
                "event_time": st.column_config.DatetimeColumn("Time", format="HH:mm:ss"),
                "loan_amnt": st.column_config.NumberColumn("Loan Amt", format="$%d"),
                "annual_inc": st.column_config.NumberColumn("Income", format="$%d"),
                "revol_util_pct": st.column_config.NumberColumn("Util %", format="%.1f%%"),
                "dti": st.column_config.NumberColumn("DTI", format="%.1f"),
            }
        )

    # Raw Data (Optional)
    if show_raw:
        st.subheader("Raw Data Inspector")
        st.dataframe(df.head(100), use_container_width=True)

    # Auto-refresh logic
    time.sleep(refresh)
    st.rerun()


if __name__ == "__main__":
    main()
