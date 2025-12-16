import pandas as pd
import plotly.express as px

class HeatmapGenerator:
    def generate(self, price_dataframe):
        """
        price_dataframe: DataFrame with columns as symbols and index as time.
        """
        corr_matrix = price_dataframe.corr()
        return corr_matrix
    
    def plot(self, corr_matrix):
        fig = px.imshow(corr_matrix, 
                        text_auto=True, 
                        aspect="auto",
                        color_continuous_scale='RdBu_r',
                        range_color=[-1, 1],
                        title="Tick Correlation Matrix")
        return fig
