import streamlit as st
import pandas as pd
import time
import sys
import os
import yaml
import asyncio

# Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.storage.sqlite_manager import SQLiteManager
from src.analytics.core.ols_hedge import OLSHedgeRatio
from src.analytics.core.spread_analysis import SpreadAnalysis
from src.analytics.core.correlation import RollingCorrelation
from src.analytics.core.adf_test import ADFTest
from src.analytics.advanced.kalman_filter import KalmanFilterHedge
from src.analytics.advanced.backtest_engine import BacktestEngine
from src.analytics.advanced.heatmap_generator import HeatmapGenerator
from src.alerts.alert_engine import AlertEngine

from src.frontend.components import price_charts, stats_table, alert_manager
from src.frontend.utils import data_exporter

# Config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../config.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

st.set_page_config(page_title=config['frontend']['title'], layout="wide")
st.title("Real-Time Quantitative Analytics Dashboard")

# --- Sidebar Controls ---
st.sidebar.header("Data Source")
data_source = st.sidebar.radio("Source", ["Live Binance Feed", "Upload OHLC Data"])

# Database
db = SQLiteManager()
# FIX: Uppercase match
all_symbols = [s.upper() for s in config['ingestion']['symbols']]

# Global Data Container
df_y = pd.DataFrame()
df_x = pd.DataFrame()
sym_y = ""
sym_x = ""

# 1. Data Selection Logic
if data_source == "Live Binance Feed":
    st.sidebar.subheader("Live Configuration")
    sym_y = st.sidebar.selectbox("Asset Y (Dependent)", all_symbols, index=0)
    sym_x = st.sidebar.selectbox("Asset X (Independent)", all_symbols, index=1)
    # Default to 1s for immediate gratification
    timeframe = st.sidebar.selectbox("Timeframe", ["1s", "1m", "5m"], index=0)
    limit = 500
    
    # Auto-Refresh Logic (Default OFF to prevent black screen on slow connections)
    refresh_rate = st.sidebar.slider("Refresh Rate (s)", 1, 60, 5)
    
    if st.sidebar.toggle("Auto-Refresh On", value=False):
        time.sleep(refresh_rate)
        st.rerun()
    else:
        st.sidebar.info("Toggle Auto-Refresh for live updates")
        if st.sidebar.button("Manual Refresh"):
            st.rerun()

    # Fetch Data
    df_y = db.fetch_recent_data(sym_y, timeframe, limit)
    df_x = db.fetch_recent_data(sym_x, timeframe, limit)

else:
    st.sidebar.subheader("Upload Configuration")
    uploaded_file = st.sidebar.file_uploader("Upload CSV (Time, Symbol, Open, Close...)", type="csv")
    if uploaded_file:
        raw_df = pd.read_csv(uploaded_file)
        # Expect minimal columns: timestamp, symbol, close
        if {'timestamp', 'symbol', 'close'}.issubset(raw_df.columns):
            raw_df['timestamp'] = pd.to_datetime(raw_df['timestamp'])
            symbols_in_file = raw_df['symbol'].unique()
            
            if len(symbols_in_file) < 2:
                st.error("CSV must contain at least 2 symbols for pair analysis.")
            else:
                sym_y = st.sidebar.selectbox("Asset Y", symbols_in_file, index=0)
                sym_x = st.sidebar.selectbox("Asset X", symbols_in_file, index=1)
                
                df_y = raw_df[raw_df['symbol'] == sym_y].copy().set_index('timestamp').sort_index()
                df_x = raw_df[raw_df['symbol'] == sym_x].copy().set_index('timestamp').sort_index()
                
                # Standardize columns for analytics
                for d in [df_y, df_x]:
                    if 'volume' not in d.columns: d['volume'] = 0
                    if 'high' not in d.columns: d['high'] = d['close']
                    if 'low' not in d.columns: d['low'] = d['close']
                    if 'open' not in d.columns: d['open'] = d['close']
                    
        else:
            st.error("CSV format must include: timestamp, symbol, close")

# --- Analytics Controls ---
st.sidebar.markdown("---")
st.sidebar.header("Analytics Settings")

window_size = st.sidebar.number_input("Rolling Window Size", min_value=10, max_value=200, value=20)
z_threshold = alert_manager.render_alert_manager()
hedge_method = st.sidebar.radio("Hedge Ratio Method", ["OLS (Static Window)", "Kalman Filter (Dynamic)"])

# --- Main Processor ---

if df_y.empty or df_x.empty:
    st.info(f"Waiting for data... (Fetched {len(df_y)} rows for Y, {len(df_x)} rows for X). Try '1s' timeframe.")
    st.stop()

# Align Data (Outer Join + Fill)
if 'timestamp' in df_y.columns: 
    df_y.set_index('timestamp', inplace=True)
if 'timestamp' in df_x.columns:
    df_x.set_index('timestamp', inplace=True)

# Outer join to keep timepoints where only one asset moved across
df = pd.merge(df_y, df_x, left_index=True, right_index=True, suffixes=('_y', '_x'), how='outer')
df.sort_index(inplace=True)
# Ensure we have datetime index type for merging
df.ffill(inplace=True) # Carry forward last known price (Fixed deprecated method)
df.dropna(inplace=True) # Drop initial rows where one asset is missing

# --- Basic Analytics (Requires only 1 point) ---
# Simple Spread (latest prices)
current_hedge = 1.0 # Default if OLS not ready
if len(df) > 1:
     # Simple static hedge for display if window not ready
     current_hedge = df['close_y'].iloc[-1] / df['close_x'].iloc[-1]

raw_spread = df['close_y'] - (current_hedge * df['close_x'])

# --- Dashboard Layout (Basic) ---
# Display prices IMMEDIATELY so user knows it's working
st.subheader("Live Market Data")
m1, m2, m3 = st.columns(3)
m1.metric(f"{sym_y} Price", f"{df['close_y'].iloc[-1]:.2f}")
m2.metric(f"{sym_x} Price", f"{df['close_x'].iloc[-1]:.2f}")
m3.metric("Raw Spread (Est)", f"{raw_spread.iloc[-1]:.4f}")
st.caption(f"Last DB Tick Time: {df.index[-1]}")

# System Status in Sidebar
st.sidebar.markdown("---")
if len(df) >= window_size:
    st.sidebar.success(f"⚡ System Status: ACTIVE ({len(df)} bars)")
else:
    st.sidebar.warning(f"⏳ System Warmup: {len(df)}/{window_size} synced bars")

# Price Chart
st.plotly_chart(price_charts.plot_price_history(df_y, sym_y), use_container_width=True)

# --- Advanced Analytics (Requires Window) ---
if len(df) < window_size:
    st.info(f"❄️ Analytics Engine is initializing... Need {window_size} common timestamps to run regression tests.")
    st.progress(min(len(df) / window_size, 1.0))
    st.markdown("**Recommendation:** Switch Timeframe to **1s** for faster warmup.")
    st.stop()

# Analytics Engines
ols = OLSHedgeRatio()
spread_analyzer = SpreadAnalysis()
corr_analyzer = RollingCorrelation()
adf = ADFTest()
backtester = BacktestEngine()
alerter = AlertEngine(threshold=z_threshold)

# 1. Hedge Ratio & Spread Calculation
if hedge_method.startswith("OLS"):
    hedge_ratio = ols.calculate(df['close_y'], df['close_x'])
    spread = spread_analyzer.calculate_spread(df['close_y'], df['close_x'], hedge_ratio)
    st.sidebar.metric("Hedge Ratio (Static OLS)", f"{hedge_ratio:.4f}")
else:
    # Kalman Filter
    betas = []
    kf = KalmanFilterHedge()
    for r in range(len(df)):
        b = kf.update(df['close_y'].iloc[r], df['close_x'].iloc[r])
        betas.append(b)
    
    hedge_ratio_series = pd.Series(betas, index=df.index)
    spread = df['close_y'] - (hedge_ratio_series * df['close_x'])
    hedge_ratio = betas[-1]
    st.sidebar.metric("Hedge Ratio (Kalman)", f"{hedge_ratio:.4f}")

# 2. Z-Score
zscore = spread_analyzer.calculate_zscore(spread * 0, window=window_size)

# 3. Correlation
correlation = corr_analyzer.calculate(df['close_y'], df['close_x'], window=window_size)

# 4. Alerts (Live Evaluation)
latest_z = zscore.iloc[-1] if not zscore.empty else 0
alert = alerter.check_zscore(f"{sym_y}-{sym_x}", latest_z)
alert_manager.display_alerts(alerter.get_latest_alerts())

# Metrics Continued
st.markdown("---")
st.metric("Current Z-Score", f"{latest_z:.2f}", delta_color="inverse")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Spread & Signals")
    st.plotly_chart(price_charts.plot_spread_zscore(spread, zscore, z_threshold, -z_threshold), use_container_width=True)

with col2:
    st.subheader("Statistical Tests")
    
    # ADF Test Trigger
    if st.button("Run ADF Test on Spread"):
        is_stat, p_val = adf.is_stationary(spread)
        st.write(f"**P-Value:** {p_val:.4f}")
        if is_stat:
            st.success("Spread is Stationary (Mean Reverting)")
        else:
            st.error("Spread is Non-Stationary")
            
    st.markdown("---")
    st.subheader("Backtest (Mean Reversion)")
    pnl = backtester.run_mean_reversion(spread, zscore, z_threshold, 0)
    st.plotly_chart(price_charts.plot_price_history(pd.DataFrame({'timestamp':pnl.index, 'open':pnl, 'high':pnl, 'low':pnl, 'close':pnl}), "Cumulative PnL"), use_container_width=True)
    st.metric("Total PnL", f"{pnl.iloc[-1]:.2f}")

    st.markdown("---")
    st.subheader("Correlations")
    st.plotly_chart(price_charts.plot_price_history(pd.DataFrame({'timestamp':correlation.index, 'open':correlation, 'high':correlation, 'low':correlation, 'close':correlation}), f"Rolling Corr ({window_size})"), use_container_width=True)

# Heatmap Section (Advanced)
with st.expander("Advanced: Multi-Symbol Heatmap"):
    if st.button("Generate Live Heatmap"):
        heatmap_df = pd.DataFrame()
        # Fetch data for all symbols
        for s in all_symbols:
            d = db.fetch_recent_data(s, timeframe, 100)
            if not d.empty:
                d = d.set_index('timestamp')
                # Resample ensure alignment
                d = d[~d.index.duplicated(keep='first')]
                heatmap_df[s] = d['close']
        
        if not heatmap_df.empty:
            hg = HeatmapGenerator()
            matrix = hg.generate(heatmap_df)
            st.plotly_chart(hg.plot(matrix), use_container_width=True)
        else:
            st.warning("Insufficient data for heatmap.")

# Detailed Stats & Export
st.markdown("---")
st.subheader("Asset Statistics")
stats_table.display_stats(df_y)

st.download_button("Download Processed Data", 
                   data_exporter.convert_df_to_csv(df), 
                   "processed_data.csv", 
                   "text/csv")
