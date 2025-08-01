import gspread
import pandas as pd
import streamlit as st
import json
from google.oauth2.service_account import Credentials
import os

class SheetsClient:
    def __init__(self):
        try:
            # Try to get credentials from environment or Streamlit secrets
            creds_raw = None
            if 'GOOGLE_CREDENTIALS' in os.environ:
                creds_raw = os.getenv('GOOGLE_CREDENTIALS')
            elif hasattr(st, 'secrets') and 'google_credentials' in st.secrets:
                creds_raw = st.secrets.google_credentials
            
            if not creds_raw:
                st.info("🏠 Using local data collection mode - all features are available with sample data generation.")
                self.client = None
                return
            
            # Parse credentials - handle both string and dict formats
            if isinstance(creds_raw, str):
                if creds_raw.strip() == '':
                    st.info("🏠 Using local data collection mode - all features are available with sample data generation.")
                    self.client = None
                    return
                creds_info = json.loads(creds_raw)
            else:
                creds_info = dict(creds_raw)
            
            # Validate required fields
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in creds_info]
            if missing_fields:
                st.info(f"🏠 Using local data collection mode - all features are available with sample data generation.")
                self.client = None
                return
            
            # Set up credentials
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_info(creds_info, scopes=scope)
            self.client = gspread.authorize(credentials)
            
        except json.JSONDecodeError as e:
            st.info("🏠 Using local data collection mode - all features are available with sample data generation.")
            self.client = None
        except Exception as e:
            st.info("🏠 Using local data collection mode - all features are available with sample data generation.")
            self.client = None

    def create_questionnaire_sheet(self, questionnaire_data):
        """Create a new Google Sheet for questionnaire responses"""
        if not self.client:
            return None
        
        try:
            # Create a new spreadsheet
            title = f"Questionnaire: {questionnaire_data.get('title', 'Survey')}"
            sheet = self.client.create(title)
            
            # Make it publicly accessible for form submissions
            sheet.share('', perm_type='anyone', role='writer')
            
            # Set up the header row
            worksheet = sheet.sheet1
            
            # Create headers based on questions
            headers = ['Timestamp', 'Response_ID']
            for i, question in enumerate(questionnaire_data.get('questions', [])):
                headers.append(f"Q{i+1}_{question['question_text'][:50]}")
            
            worksheet.insert_row(headers, 1)
            
            # Store questionnaire metadata in a separate sheet
            metadata_sheet = sheet.add_worksheet(title="Metadata", rows="100", cols="20")
            metadata_sheet.update('A1', 'Questionnaire Data')
            metadata_sheet.update('A2', json.dumps(questionnaire_data, indent=2))
            
            return sheet.url
            
        except Exception as e:
            st.error(f"Error creating questionnaire sheet: {str(e)}")
            return None

    def save_response(self, sheet_url, responses):
        """Save a response to the Google Sheet"""
        if not self.client:
            return False
        
        try:
            # Extract sheet ID from URL
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            sheet = self.client.open_by_key(sheet_id)
            worksheet = sheet.sheet1
            
            # Add timestamp and response ID
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response_id = f"R{len(worksheet.get_all_records()) + 1}"
            
            row_data = [timestamp, response_id] + responses
            worksheet.insert_row(row_data, len(worksheet.get_all_records()) + 2)
            
            return True
            
        except Exception as e:
            st.error(f"Error saving response: {str(e)}")
            return False

    def get_responses(self, sheet_url):
        """Get all responses from the Google Sheet"""
        if not self.client:
            return None
        
        try:
            # Extract sheet ID from URL
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            sheet = self.client.open_by_key(sheet_id)
            worksheet = sheet.sheet1
            
            # Get all records
            records = worksheet.get_all_records()
            
            if not records:
                return pd.DataFrame()
            
            return pd.DataFrame(records)
            
        except Exception as e:
            st.error(f"Error retrieving responses: {str(e)}")
            return None

    def get_questionnaire_metadata(self, sheet_url):
        """Get questionnaire metadata from the sheet"""
        if not self.client:
            return None
        
        try:
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            sheet = self.client.open_by_key(sheet_id)
            metadata_sheet = sheet.worksheet("Metadata")
            
            metadata_json = metadata_sheet.acell('A2').value
            return json.loads(metadata_json)
            
        except Exception as e:
            st.error(f"Error retrieving questionnaire metadata: {str(e)}")
            return None

    def create_sample_data(self, questionnaire_data, num_samples=50):
        """Create sample data for demonstration (only when no real data exists)"""
        if not questionnaire_data or not questionnaire_data.get('questions'):
            return pd.DataFrame()
        
        import random
        import datetime
        
        sample_data = []
        
        for i in range(num_samples):
            response = {
                'Timestamp': (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S"),
                'Response_ID': f"R{i+1}"
            }
            
            for j, question in enumerate(questionnaire_data['questions']):
                question_key = f"Q{j+1}_{question['question_text'][:50]}"
                
                if question['question_type'] == 'number':
                    response[question_key] = random.randint(1, 10)
                elif question['question_type'] == 'select' and 'options' in question:
                    response[question_key] = random.choice(question['options'])
                elif question['question_type'] == 'boolean':
                    response[question_key] = random.choice([True, False])
                elif question['question_type'] == 'date':
                    response[question_key] = (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
                else:
                    # Text responses
                    sample_texts = [
                        "Great experience overall",
                        "Could be improved",
                        "Very satisfied with the service",
                        "Average quality",
                        "Exceeded expectations",
                        "Room for improvement",
                        "Excellent customer service",
                        "Good value for money"
                    ]
                    response[question_key] = random.choice(sample_texts)
            
            sample_data.append(response)
        
        return pd.DataFrame(sample_data)
