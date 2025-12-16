import streamlit as st

def render_alert_manager():
    st.sidebar.subheader("Alert Settings")
    z_threshold = st.sidebar.slider("Z-Score Threshold", 1.0, 5.0, 2.0, 0.1)
    return z_threshold

def display_alerts(alerts):
    if alerts:
        st.error(f"Active Alerts: {len(alerts)}")
        for a in alerts:
            st.warning(a['message'])
