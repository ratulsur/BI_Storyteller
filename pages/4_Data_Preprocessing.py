import streamlit as st
from utils.data_processor import DataProcessor
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Data Preprocessing - BI StoryTeller",

    layout="wide"
)

st.title("Data Preprocessing")
st.markdown("Clean and prepare your data for comprehensive analysis.")

# Check prerequisites
raw_data = st.session_state.get('raw_data')
if raw_data is None or raw_data.empty:
    st.warning("No data available for preprocessing. Please collect data first.")
    if st.button("Go to Data Collection"):
        st.switch_page("pages/3_Data_Collection.py")
    st.stop()

# Initialize data processor
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor()

# Display raw data info
st.header("Raw Data Overview")
raw_data = st.session_state.raw_data

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Rows", raw_data.shape[0])

with col2:
    st.metric("Total Columns", raw_data.shape[1])

with col3:
    missing_count = raw_data.isnull().sum().sum()
    st.metric("Missing Values", missing_count)

with col4:
    duplicate_count = raw_data.duplicated().sum()
    st.metric("Duplicate Rows", duplicate_count)

# Data preview
st.subheader("Form Data Preview")
st.dataframe(raw_data.head(10), use_container_width=True)

# Data quality assessment
st.header("Data Quality Assessment")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Missing Values by Column")
    missing_by_column = raw_data.isnull().sum()
    missing_df = pd.DataFrame({
        'Column': missing_by_column.index,
        'Missing Count': missing_by_column.values,
        'Missing %': (missing_by_column.values / len(raw_data) * 100).round(2)
    })
    missing_df = missing_df[missing_df['Missing Count'] > 0]
    
    if not missing_df.empty:
        st.dataframe(missing_df, use_container_width=True)
    else:
        st.success("No missing values found!")

with col2:
    st.subheader("Data Types")
    dtype_df = pd.DataFrame({
        'Column': raw_data.dtypes.index,
        'Data Type': raw_data.dtypes.values.astype(str),
        'Unique Values': [raw_data[col].nunique() for col in raw_data.columns]
    })
    st.dataframe(dtype_df, use_container_width=True)

# Preprocessing options
st.header("Preprocessing Options")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Data Cleaning")
    
    remove_missing = st.checkbox(
        "Remove rows with missing values",
        value=True,
        help="Remove all rows that contain any missing values"
    )
    
    remove_duplicates = st.checkbox(
        "Remove duplicate rows",
        value=True,
        help="Remove rows that are exact duplicates"
    )
    
    remove_outliers = st.checkbox(
        "Remove statistical outliers",
        value=True,
        help="Remove outliers using IQR method for numerical columns"
    )

with col2:
    st.subheader("Data Transformation")
    
    normalize_numerical = st.checkbox(
        "Normalize numerical columns",
        value=False,
        help="Scale numerical values to have mean=0 and std=1"
    )
    
    encode_categorical = st.checkbox(
        "Encode categorical variables",
        value=True,
        help="Convert categorical text to numerical values"
    )
    
    convert_dates = st.checkbox(
        "Convert date columns",
        value=True,
        help="Automatically detect and convert date columns"
    )

# Advanced options
with st.expander("Advanced Options"):
    st.subheader("Data Balancing")
    
    balance_data = st.checkbox(
        "Balance dataset",
        value=False,
        help="Balance the dataset if you have a target variable"
    )
    
    if balance_data:
        target_column = st.selectbox(
            "Select target column for balancing",
            options=[None] + list(raw_data.columns),
            help="Choose the column that represents your target variable"
        )
    else:
        target_column = None
    
    st.subheader("Custom Preprocessing")
    custom_code = st.text_area(
        "Custom preprocessing code (Python/Pandas)",
        placeholder="# Example: df['new_column'] = df['old_column'].apply(lambda x: x.upper())",
        help="Advanced users can add custom preprocessing steps"
    )

# Apply preprocessing
st.header("Apply Preprocessing")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("Clean Data", type="primary", use_container_width=True):
        with st.spinner("Processing data..."):
            try:
                # Prepare options
                options = {
                    'remove_missing': remove_missing,
                    'remove_outliers': remove_outliers,
                    'normalize_numerical': normalize_numerical,
                    'encode_categorical': encode_categorical,
                    'convert_dates': convert_dates
                }
                
                # Start with raw data
                processed_data = raw_data.copy()
                
                # Remove duplicates if selected
                if remove_duplicates:
                    initial_rows = len(processed_data)
                    processed_data = processed_data.drop_duplicates()
                    removed_duplicates = initial_rows - len(processed_data)
                    if removed_duplicates > 0:
                        st.session_state.data_processor.processing_log.append(
                            f"Removed {removed_duplicates} duplicate rows"
                        )
                
                # Apply main cleaning
                processed_data = st.session_state.data_processor.clean_data(processed_data, options)
                
                # Apply custom code if provided
                if custom_code.strip():
                    try:
                        # Create a safe environment for custom code
                        local_vars = {'df': processed_data, 'pd': pd, 'np': np}
                        exec(custom_code, {"__builtins__": {}}, local_vars)
                        processed_data = local_vars['df']
                        st.session_state.data_processor.processing_log.append("Applied custom preprocessing code")
                    except Exception as e:
                        st.error(f"Error in custom code: {str(e)}")
                
                # Balance data if requested
                if balance_data and target_column:
                    processed_data = st.session_state.data_processor.balance_data(processed_data, target_column)
                
                # Save processed data
                st.session_state.processed_data = processed_data
                
                st.success(f"Data preprocessing completed! Processed {len(processed_data)} rows.")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error during preprocessing: {str(e)}")

with col2:
    if st.button("👀 Preview Changes", use_container_width=True):
        with st.spinner("Generating preview..."):
            try:
                # Create a sample for preview
                sample_size = min(100, len(raw_data))
                sample_data = raw_data.head(sample_size).copy()
                
                # Apply same preprocessing to sample
                options = {
                    'remove_missing': remove_missing,
                    'remove_outliers': remove_outliers,
                    'normalize_numerical': normalize_numerical,
                    'encode_categorical': encode_categorical
                }
                
                preview_data = st.session_state.data_processor.clean_data(sample_data, options)
                
                st.subheader("Preview of Changes")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("**Before Preprocessing:**")
                    st.dataframe(sample_data.head(), use_container_width=True)
                    st.caption(f"Shape: {sample_data.shape}")
                
                with col_b:
                    st.markdown("**After Preprocessing:**")
                    st.dataframe(preview_data.head(), use_container_width=True)
                    st.caption(f"Shape: {preview_data.shape}")
                
            except Exception as e:
                st.error(f"Error generating preview: {str(e)}")

with col3:
    if st.button("🔄 Reset Data", use_container_width=True):
        st.session_state.processed_data = None
        st.session_state.data_processor = DataProcessor()
        st.success("Data reset to original state.")
        st.rerun()

# Display processed data if available
if st.session_state.get('processed_data') is not None:
    processed_data = st.session_state.processed_data
    
    st.header("Approve Processed Data")
    
    # Comparison metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        original_rows = raw_data.shape[0]
        processed_rows = processed_data.shape[0]
        st.metric(
            "Rows",
            processed_rows,
            delta=int(processed_rows - original_rows)
        )
    
    with col2:
        original_cols = raw_data.shape[1]
        processed_cols = processed_data.shape[1]
        st.metric(
            "Columns",
            processed_cols,
            delta=int(processed_cols - original_cols)
        )
    
    with col3:
        original_missing = raw_data.isnull().sum().sum()
        processed_missing = processed_data.isnull().sum().sum()
        st.metric(
            "Missing Values",
            int(processed_missing),
            delta=int(processed_missing - original_missing)
        )
    
    with col4:
        quality_score = (1 - processed_data.isnull().sum().sum() / (processed_data.shape[0] * processed_data.shape[1])) * 100
        st.metric("Data Quality", f"{quality_score:.1f}%")
    
    # Processing log
    st.subheader("Form Processing Log")
    processing_log = st.session_state.data_processor.get_processing_log()
    if processing_log:
        for log_entry in processing_log:
            st.success(f"Approve {log_entry}")
    else:
        st.info("No preprocessing steps applied yet.")
    
    # Data preview
    st.subheader("Processed Data Preview")
    st.dataframe(processed_data.head(10), use_container_width=True)
    
    # Download processed data
    st.subheader("Download Download Processed Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = processed_data.to_csv(index=False)
        st.download_button(
            label="Download Download as CSV",
            data=csv_data,
            file_name="processed_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        json_data = processed_data.to_json(orient='records', indent=2)
        st.download_button(
            label="Download Download as JSON",
            data=json_data,
            file_name="processed_data.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Next steps
    st.header("Ready for Analysis")
    st.success("Your data is now clean and ready for comprehensive analysis!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Analysis", type="primary", use_container_width=True):
            st.switch_page("pages/5_Analysis.py")
    
    with col2:
        if st.button("View Dashboard", use_container_width=True):
            st.switch_page("pages/6_Dashboard.py")

# Navigation
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("Back to Data Collection", use_container_width=True):
        st.switch_page("pages/3_Data_Collection.py")

with col2:
    has_processed_data = st.session_state.get('processed_data') is not None
    if st.button("Next: Analysis", use_container_width=True, disabled=not has_processed_data):
        st.switch_page("pages/5_Analysis.py")
