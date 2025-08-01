import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import streamlit as st

class DataProcessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.processing_log = []

    def clean_data(self, df, options=None):
        """Clean and preprocess the data based on selected options"""
        if df is None or df.empty:
            return df
        
        cleaned_df = df.copy()
        self.processing_log = []
        
        if not options:
            options = {
                'remove_missing': True,
                'remove_outliers': True,
                'normalize_numerical': False,
                'encode_categorical': True
            }
        
        # Remove missing values
        if options.get('remove_missing', True):
            initial_rows = len(cleaned_df)
            cleaned_df = cleaned_df.dropna()
            removed_rows = initial_rows - len(cleaned_df)
            if removed_rows > 0:
                self.processing_log.append(f"Removed {removed_rows} rows with missing values")
        
        # Handle outliers for numerical columns
        if options.get('remove_outliers', True):
            numerical_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            for col in numerical_cols:
                if col in ['Timestamp', 'Response_ID']:
                    continue
                    
                Q1 = cleaned_df[col].quantile(0.25)
                Q3 = cleaned_df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                initial_count = len(cleaned_df)
                cleaned_df = cleaned_df[(cleaned_df[col] >= lower_bound) & (cleaned_df[col] <= upper_bound)]
                removed_outliers = initial_count - len(cleaned_df)
                
                if removed_outliers > 0:
                    self.processing_log.append(f"Removed {removed_outliers} outliers from column '{col}'")
        
        # Normalize numerical columns
        if options.get('normalize_numerical', False):
            numerical_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            numerical_cols = [col for col in numerical_cols if col not in ['Timestamp', 'Response_ID']]
            
            if len(numerical_cols) > 0:
                cleaned_df[numerical_cols] = self.scaler.fit_transform(cleaned_df[numerical_cols])
                self.processing_log.append(f"Normalized numerical columns: {', '.join(numerical_cols)}")
        
        # Encode categorical variables
        if options.get('encode_categorical', True):
            categorical_cols = cleaned_df.select_dtypes(include=['object']).columns
            categorical_cols = [col for col in categorical_cols if col not in ['Timestamp', 'Response_ID']]
            
            for col in categorical_cols:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                
                cleaned_df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(cleaned_df[col].astype(str))
                self.processing_log.append(f"Encoded categorical column '{col}'")
        
        # Convert date columns
        date_cols = [col for col in cleaned_df.columns if 'date' in col.lower() or 'timestamp' in col.lower()]
        for col in date_cols:
            try:
                cleaned_df[col] = pd.to_datetime(cleaned_df[col])
                self.processing_log.append(f"Converted '{col}' to datetime")
            except:
                pass
        
        return cleaned_df

    def get_data_summary(self, df):
        """Generate a comprehensive data summary"""
        if df is None or df.empty:
            return "No data available for summary."
        
        summary = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'numerical_summary': {},
            'categorical_summary': {}
        }
        
        # Numerical columns summary
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            summary['numerical_summary'][col] = {
                'mean': df[col].mean(),
                'median': df[col].median(),
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max(),
                'unique_values': df[col].nunique()
            }
        
        # Categorical columns summary
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            summary['categorical_summary'][col] = {
                'unique_values': df[col].nunique(),
                'most_common': df[col].mode().iloc[0] if not df[col].mode().empty else None,
                'value_counts': df[col].value_counts().head().to_dict()
            }
        
        return summary

    def balance_data(self, df, target_column=None):
        """Balance the dataset if target column is specified"""
        if not target_column or target_column not in df.columns:
            return df
        
        try:
            from imblearn.over_sampling import RandomOverSampler
            
            # Separate features and target
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            # Apply random oversampling
            ros = RandomOverSampler(random_state=42)
            X_resampled, y_resampled = ros.fit_resample(X, y)
            
            # Combine back into DataFrame
            balanced_df = pd.concat([X_resampled, y_resampled], axis=1)
            
            self.processing_log.append(f"Balanced dataset using RandomOverSampler on '{target_column}'")
            return balanced_df
            
        except ImportError:
            st.warning("imbalanced-learn package not available. Skipping data balancing.")
            return df
        except Exception as e:
            st.error(f"Error balancing data: {str(e)}")
            return df

    def detect_data_types(self, df):
        """Automatically detect and suggest data types for columns"""
        if df is None or df.empty:
            return {}
        
        suggestions = {}
        
        for col in df.columns:
            if col in ['Timestamp', 'Response_ID']:
                continue
            
            sample_values = df[col].dropna().head(10)
            
            # Check if it's numerical
            try:
                pd.to_numeric(sample_values)
                suggestions[col] = 'numerical'
                continue
            except:
                pass
            
            # Check if it's date
            try:
                pd.to_datetime(sample_values)
                suggestions[col] = 'date'
                continue
            except:
                pass
            
            # Check if it's boolean
            unique_values = set(str(v).lower() for v in sample_values.unique())
            if unique_values.issubset({'true', 'false', '1', '0', 'yes', 'no'}):
                suggestions[col] = 'boolean'
                continue
            
            # Default to categorical
            suggestions[col] = 'categorical'
        
        return suggestions

    def get_processing_log(self):
        """Return the processing log"""
        return self.processing_log

    def export_processed_data(self, df, format='csv'):
        """Export processed data in specified format"""
        if df is None or df.empty:
            return None
        
        if format == 'csv':
            return df.to_csv(index=False)
        elif format == 'json':
            return df.to_json(orient='records', indent=2)
        else:
            return None
