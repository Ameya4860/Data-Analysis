import streamlit as st

def render_control_panel(symbols):
    st.sidebar.header("Configuration")
    
    selected_symbol_y = st.sidebar.selectbox("Select Asset Y (Dependent)", symbols, index=0)
    selected_symbol_x = st.sidebar.selectbox("Select Asset X (Independent)", symbols, index=1)
    
    timeframe = st.sidebar.selectbox("Timeframe", ["1s", "1m", "5m"], index=1)
    
    return selected_symbol_y, selected_symbol_x, timeframe
