import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

def render_questionnaire_form(questionnaire_data):
    """Render the questionnaire form and collect responses"""
    if not questionnaire_data or 'questions' not in questionnaire_data:
        st.error("Invalid questionnaire data")
        return None
    
    st.header(questionnaire_data.get('title', 'Survey'))
    st.markdown(questionnaire_data.get('description', ''))
    
    responses = {}
    
    with st.form("questionnaire_form"):
        for i, question in enumerate(questionnaire_data['questions']):
            question_key = f"q_{i}"
            question_text = question['question_text']
            question_type = question['question_type']
            required = question.get('required', False)
            
            # Add required indicator
            if required:
                question_text += " *"
            
            if question_type == 'text':
                responses[question_key] = st.text_area(
                    question_text,
                    key=question_key,
                    help="Please provide your answer in text format"
                )
                
            elif question_type == 'number':
                responses[question_key] = st.number_input(
                    question_text,
                    key=question_key,
                    help="Please enter a numerical value"
                )
                
            elif question_type == 'select':
                options = question.get('options', [])
                if options:
                    responses[question_key] = st.selectbox(
                        question_text,
                        options=options,
                        key=question_key,
                        index=None if required else 0
                    )
                else:
                    st.error(f"No options provided for question: {question_text}")
                    
            elif question_type == 'multiselect':
                options = question.get('options', [])
                if options:
                    responses[question_key] = st.multiselect(
                        question_text,
                        options=options,
                        key=question_key
                    )
                else:
                    st.error(f"No options provided for question: {question_text}")
                    
            elif question_type == 'date':
                responses[question_key] = st.date_input(
                    question_text,
                    key=question_key
                )
                
            elif question_type == 'boolean':
                responses[question_key] = st.checkbox(
                    question_text,
                    key=question_key
                )
                
            else:
                st.error(f"Unknown question type: {question_type}")
        
        submitted = st.form_submit_button("Submit Response")
        
        if submitted:
            # Validate required fields
            valid = True
            for i, question in enumerate(questionnaire_data['questions']):
                question_key = f"q_{i}"
                if question.get('required', False):
                    if not responses.get(question_key):
                        st.error(f"Please answer the required question: {question['question_text']}")
                        valid = False
            
            if valid:
                return responses
    
    return None

def create_shareable_form(questionnaire_data):
    """Create a shareable form page"""
    st.set_page_config(
        page_title=questionnaire_data.get('title', 'Survey'),

        layout="wide"
    )
    
    # Custom CSS for better form styling
    st.markdown("""
    <style>
    .stForm {
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    .required {
        color: red;
    }
    </style>
    """, unsafe_allow_html=True)
    
    responses = render_questionnaire_form(questionnaire_data)
    
    if responses:
        # Save response (in a real implementation, this would go to the database)
        response_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # For demonstration, show success message
        st.success("Thank you for your response! Your submission has been recorded.")
        
        # In a real implementation, you would save to Google Sheets here
        # st.session_state.sheets_client.save_response(sheet_url, list(responses.values()))
        
        return {
            'response_id': response_id,
            'timestamp': timestamp,
            'responses': responses
        }
    
    return None

def generate_form_html(questionnaire_data, form_action_url):
    """Generate HTML form for external hosting"""
    if not questionnaire_data or 'questions' not in questionnaire_data:
        return ""
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{questionnaire_data.get('title', 'Survey')}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .form-container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .question {{
                margin-bottom: 20px;
            }}
            label {{
                display: block;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            input, select, textarea {{
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }}
            textarea {{
                height: 100px;
                resize: vertical;
            }}
            .required {{
                color: red;
            }}
            .submit-btn {{
                background-color: #007bff;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }}
            .submit-btn:hover {{
                background-color: #0056b3;
            }}
        </style>
    </head>
    <body>
        <div class="form-container">
            <h1>{questionnaire_data.get('title', 'Survey')}</h1>
            <p>{questionnaire_data.get('description', '')}</p>
            
            <form action="{form_action_url}" method="POST">
    """
    
    for i, question in enumerate(questionnaire_data['questions']):
        question_text = question['question_text']
        question_type = question['question_type']
        required = question.get('required', False)
        field_name = f"q_{i}"
        
        required_attr = "required" if required else ""
        required_indicator = '<span class="required">*</span>' if required else ""
        
        html += f'<div class="question">'
        html += f'<label for="{field_name}">{question_text} {required_indicator}</label>'
        
        if question_type == 'text':
            html += f'<textarea name="{field_name}" id="{field_name}" {required_attr}></textarea>'
        elif question_type == 'number':
            html += f'<input type="number" name="{field_name}" id="{field_name}" {required_attr}>'
        elif question_type == 'select':
            options = question.get('options', [])
            html += f'<select name="{field_name}" id="{field_name}" {required_attr}>'
            if not required:
                html += '<option value="">-- Please select --</option>'
            for option in options:
                html += f'<option value="{option}">{option}</option>'
            html += '</select>'
        elif question_type == 'date':
            html += f'<input type="date" name="{field_name}" id="{field_name}" {required_attr}>'
        elif question_type == 'boolean':
            html += f'<input type="checkbox" name="{field_name}" id="{field_name}" value="true">'
        
        html += '</div>'
    
    html += """
                <button type="submit" class="submit-btn">Submit Response</button>
            </form>
        </div>
    </body>
    </html>
    """
    
    return html

def validate_questionnaire(questionnaire_data):
    """Validate questionnaire structure and content"""
    if not questionnaire_data:
        return False, "Questionnaire data is empty"
    
    if 'title' not in questionnaire_data:
        return False, "Questionnaire must have a title"
    
    if 'questions' not in questionnaire_data or not questionnaire_data['questions']:
        return False, "Questionnaire must have at least one question"
    
    for i, question in enumerate(questionnaire_data['questions']):
        if 'question_text' not in question:
            return False, f"Question {i+1} is missing question text"
        
        if 'question_type' not in question:
            return False, f"Question {i+1} is missing question type"
        
        valid_types = ['text', 'number', 'select', 'multiselect', 'date', 'boolean']
        if question['question_type'] not in valid_types:
            return False, f"Question {i+1} has invalid type: {question['question_type']}"
        
        if question['question_type'] in ['select', 'multiselect']:
            if 'options' not in question or not question['options']:
                return False, f"Question {i+1} of type {question['question_type']} must have options"
    
    return True, "Questionnaire is valid"
