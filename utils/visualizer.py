import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st
from textblob import TextBlob
import matplotlib.pyplot as plt
import seaborn as sns

class Visualizer:
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3

    def create_distribution_plot(self, df, column):
        """Create distribution plot for a column"""
        if df is None or df.empty or column not in df.columns:
            return None
        
        if df[column].dtype in ['object', 'bool']:
            # Categorical distribution
            value_counts = df[column].value_counts()
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=f"Distribution of {column}",
                labels={'x': column, 'y': 'Count'}
            )
        else:
            # Numerical distribution
            fig = px.histogram(
                df,
                x=column,
                title=f"Distribution of {column}",
                nbins=30
            )
            
        fig.update_layout(showlegend=False)
        return fig

    def create_correlation_heatmap(self, df):
        """Create correlation heatmap for numerical columns"""
        if df is None or df.empty:
            return None
        
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        numerical_cols = [col for col in numerical_cols if col not in ['Response_ID']]
        
        if len(numerical_cols) < 2:
            return None
        
        corr_matrix = df[numerical_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            title="Correlation Heatmap",
            color_continuous_scale="RdBu",
            aspect="auto"
        )
        
        return fig

    def create_scatter_plot(self, df, x_col, y_col, color_col=None):
        """Create scatter plot between two variables"""
        if df is None or df.empty or x_col not in df.columns or y_col not in df.columns:
            return None
        
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col if color_col and color_col in df.columns else None,
            title=f"{y_col} vs {x_col}"
        )
        
        return fig

    def create_time_series_plot(self, df, date_col, value_col):
        """Create time series plot"""
        if df is None or df.empty or date_col not in df.columns or value_col not in df.columns:
            return None
        
        # Ensure date column is datetime
        try:
            df[date_col] = pd.to_datetime(df[date_col])
        except:
            return None
        
        # Group by date and aggregate
        time_series_data = df.groupby(df[date_col].dt.date)[value_col].mean().reset_index()
        
        fig = px.line(
            time_series_data,
            x=date_col,
            y=value_col,
            title=f"{value_col} Over Time"
        )
        
        return fig

    def create_box_plot(self, df, x_col, y_col):
        """Create box plot for categorical vs numerical comparison"""
        if df is None or df.empty or x_col not in df.columns or y_col not in df.columns:
            return None
        
        fig = px.box(
            df,
            x=x_col,
            y=y_col,
            title=f"{y_col} by {x_col}"
        )
        
        return fig

    def create_sentiment_analysis(self, df, text_columns):
        """Perform sentiment analysis on text columns"""
        if df is None or df.empty or not text_columns:
            return None, None
        
        sentiment_data = []
        
        for col in text_columns:
            if col not in df.columns:
                continue
                
            for idx, text in df[col].dropna().items():
                try:
                    blob = TextBlob(str(text))
                    sentiment_data.append({
                        'column': col,
                        'text': text[:100] + '...' if len(str(text)) > 100 else text,
                        'polarity': blob.sentiment.polarity,
                        'subjectivity': blob.sentiment.subjectivity,
                        'sentiment': 'positive' if blob.sentiment.polarity > 0.1 else 'negative' if blob.sentiment.polarity < -0.1 else 'neutral'
                    })
                except:
                    continue
        
        if not sentiment_data:
            return None, None
        
        sentiment_df = pd.DataFrame(sentiment_data)
        
        # Create sentiment distribution plot
        fig_dist = px.histogram(
            sentiment_df,
            x='sentiment',
            color='column',
            title="Sentiment Distribution by Column",
            barmode='group'
        )
        
        # Create polarity vs subjectivity scatter plot
        fig_scatter = px.scatter(
            sentiment_df,
            x='polarity',
            y='subjectivity',
            color='sentiment',
            hover_data=['text'],
            title="Sentiment Analysis: Polarity vs Subjectivity"
        )
        
        return fig_dist, fig_scatter

    def create_dashboard_overview(self, df, summary_stats):
        """Create overview dashboard with key metrics"""
        if df is None or df.empty:
            return None
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Data Overview', 'Column Types', 'Missing Values', 'Data Quality'),
            specs=[[{"type": "table"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "indicator"}]]
        )
        
        # Data overview table
        overview_data = [
            ['Total Rows', df.shape[0]],
            ['Total Columns', df.shape[1]],
            ['Memory Usage', f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"],
            ['Date Range', f"{df['Timestamp'].min()} to {df['Timestamp'].max()}" if 'Timestamp' in df.columns else 'N/A']
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value']),
                cells=dict(values=list(zip(*overview_data)))
            ),
            row=1, col=1
        )
        
        # Column types pie chart
        dtype_counts = df.dtypes.value_counts()
        fig.add_trace(
            go.Pie(
                labels=dtype_counts.index.astype(str),
                values=dtype_counts.values,
                name="Column Types"
            ),
            row=1, col=2
        )
        
        # Missing values bar chart
        missing_values = df.isnull().sum()
        missing_values = missing_values[missing_values > 0]
        
        if not missing_values.empty:
            fig.add_trace(
                go.Bar(
                    x=missing_values.index,
                    y=missing_values.values,
                    name="Missing Values"
                ),
                row=2, col=1
            )
        
        # Data quality indicator
        quality_score = (1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=quality_score,
                title={'text': "Data Quality Score"},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "darkblue"},
                       'steps': [{'range': [0, 50], 'color': "lightgray"},
                                {'range': [50, 80], 'color': "yellow"},
                                {'range': [80, 100], 'color': "green"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 90}}
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=False, title_text="Data Dashboard Overview")
        return fig

    def create_trend_analysis(self, df, date_col, metrics):
        """Create trend analysis visualization"""
        if df is None or df.empty or date_col not in df.columns:
            return None
        
        try:
            df[date_col] = pd.to_datetime(df[date_col])
        except:
            return None
        
        # Group by date and calculate trends
        daily_trends = df.groupby(df[date_col].dt.date)[metrics].mean().reset_index()
        
        fig = go.Figure()
        
        for metric in metrics:
            if metric in daily_trends.columns:
                fig.add_trace(go.Scatter(
                    x=daily_trends[date_col],
                    y=daily_trends[metric],
                    mode='lines+markers',
                    name=metric,
                    line=dict(width=2)
                ))
        
        fig.update_layout(
            title="Trends Over Time",
            xaxis_title="Date",
            yaxis_title="Value",
            hovermode='x unified'
        )
        
        return fig

    def create_predictive_chart(self, historical_data, predictions, metric_name):
        """Create visualization showing historical data and predictions"""
        if not historical_data or not predictions:
            return None
        
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=list(range(len(historical_data))),
            y=historical_data,
            mode='lines+markers',
            name='Historical Data',
            line=dict(color='blue')
        ))
        
        # Predictions
        prediction_x = list(range(len(historical_data), len(historical_data) + len(predictions)))
        fig.add_trace(go.Scatter(
            x=prediction_x,
            y=predictions,
            mode='lines+markers',
            name='Predictions',
            line=dict(color='red', dash='dash')
        ))
        
        # Add vertical line to separate historical and predicted data
        fig.add_vline(x=len(historical_data)-0.5, line_dash="dot", line_color="gray")
        
        fig.update_layout(
            title=f"{metric_name} - Historical Data and Predictions",
            xaxis_title="Time Period",
            yaxis_title=metric_name,
            hovermode='x unified'
        )
        
        return fig
