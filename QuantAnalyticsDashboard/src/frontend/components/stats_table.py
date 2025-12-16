import pandas as pd
import streamlit as st

def display_stats(df):
    if df.empty:
        st.write("No data available")
        return

    latest = df.iloc[-1]
    stats = {
        "Latest Price": latest['close'],
        "Volume": latest['volume'],
        "High (Session)": df['high'].max(),
        "Low (Session)": df['low'].min(),
        "Volatility (Std)": df['close'].std()
    }
    st.table(pd.DataFrame([stats]))
