import streamlit as st
from utils.visualizer import Visualizer
from utils.data_processor import DataProcessor
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Dashboard - BI StoryTeller",

    layout="wide"
)

st.title("Interactive Dashboard")
st.markdown("Real-time insights, trends, and predictions from your data analysis.")

# Check prerequisites
data_to_analyze = st.session_state.get('processed_data')
if data_to_analyze is None or data_to_analyze.empty:
    data_to_analyze = st.session_state.get('raw_data')

if data_to_analyze is None or data_to_analyze.empty:
    st.warning("No data available for dashboard. Please collect and analyze data first.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Data Collection"):
            st.switch_page("pages/3_Data_Collection.py")
    with col2:
        if st.button("Go to Analysis"):
            st.switch_page("pages/5_Analysis.py")
    st.stop()

# Initialize components
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = Visualizer()

visualizer = st.session_state.visualizer

# Dashboard overview metrics
st.header("Key Metrics Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Records",
        data_to_analyze.shape[0],
        help="Total number of data points collected"
    )

with col2:
    data_quality = (1 - data_to_analyze.isnull().sum().sum() / (data_to_analyze.shape[0] * data_to_analyze.shape[1])) * 100
    st.metric(
        "Data Quality",
        f"{data_quality:.1f}%",
        help="Percentage of complete data points"
    )

with col3:
    numerical_cols = data_to_analyze.select_dtypes(include=[np.number]).columns
    if len(numerical_cols) > 0:
        avg_response = data_to_analyze[numerical_cols].mean().mean()
        st.metric(
            "Avg Response",
            f"{avg_response:.2f}",
            help="Average value across numerical responses"
        )
    else:
        st.metric("Avg Response", "N/A")

with col4:
    if 'Timestamp' in data_to_analyze.columns:
        try:
            data_to_analyze['Timestamp'] = pd.to_datetime(data_to_analyze['Timestamp'])
            latest_response = data_to_analyze['Timestamp'].max()
            time_since = datetime.now() - latest_response
            if time_since.days > 0:
                st.metric("Latest Response", f"{time_since.days}d ago")
            elif time_since.seconds > 3600:
                st.metric("Latest Response", f"{time_since.seconds//3600}h ago")
            else:
                st.metric("Latest Response", f"{time_since.seconds//60}m ago")
        except:
            st.metric("Latest Response", "N/A")
    else:
        st.metric("Latest Response", "N/A")

with col5:
    categorical_cols = data_to_analyze.select_dtypes(include=['object']).columns
    unique_responses = sum([data_to_analyze[col].nunique() for col in categorical_cols if col not in ['Timestamp', 'Response_ID']])
    st.metric(
        "Response Variety",
        unique_responses,
        help="Total unique categorical responses"
    )

# Dashboard tabs
tab1, tab2, tab3, tab4 = st.tabs(["Trends", "Sentiment", "Predictions", "Insights"])

with tab1:
    st.header("Trend Analysis")
    
    # Time-based trends
    if 'Timestamp' in data_to_analyze.columns:
        try:
            data_to_analyze['Timestamp'] = pd.to_datetime(data_to_analyze['Timestamp'])
            
            # Select metrics for trend analysis
            numerical_cols = data_to_analyze.select_dtypes(include=[np.number]).columns
            numerical_cols = [col for col in numerical_cols if col not in ['Response_ID']]
            
            if len(numerical_cols) > 0:
                st.subheader("Numerical Trends Over Time")
                
                selected_metrics = st.multiselect(
                    "Select metrics to display",
                    options=numerical_cols,
                    default=numerical_cols[:3] if len(numerical_cols) >= 3 else numerical_cols
                )
                
                if selected_metrics:
                    fig = visualizer.create_trend_analysis(data_to_analyze, 'Timestamp', selected_metrics)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Trend summary
                    st.subheader("Trend Summary")
                    for metric in selected_metrics:
                        try:
                            daily_data = data_to_analyze.groupby(data_to_analyze['Timestamp'].dt.date)[metric].mean()
                            if len(daily_data) > 1:
                                trend = "increasing" if daily_data.iloc[-1] > daily_data.iloc[0] else "decreasing"
                                change = abs(daily_data.iloc[-1] - daily_data.iloc[0])
                                st.metric(
                                    f"{metric} Trend",
                                    f"{trend.title()}",
                                    delta=f"{change:.2f}" if trend == "increasing" else f"-{change:.2f}"
                                )
                        except:
                            continue
            
            # Response volume trends
            st.subheader("Response Volume Trends")
            daily_responses = data_to_analyze.groupby(data_to_analyze['Timestamp'].dt.date).size()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_responses.index,
                y=daily_responses.values,
                mode='lines+markers',
                name='Daily Responses',
                line=dict(color='#1f77b4', width=3)
            ))
            
            fig.update_layout(
                title="Daily Response Volume",
                xaxis_title="Date",
                yaxis_title="Number of Responses",
                hovermode='x'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating time-based trends: {str(e)}")
    
    else:
        st.info("No timestamp data available for trend analysis.")
        
        # Alternative: Show distribution trends
        st.subheader("Distribution Analysis")
        
        numerical_cols = data_to_analyze.select_dtypes(include=[np.number]).columns
        numerical_cols = [col for col in numerical_cols if col not in ['Response_ID']]
        
        if len(numerical_cols) > 0:
            selected_col = st.selectbox("Select variable for distribution analysis", numerical_cols)
            
            if selected_col:
                fig = visualizer.create_distribution_plot(data_to_analyze, selected_col)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Sentiment Analysis")
    
    # Find text columns for sentiment analysis
    text_columns = data_to_analyze.select_dtypes(include=['object']).columns
    text_columns = [col for col in text_columns if col not in ['Timestamp', 'Response_ID']]
    
    if text_columns:
        st.subheader("Text Response Sentiment")
        
        selected_text_cols = st.multiselect(
            "Select text columns for sentiment analysis",
            options=text_columns,
            default=text_columns[:2] if len(text_columns) >= 2 else text_columns
        )
        
        if selected_text_cols:
            if st.button("Analyze Sentiment", type="primary"):
                with st.spinner("Analyzing sentiment..."):
                    try:
                        fig_dist, fig_scatter = visualizer.create_sentiment_analysis(data_to_analyze, selected_text_cols)
                        
                        if fig_dist and fig_scatter:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.plotly_chart(fig_dist, use_container_width=True)
                            
                            with col2:
                                st.plotly_chart(fig_scatter, use_container_width=True)
                            
                            # Store sentiment results
                            st.session_state.sentiment_analyzed = True
                        else:
                            st.warning("Could not perform sentiment analysis on selected columns.")
                            
                    except Exception as e:
                        st.error(f"Error in sentiment analysis: {str(e)}")
        
        # Sentiment insights using AI
        if st.session_state.get('sentiment_analyzed'):
            st.subheader("🤖 AI Sentiment Insights")
            
            if st.button("Generate Sentiment Insights"):
                with st.spinner("Generating sentiment insights..."):
                    try:
                        # Create summary for sentiment analysis
                        text_summary = ""
                        for col in selected_text_cols:
                            sample_texts = data_to_analyze[col].dropna().head(10).tolist()
                            text_summary += f"\n{col}: {sample_texts}"
                        
                        sentiment_insights = st.session_state.groq_client.analyze_data(
                            text_summary, 
                            "sentiment and emotional tone"
                        )
                        
                        if sentiment_insights:
                            st.markdown(sentiment_insights)
                        else:
                            st.error("Failed to generate sentiment insights.")
                            
                    except Exception as e:
                        st.error(f"Error generating sentiment insights: {str(e)}")
    
    else:
        st.info("No text columns available for sentiment analysis.")
        
        # Alternative: Show categorical sentiment proxy
        st.subheader("Response Pattern Analysis")
        categorical_cols = data_to_analyze.select_dtypes(include=['object']).columns
        categorical_cols = [col for col in categorical_cols if col not in ['Timestamp', 'Response_ID']]
        
        if categorical_cols:
            for col in categorical_cols[:2]:  # Show first 2 categorical columns
                fig = visualizer.create_distribution_plot(data_to_analyze, col)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Predictions & Forecasting")
    
    st.subheader("Predictive Analysis")
    
    if st.button("Generate Predictions", type="primary"):
        with st.spinner("Generating predictions and forecasts..."):
            try:
                # Create data summary for predictions
                data_processor = DataProcessor()
                summary = data_processor.get_data_summary(data_to_analyze)
                
                # Generate predictions using AI
                predictions = st.session_state.groq_client.generate_predictions(str(summary))
                
                if predictions:
                    st.session_state.predictions = predictions
                    st.markdown(predictions)
                else:
                    st.error("Failed to generate predictions.")
                    
            except Exception as e:
                st.error(f"Error generating predictions: {str(e)}")
    
    # Display previous predictions
    if st.session_state.get('predictions'):
        st.subheader("Previous Predictions")
        st.markdown(st.session_state.predictions)
    
    # Trend-based predictions for numerical data
    numerical_cols = data_to_analyze.select_dtypes(include=[np.number]).columns
    numerical_cols = [col for col in numerical_cols if col not in ['Response_ID']]
    
    if len(numerical_cols) > 0 and 'Timestamp' in data_to_analyze.columns:
        st.subheader("Trend-Based Forecasting")
        
        selected_metric = st.selectbox(
            "Select metric for forecasting",
            options=numerical_cols
        )
        
        if selected_metric:
            try:
                # Simple trend-based prediction
                data_to_analyze['Timestamp'] = pd.to_datetime(data_to_analyze['Timestamp'])
                daily_data = data_to_analyze.groupby(data_to_analyze['Timestamp'].dt.date)[selected_metric].mean()
                
                if len(daily_data) >= 3:
                    # Calculate simple trend
                    x = np.arange(len(daily_data))
                    y = daily_data.values
                    
                    # Linear regression for trend
                    coeffs = np.polyfit(x, y, 1)
                    
                    # Generate future predictions (next 7 days)
                    future_x = np.arange(len(daily_data), len(daily_data) + 7)
                    future_y = np.polyval(coeffs, future_x)
                    
                    # Create visualization
                    fig = visualizer.create_predictive_chart(
                        daily_data.values.tolist(),
                        future_y.tolist(),
                        selected_metric
                    )
                    
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show trend analysis
                        trend_direction = "increasing" if coeffs[0] > 0 else "decreasing"
                        st.metric(
                            f"{selected_metric} Trend",
                            trend_direction.title(),
                            delta=f"{coeffs[0]:.3f} per day"
                        )
                
            except Exception as e:
                st.error(f"Error creating forecast: {str(e)}")

with tab4:
    st.header("Key Insights & Recommendations")
    
    # AI-generated insights
    st.subheader("🤖 AI-Generated Insights")
    
    if st.button("🧠 Generate Comprehensive Insights", type="primary"):
        with st.spinner("Analyzing data and generating insights..."):
            try:
                # Create comprehensive data summary
                data_processor = DataProcessor()
                summary = data_processor.get_data_summary(data_to_analyze)
                
                # Generate comprehensive insights
                insights = st.session_state.groq_client.analyze_data(
                    str(summary), 
                    "comprehensive business insights and actionable recommendations"
                )
                
                if insights:
                    st.session_state.dashboard_insights = insights
                    st.markdown(insights)
                else:
                    st.error("Failed to generate insights.")
                    
            except Exception as e:
                st.error(f"Error generating insights: {str(e)}")
    
    # Display previous insights
    if st.session_state.get('dashboard_insights'):
        st.subheader("Form Previous Insights")
        st.markdown(st.session_state.dashboard_insights)
    
    # Key statistics and patterns
    st.subheader("Statistical Highlights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Data Highlights:**")
        
        # Response rate over time
        if 'Timestamp' in data_to_analyze.columns:
            try:
                data_to_analyze['Timestamp'] = pd.to_datetime(data_to_analyze['Timestamp'])
                date_range = (data_to_analyze['Timestamp'].max() - data_to_analyze['Timestamp'].min()).days
                daily_avg = len(data_to_analyze) / max(date_range, 1)
                st.metric("Daily Response Rate", f"{daily_avg:.1f} responses/day")
            except:
                pass
        
        # Most common responses
        categorical_cols = data_to_analyze.select_dtypes(include=['object']).columns
        categorical_cols = [col for col in categorical_cols if col not in ['Timestamp', 'Response_ID']]
        
        if categorical_cols:
            for col in categorical_cols[:2]:
                most_common = data_to_analyze[col].mode().iloc[0] if not data_to_analyze[col].mode().empty else "N/A"
                st.metric(f"Most Common {col}", most_common)
    
    with col2:
        st.markdown("**Performance Metrics:**")
        
        # Data completeness by column
        completeness = ((data_to_analyze.notnull().sum() / len(data_to_analyze)) * 100).round(1)
        avg_completeness = completeness.mean()
        st.metric("Average Completeness", f"{avg_completeness:.1f}%")
        
        # Response consistency (for numerical columns)
        numerical_cols = data_to_analyze.select_dtypes(include=[np.number]).columns
        numerical_cols = [col for col in numerical_cols if col not in ['Response_ID']]
        
        if len(numerical_cols) > 0:
            avg_cv = np.mean([data_to_analyze[col].std() / data_to_analyze[col].mean() for col in numerical_cols if data_to_analyze[col].mean() != 0])
            consistency = max(0, 100 - (avg_cv * 100))
            st.metric("Response Consistency", f"{consistency:.1f}%")

# Action items and next steps
st.header("Recommended Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Data Collection:**")
    if len(data_to_analyze) < 100:
        st.warning("Consider collecting more responses for better insights")
        if st.button("Collect More Data"):
            st.switch_page("pages/3_Data_Collection.py")
    else:
        st.success("Good sample size for analysis")

with col2:
    st.markdown("**Analysis Depth:**")
    if not st.session_state.get('analysis_results'):
        st.info("Perform detailed analysis for deeper insights")
        if st.button("Deep Analysis"):
            st.switch_page("pages/5_Analysis.py")
    else:
        st.success("Analysis completed")

with col3:
    st.markdown("**Expert Consultation:**")
    st.info("Ask specific questions about your data")
    if st.button("Chat with AI"):
        st.switch_page("pages/7_Chat.py")

# Export dashboard
st.header("Download Export Dashboard")

col1, col2 = st.columns(2)

with col1:
    if st.button("Download Dashboard Summary", use_container_width=True):
        try:
            dashboard_summary = f"""
# Dashboard Summary Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Key Metrics
- Total Records: {data_to_analyze.shape[0]}
- Data Quality: {data_quality:.1f}%
- Variables: {data_to_analyze.shape[1]}

## Insights
{st.session_state.get('dashboard_insights', 'No insights generated yet.')}

## Predictions
{st.session_state.get('predictions', 'No predictions generated yet.')}
            """
            
            st.download_button(
                label="Download Download Summary",
                data=dashboard_summary,
                file_name=f"dashboard_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
            
        except Exception as e:
            st.error(f"Error creating dashboard summary: {str(e)}")

with col2:
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.rerun()

# Navigation
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("Back to Analysis", use_container_width=True):
        st.switch_page("pages/5_Analysis.py")

with col2:
    if st.button("Open Chat", use_container_width=True):
        st.switch_page("pages/7_Chat.py")
