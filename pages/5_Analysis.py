import streamlit as st
from utils.visualizer import Visualizer
from utils.data_processor import DataProcessor
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats

st.set_page_config(
    page_title="Analysis - BI StoryTeller",

    layout="wide"
)

st.title("Comprehensive Data Analysis")
st.markdown("Explore your data through statistical analysis and interactive visualizations.")

# Check prerequisites
data_to_analyze = st.session_state.get('processed_data')
if data_to_analyze is None or data_to_analyze.empty:
    data_to_analyze = st.session_state.get('raw_data')

if data_to_analyze is None or data_to_analyze.empty:
    st.warning("No data available for analysis. Please collect and preprocess data first.")
    if st.button("Go to Data Collection"):
        st.switch_page("pages/3_Data_Collection.py")
    st.stop()

# Initialize visualizer
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = Visualizer()

visualizer = st.session_state.visualizer

# Data overview
st.header("Data Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Records", data_to_analyze.shape[0])

with col2:
    st.metric("Variables", data_to_analyze.shape[1])

with col3:
    numerical_cols = data_to_analyze.select_dtypes(include=[np.number]).columns
    st.metric("Numerical Variables", len(numerical_cols))

with col4:
    categorical_cols = data_to_analyze.select_dtypes(include=['object']).columns
    st.metric("Categorical Variables", len(categorical_cols))

# Analysis tabs
tab1, tab2, tab3, tab4 = st.tabs(["Descriptive Statistics", "Visualizations", "Correlation Analysis", "AI Insights"])

with tab1:
    st.header("Descriptive Statistics")
    
    # Numerical statistics
    numerical_cols = data_to_analyze.select_dtypes(include=[np.number]).columns
    numerical_cols = [col for col in numerical_cols if col not in ['Response_ID']]
    
    if len(numerical_cols) > 0:
        st.subheader("Numerical Variables")
        
        for col in numerical_cols:
            with st.expander(f"{col}", expanded=False):
                col_data = data_to_analyze[col].dropna()
                
                if len(col_data) > 0:
                    # Statistics
                    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                    
                    with stats_col1:
                        st.metric("Mean", f"{col_data.mean():.2f}")
                        st.metric("Std Dev", f"{col_data.std():.2f}")
                    
                    with stats_col2:
                        st.metric("Median", f"{col_data.median():.2f}")
                        st.metric("IQR", f"{col_data.quantile(0.75) - col_data.quantile(0.25):.2f}")
                    
                    with stats_col3:
                        st.metric("Min", f"{col_data.min():.2f}")
                        st.metric("Max", f"{col_data.max():.2f}")
                    
                    with stats_col4:
                        st.metric("Skewness", f"{stats.skew(col_data):.2f}")
                        st.metric("Kurtosis", f"{stats.kurtosis(col_data):.2f}")
                    
                    # Distribution plot
                    fig = visualizer.create_distribution_plot(data_to_analyze, col)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
    
    # Categorical statistics
    categorical_cols = data_to_analyze.select_dtypes(include=['object']).columns
    categorical_cols = [col for col in categorical_cols if col not in ['Timestamp', 'Response_ID']]
    
    if len(categorical_cols) > 0:
        st.subheader("Categorical Variables")
        
        for col in categorical_cols:
            with st.expander(f"Form {col}", expanded=False):
                col_data = data_to_analyze[col].dropna()
                
                if len(col_data) > 0:
                    # Value counts
                    value_counts = col_data.value_counts()
                    
                    stats_col1, stats_col2 = st.columns(2)
                    
                    with stats_col1:
                        st.metric("Unique Values", col_data.nunique())
                        most_common = value_counts.index[0] if len(value_counts) > 0 else "N/A"
                        # Convert date objects to string for display
                        if hasattr(most_common, 'strftime'):
                            most_common = most_common.strftime('%Y-%m-%d')
                        st.metric("Most Common", str(most_common))
                    
                    with stats_col2:
                        st.metric("Mode Frequency", value_counts.iloc[0] if len(value_counts) > 0 else 0)
                        st.metric("Mode Percentage", f"{value_counts.iloc[0]/len(col_data)*100:.1f}%" if len(value_counts) > 0 else "0%")
                    
                    # Value counts table
                    st.markdown("**Value Distribution:**")
                    # Convert any date objects to strings for display
                    display_values = []
                    for val in value_counts.index:
                        if hasattr(val, 'strftime'):
                            display_values.append(val.strftime('%Y-%m-%d'))
                        else:
                            display_values.append(str(val))
                    
                    value_counts_df = pd.DataFrame({
                        'Value': display_values,
                        'Count': value_counts.values,
                        'Percentage': (value_counts.values / len(col_data) * 100).round(2)
                    })
                    st.dataframe(value_counts_df, use_container_width=True)
                    
                    # Distribution plot
                    fig = visualizer.create_distribution_plot(data_to_analyze, col)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True, key=f"dist_plot_tab1_{col}")

with tab2:
    st.header("Interactive Visualizations")
    
    viz_type = st.selectbox(
        "Select Visualization Type",
        options=[
            "Distribution Plot",
            "Scatter Plot",
            "Box Plot",
            "Time Series",
            "Correlation Heatmap"
        ]
    )
    
    if viz_type == "Distribution Plot":
        st.subheader("Distribution Analysis")
        
        column = st.selectbox(
            "Select column to analyze",
            options=data_to_analyze.columns.tolist()
        )
        
        if column:
            fig = visualizer.create_distribution_plot(data_to_analyze, column)
            if fig:
                st.plotly_chart(fig, use_container_width=True, key=f"dist_plot_tab2_{column}")
            
            # Additional statistics
            if data_to_analyze[column].dtype in [np.number]:
                col_data = data_to_analyze[column].dropna()
                st.markdown("**Statistical Summary:**")
                st.write(col_data.describe())
    
    elif viz_type == "Scatter Plot":
        st.subheader("Scatter Plot Analysis")
        
        numerical_cols = data_to_analyze.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numerical_cols) >= 2:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                x_col = st.selectbox("X-axis", numerical_cols)
            
            with col2:
                y_col = st.selectbox("Y-axis", [c for c in numerical_cols if c != x_col])
            
            with col3:
                color_col = st.selectbox(
                    "Color by (optional)",
                    options=[None] + data_to_analyze.columns.tolist(),
                    index=0
                )
            
            if x_col and y_col:
                fig = visualizer.create_scatter_plot(data_to_analyze, x_col, y_col, color_col)
                if fig:
                    st.plotly_chart(fig, use_container_width=True, key=f"scatter_plot_{x_col}_{y_col}")
                
                # Correlation coefficient
                if x_col in data_to_analyze.columns and y_col in data_to_analyze.columns:
                    corr = data_to_analyze[x_col].corr(data_to_analyze[y_col])
                    st.metric("Correlation Coefficient", f"{corr:.3f}")
        else:
            st.info("Need at least 2 numerical columns for scatter plot.")
    
    elif viz_type == "Box Plot":
        st.subheader("Box Plot Analysis")
        
        numerical_cols = data_to_analyze.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = data_to_analyze.select_dtypes(include=['object']).columns.tolist()
        
        if numerical_cols and categorical_cols:
            col1, col2 = st.columns(2)
            
            with col1:
                y_col = st.selectbox("Numerical variable (Y-axis)", numerical_cols)
            
            with col2:
                x_col = st.selectbox("Categorical variable (X-axis)", categorical_cols)
            
            if x_col and y_col:
                fig = visualizer.create_box_plot(data_to_analyze, x_col, y_col)
                if fig:
                    st.plotly_chart(fig, use_container_width=True, key=f"box_plot_{x_col}_{y_col}")
        else:
            st.info("Need both numerical and categorical columns for box plot.")
    
    elif viz_type == "Time Series":
        st.subheader("Time Series Analysis")
        
        date_cols = [col for col in data_to_analyze.columns if 'date' in col.lower() or 'timestamp' in col.lower()]
        numerical_cols = data_to_analyze.select_dtypes(include=[np.number]).columns.tolist()
        
        if date_cols and numerical_cols:
            col1, col2 = st.columns(2)
            
            with col1:
                date_col = st.selectbox("Date column", date_cols)
            
            with col2:
                value_col = st.selectbox("Value column", numerical_cols)
            
            if date_col and value_col:
                fig = visualizer.create_time_series_plot(data_to_analyze, date_col, value_col)
                if fig:
                    st.plotly_chart(fig, use_container_width=True, key=f"timeseries_{date_col}_{value_col}")
        else:
            st.info("Need date and numerical columns for time series.")
    
    elif viz_type == "Correlation Heatmap":
        st.subheader("Correlation Analysis")
        
        fig = visualizer.create_correlation_heatmap(data_to_analyze)
        if fig:
            st.plotly_chart(fig, use_container_width=True, key="correlation_heatmap_viz")
        else:
            st.info("Need at least 2 numerical columns for correlation analysis.")

with tab3:
    st.header("Correlation Analysis")
    
    numerical_cols = data_to_analyze.select_dtypes(include=[np.number]).columns
    numerical_cols = [col for col in numerical_cols if col not in ['Response_ID']]
    
    if len(numerical_cols) >= 2:
        # Correlation matrix
        corr_matrix = data_to_analyze[numerical_cols].corr()
        
        st.subheader("Correlation Matrix")
        fig = visualizer.create_correlation_heatmap(data_to_analyze)
        if fig:
            st.plotly_chart(fig, use_container_width=True, key="correlation_heatmap_tab3")
        
        # Strong correlations
        st.subheader("Notable Correlations")
        
        # Find strong correlations (> 0.7 or < -0.7)
        strong_corrs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    strong_corrs.append({
                        'Variable 1': corr_matrix.columns[i],
                        'Variable 2': corr_matrix.columns[j],
                        'Correlation': corr_val,
                        'Strength': 'Strong Positive' if corr_val > 0.7 else 'Strong Negative'
                    })
        
        if strong_corrs:
            strong_corr_df = pd.DataFrame(strong_corrs)
            st.dataframe(strong_corr_df, use_container_width=True)
        else:
            st.info("No strong correlations (|r| > 0.7) found between variables.")
        
        # Correlation insights
        st.subheader("Correlation Insights")
        for i, col1 in enumerate(numerical_cols):
            for j, col2 in enumerate(numerical_cols[i+1:], i+1):
                corr_val = corr_matrix.loc[col1, col2]
                if abs(corr_val) > 0.5:
                    strength = "strong" if abs(corr_val) > 0.7 else "moderate"
                    direction = "positive" if corr_val > 0 else "negative"
                    st.write(f"• **{col1}** and **{col2}** show a {strength} {direction} correlation (r = {corr_val:.3f})")
    
    else:
        st.info("Need at least 2 numerical variables for correlation analysis.")

with tab4:
    st.header("AI-Generated Insights")
    
    if st.button("🤖 Generate AI Insights", type="primary"):
        with st.spinner("Analyzing data and generating insights..."):
            try:
                # Create data summary
                data_processor = DataProcessor()
                summary = data_processor.get_data_summary(data_to_analyze)
                
                # Generate insights using Groq
                insights = st.session_state.groq_client.analyze_data(str(summary), "comprehensive")
                
                if insights:
                    st.session_state.analysis_results['ai_insights'] = insights
                    st.markdown(insights)
                else:
                    st.error("Failed to generate AI insights.")
                    
            except Exception as e:
                st.error(f"Error generating insights: {str(e)}")
    
    # Display previously generated insights
    if st.session_state.get('analysis_results', {}).get('ai_insights'):
        st.subheader("Previous Insights")
        st.markdown(st.session_state.analysis_results['ai_insights'])
    
    # Sentiment analysis for text columns
    text_columns = data_to_analyze.select_dtypes(include=['object']).columns
    text_columns = [col for col in text_columns if col not in ['Timestamp', 'Response_ID']]
    
    if text_columns:
        st.subheader("Sentiment Analysis")
        
        selected_text_cols = st.multiselect(
            "Select text columns for sentiment analysis",
            options=text_columns,
            default=text_columns[:2] if len(text_columns) >= 2 else text_columns
        )
        
        if selected_text_cols and st.button("Analyze Sentiment"):
            with st.spinner("Performing sentiment analysis..."):
                try:
                    fig_dist, fig_scatter = visualizer.create_sentiment_analysis(data_to_analyze, selected_text_cols)
                    
                    if fig_dist and fig_scatter:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.plotly_chart(fig_dist, use_container_width=True)
                        
                        with col2:
                            st.plotly_chart(fig_scatter, use_container_width=True)
                    else:
                        st.warning("Could not perform sentiment analysis on selected columns.")
                        
                except Exception as e:
                    st.error(f"Error in sentiment analysis: {str(e)}")

# Export analysis results
st.header("Download Export Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Export Summary Report", use_container_width=True):
        try:
            # Create summary report
            report = f"""
# Data Analysis Report

## Dataset Overview
- Total Records: {data_to_analyze.shape[0]}
- Total Variables: {data_to_analyze.shape[1]}
- Numerical Variables: {len(data_to_analyze.select_dtypes(include=[np.number]).columns)}
- Categorical Variables: {len(data_to_analyze.select_dtypes(include=['object']).columns)}

## Data Quality
- Missing Values: {data_to_analyze.isnull().sum().sum()}
- Completeness: {(1 - data_to_analyze.isnull().sum().sum() / (data_to_analyze.shape[0] * data_to_analyze.shape[1])) * 100:.1f}%

## Key Statistics
{data_to_analyze.describe().to_string()}

## AI Insights
{st.session_state.get('analysis_results', {}).get('ai_insights', 'No AI insights generated yet.')}
            """
            
            st.download_button(
                label="Download Download Report",
                data=report,
                file_name="analysis_report.md",
                mime="text/markdown"
            )
            
        except Exception as e:
            st.error(f"Error creating report: {str(e)}")

with col2:
    if st.button("Save Analysis State", use_container_width=True):
        # Save current analysis state
        st.session_state.analysis_complete = True
        st.success("Analysis state saved! You can now proceed to the dashboard.")

with col3:
    if st.button("View Dashboard", use_container_width=True):
        st.switch_page("pages/6_Dashboard.py")

# Navigation
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("Back to Preprocessing", use_container_width=True):
        st.switch_page("pages/4_Data_Preprocessing.py")

with col2:
    if st.button("Next: Dashboard", use_container_width=True):
        st.switch_page("pages/6_Dashboard.py")
