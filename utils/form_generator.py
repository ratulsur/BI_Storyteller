import streamlit as st
import json
from datetime import datetime, date
from utils.database_client import DatabaseClient

class FormGenerator:
    def __init__(self):
        self.db_client = DatabaseClient()
    
    def render_survey_form(self, questionnaire_data):
        """Render a Streamlit form based on questionnaire structure"""
        if not questionnaire_data or 'questions' not in questionnaire_data:
            st.error("Invalid questionnaire data")
            return None
        
        st.markdown(f"## {questionnaire_data.get('title', 'Survey')}")
        st.markdown(questionnaire_data.get('description', ''))
        
        # Create form
        with st.form(key=f"survey_form_{questionnaire_data.get('id', 'default')}"):
            response_data = {}
            
            for i, question in enumerate(questionnaire_data['questions']):
                question_id = question.get('id', f"question_{i+1}")
                question_text = question.get('text', question.get('question', question.get('question_text', '')))
                question_type = question.get('type', question.get('question_type', 'text'))
                required = question.get('required', False)
                
                # Add required indicator
                label = f"{question_text} {'*' if required else ''}"
                
                if question_type == 'text':
                    response_data[question_id] = st.text_input(
                        label,
                        placeholder=question.get('placeholder', ''),
                        help=question.get('help', None)
                    )
                
                elif question_type == 'email':
                    response_data[question_id] = st.text_input(
                        label,
                        placeholder="example@email.com",
                        help=question.get('help', None)
                    )
                
                elif question_type == 'number':
                    min_val = question.get('min', None)
                    max_val = question.get('max', None)
                    response_data[question_id] = st.number_input(
                        label,
                        min_value=min_val,
                        max_value=max_val,
                        help=question.get('help', None)
                    )
                
                elif question_type == 'rating':
                    max_rating = question.get('max', 5)
                    response_data[question_id] = st.slider(
                        label,
                        min_value=1,
                        max_value=max_rating,
                        value=1,
                        help=question.get('help', None)
                    )
                
                elif question_type == 'select':
                    options = question.get('options', [])
                    response_data[question_id] = st.selectbox(
                        label,
                        options=[''] + options if not required else options,
                        help=question.get('help', None)
                    )
                
                elif question_type == 'multiselect':
                    options = question.get('options', [])
                    response_data[question_id] = st.multiselect(
                        label,
                        options=options,
                        help=question.get('help', None)
                    )
                
                elif question_type == 'boolean':
                    response_data[question_id] = st.checkbox(
                        label,
                        help=question.get('help', None)
                    )
                
                elif question_type == 'date':
                    response_data[question_id] = st.date_input(
                        label,
                        help=question.get('help', None)
                    )
                
                elif question_type == 'textarea':
                    response_data[question_id] = st.text_area(
                        label,
                        placeholder=question.get('placeholder', ''),
                        help=question.get('help', None)
                    )
                
                else:
                    # Default to text input
                    response_data[question_id] = st.text_input(
                        label,
                        placeholder=question.get('placeholder', ''),
                        help=question.get('help', None)
                    )
            
            # Submit button
            submitted = st.form_submit_button("Submit Response", type="primary")
            
            if submitted:
                # Validate required fields
                validation_errors = []
                for i, question in enumerate(questionnaire_data['questions']):
                    if question.get('required', False):
                        question_id = question.get('id', f"question_{i+1}")
                        value = response_data.get(question_id)
                        question_text = question.get('text', question.get('question', question.get('question_text', '')))
                        if not value or (isinstance(value, str) and not value.strip()):
                            validation_errors.append(f"'{question_text}' is required")
                
                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                    return None
                
                # Process and save response
                return self._save_response(questionnaire_data, response_data)
        
        return None
    
    def _save_response(self, questionnaire_data, response_data):
        """Save survey response to database"""
        try:
            # Create table if it doesn't exist
            table_name = self.db_client.create_survey_table(questionnaire_data)
            if not table_name:
                st.error("Failed to create survey table")
                return None
            
            # Clean and prepare data
            cleaned_data = {}
            for key, value in response_data.items():
                if isinstance(value, date):
                    cleaned_data[key] = value.isoformat()
                elif isinstance(value, list):
                    # Convert list to PostgreSQL array format
                    cleaned_data[key] = value
                elif value is None or value == '':
                    cleaned_data[key] = None
                else:
                    cleaned_data[key] = value
            
            # Submit to database
            success = self.db_client.submit_survey_response(table_name, cleaned_data)
            
            if success:
                st.success("Response submitted successfully!")
                st.balloons()
                return table_name
            else:
                st.error("Failed to submit response")
                return None
                
        except Exception as e:
            st.error(f"Error saving response: {str(e)}")
            return None
    
    def get_form_responses(self, questionnaire_data):
        """Get all responses for a questionnaire"""
        if not questionnaire_data:
            return None
            
        table_name = f"survey_{questionnaire_data.get('id', 'default')}"
        
        if not self.db_client.table_exists(table_name):
            return None
            
        return self.db_client.get_survey_responses(table_name)
    
    def get_response_count(self, questionnaire_data):
        """Get total response count"""
        if not questionnaire_data:
            return 0
            
        table_name = f"survey_{questionnaire_data.get('id', 'default')}"
        return self.db_client.get_response_count(table_name)
    
    def delete_survey_data(self, questionnaire_data):
        """Delete all survey data"""
        if not questionnaire_data:
            return False
            
        table_name = f"survey_{questionnaire_data.get('id', 'default')}"
        return self.db_client.delete_table(table_name)