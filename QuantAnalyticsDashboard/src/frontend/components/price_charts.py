import plotly.graph_objects as go
import plotly.express as px

def plot_price_history(df, symbol):
    fig = go.Figure()
    # Use Line chart for clarity on small datasets (1s updates)
    # df.index is timestamp because we set_index in app.py logic passing here?
    # Actually app.py passes df_y which has 'timestamp' column or index? 
    # In app.py: `if 'timestamp' in df_y.columns: df_y.set_index...`
    # Warning: plot_price_history expects df with 'timestamp' column in previous version.
    # Let's support both index/column to be safe.
    
    x_val = df.index if 'timestamp' not in df.columns else df['timestamp']
    
    fig.add_trace(go.Scatter(x=x_val, y=df['close'], mode='lines+markers', name=symbol))
    
    fig.update_layout(title=f"{symbol} Price History", xaxis_title="Time", yaxis_title="Price")
    return fig

def plot_spread_zscore(spread, zscore, upper=2, lower=-2):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=zscore.index, y=zscore.values, name="Z-Score", line=dict(color='blue')))
    
    # Thresholds
    fig.add_hline(y=upper, line_dash="dash", line_color="red", annotation_text="Short Entry")
    fig.add_hline(y=lower, line_dash="dash", line_color="green", annotation_text="Long Entry")
    fig.add_hline(y=0, line_dash="solid", line_color="gray")
    
    fig.update_layout(title="Z-Score & Signals", xaxis_title="Time", yaxis_title="Z-Score")
    return fig
