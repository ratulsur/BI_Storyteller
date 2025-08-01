import streamlit as st
from utils.database_client import DatabaseClient
from utils.form_generator import FormGenerator
import pandas as pd
import io
import json
import random
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Data Collection - BI StoryTeller",
    layout="wide"
)

st.title("Data Collection")
st.markdown("Create interactive forms and collect responses directly in the platform using PostgreSQL database.")

# Quick sample data generation at the top
st.markdown("### 🎯 Quick Start with Sample Data")
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("Generate realistic sample responses instantly to test analysis features without manual data entry.")

with col2:
    if st.button("🚀 Generate Sample Data Now", type="primary", key="quick_sample"):
        with st.spinner("Creating 15 realistic responses..."):
            try:
                sample_data = generate_sample_responses(questionnaire)
                
                # Create table and insert sample data
                db_client = DatabaseClient()
                table_name = db_client.create_survey_table(questionnaire)
                
                if table_name:
                    success_count = 0
                    for sample in sample_data:
                        if db_client.submit_survey_response(table_name, sample):
                            success_count += 1
                    
                    st.success(f"✅ Generated {success_count} sample responses! Check the Response Management tab.")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to create database table")
            except Exception as e:
                st.error(f"Error generating sample data: {str(e)}")

st.markdown("---")

def generate_sample_responses(questionnaire):
    """Generate realistic sample responses for testing"""
    # Realistic sample data pools
    names = ["Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Emma Brown", 
             "Frank Miller", "Grace Lee", "Henry Taylor", "Iris Garcia", "Jack Martinez"]
    
    companies = ["TechCorp", "DataFlow Inc", "Innovation Labs", "Future Systems", "NextGen Solutions",
                "Global Dynamics", "Smart Industries", "Digital Ventures", "CloudTech", "AI Innovations"]
    
    departments = ["Marketing", "Sales", "Engineering", "HR", "Finance", "Operations", "IT", "Customer Service"]
    
    satisfaction_responses = ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]
    
    text_responses = [
        "The new system has improved our productivity significantly",
        "We need better training on the new processes",
        "Great initiative, looking forward to more improvements",
        "The interface could be more user-friendly",
        "Excellent results so far, team is very happy",
        "Some minor issues but overall positive experience",
        "Would like to see more customization options",
        "The implementation went smoother than expected"
    ]
    
    sample_responses = []
    
    for i in range(15):  # Generate 15 sample responses for better analysis
        response = {}
        
        for j, question in enumerate(questionnaire.get('questions', [])):
            question_id = question.get('id', f"question_{j+1}")
            question_type = question.get('type', question.get('question_type', 'text'))
            question_text = question.get('text', question.get('question', question.get('question_text', ''))).lower()
            
            # Generate contextual responses based on question content
            if question_type == 'text':
                if 'name' in question_text:
                    response[question_id] = random.choice(names)
                elif 'company' in question_text or 'organization' in question_text:
                    response[question_id] = random.choice(companies)
                elif 'department' in question_text:
                    response[question_id] = random.choice(departments)
                elif 'feedback' in question_text or 'comment' in question_text or 'suggestion' in question_text:
                    response[question_id] = random.choice(text_responses)
                else:
                    response[question_id] = f"Sample response {i+1}: " + random.choice(text_responses[:3])
                    
            elif question_type == 'email':
                name_part = random.choice(names).lower().replace(' ', '.')
                domain = random.choice(['company.com', 'business.org', 'corp.net'])
                response[question_id] = f"{name_part}@{domain}"
                
            elif question_type == 'number':
                min_val = question.get('min', 1)
                max_val = question.get('max', 100)
                if 'age' in question_text:
                    response[question_id] = random.randint(22, 65)
                elif 'year' in question_text or 'experience' in question_text:
                    response[question_id] = random.randint(1, 20)
                elif 'salary' in question_text or 'income' in question_text:
                    response[question_id] = random.randint(40000, 150000)
                else:
                    response[question_id] = random.randint(min_val, max_val)
                    
            elif question_type == 'rating':
                max_rating = question.get('max', 5)
                # Weight towards positive responses for satisfaction questions
                if 'satisfaction' in question_text or 'happy' in question_text:
                    response[question_id] = random.choices(
                        range(1, max_rating + 1),
                        weights=[10, 15, 25, 30, 20]  # Weighted towards higher ratings
                    )[0]
                else:
                    response[question_id] = random.randint(1, max_rating)
                    
            elif question_type == 'select':
                options = question.get('options', satisfaction_responses)
                if 'satisfaction' in question_text:
                    # Weight towards positive responses
                    response[question_id] = random.choices(
                        satisfaction_responses,
                        weights=[5, 25, 15, 30, 25]
                    )[0]
                elif 'department' in question_text and departments[0] in str(options):
                    response[question_id] = random.choice(departments)
                else:
                    response[question_id] = random.choice(options)
                    
            elif question_type == 'multiselect':
                options = question.get('options', ['Option 1', 'Option 2', 'Option 3'])
                num_selections = random.randint(1, min(3, len(options)))
                response[question_id] = random.sample(options, num_selections)
                
            elif question_type == 'boolean':
                # Weight towards True for positive questions
                if 'recommend' in question_text or 'satisfied' in question_text:
                    response[question_id] = random.choices([True, False], weights=[70, 30])[0]
                else:
                    response[question_id] = random.choice([True, False])
                    
            elif question_type == 'date':
                if 'birth' in question_text:
                    # Generate birth dates for working age adults
                    base_year = datetime.now().year - random.randint(25, 60)
                    birth_date = datetime(base_year, random.randint(1, 12), random.randint(1, 28))
                    response[question_id] = birth_date.date().isoformat()
                elif 'start' in question_text or 'join' in question_text:
                    # Generate start dates within last 10 years
                    base_date = datetime.now() - timedelta(days=random.randint(30, 3650))
                    response[question_id] = base_date.date().isoformat()
                else:
                    # Random date within last year
                    base_date = datetime.now() - timedelta(days=random.randint(0, 365))
                    response[question_id] = base_date.date().isoformat()
            else:
                response[question_id] = f"Sample data {i+1}"
        
        sample_responses.append(response)
    
    return sample_responses

# Check prerequisites
if not st.session_state.get('questionnaire'):
    st.warning("Please create a questionnaire first.")
    if st.button("Go to Questionnaire Page"):
        st.switch_page("pages/2_Questionnaire.py")
    st.stop()

# Initialize form generator if not exists
if 'form_generator' not in st.session_state:
    st.session_state.form_generator = FormGenerator()

questionnaire = st.session_state.questionnaire
form_generator = st.session_state.form_generator

# Create tabs for different collection methods
tab1, tab2, tab3 = st.tabs(["Interactive Form", "Response Management", "Data Export"])

with tab1:
    st.header("Interactive Data Collection Form")
    
    # Display questionnaire info
    with st.expander("Questionnaire Details", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Title", questionnaire.get('title', 'N/A'))
        
        with col2:
            st.metric("Questions", len(questionnaire.get('questions', [])))
        
        with col3:
            required_count = sum(1 for q in questionnaire.get('questions', []) if q.get('required', False))
            st.metric("Required Questions", required_count)
    
    st.markdown("---")
    
    # Check if we're in submission mode
    if st.session_state.get('show_success_message'):
        st.success("Thank you! Your response has been recorded successfully.")
        if st.button("Submit Another Response"):
            st.session_state.show_success_message = False
            st.rerun()
    else:
        # Render the interactive form
        st.markdown("### Fill out the questionnaire below:")
        
        table_name = form_generator.render_survey_form(questionnaire)
        
        if table_name:
            st.session_state.show_success_message = True
            st.session_state.current_table_name = table_name
            st.rerun()

with tab2:
    st.header("Response Management")
    
    # Get response count
    response_count = form_generator.get_response_count(questionnaire)
    
    # Show current status
    if response_count == 0:
        st.info("💡 Tip: Use the 'Generate Sample Data Now' button at the top for instant testing data!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Responses", response_count)
    
    with col2:
        if response_count and response_count > 0:
            completion_rate = min(100, (response_count / 10) * 100)  # Assume target of 10 responses
            st.metric("Progress", f"{completion_rate:.1f}%")
        else:
            st.metric("Progress", "0%")
    
    with col3:
        if st.button("Refresh Data"):
            st.rerun()
    
    if response_count and response_count > 0:
        # Get and display responses
        responses_df = form_generator.get_form_responses(questionnaire)
        
        if responses_df is not None and not responses_df.empty:
            st.subheader("Recent Responses")
            
            # Display summary statistics
            with st.expander("Response Summary", expanded=True):
                st.markdown("**Latest Response:** " + str(responses_df['submitted_at'].max()))
                st.markdown("**First Response:** " + str(responses_df['submitted_at'].min()))
                
                # Show response distribution over time
                if len(responses_df) > 1:
                    responses_df['date'] = pd.to_datetime(responses_df['submitted_at']).dt.date
                    daily_responses = responses_df.groupby('date').size()
                    
                    if len(daily_responses) > 1:
                        st.line_chart(daily_responses)
            
            # Display responses table
            st.subheader("Response Data")
            
            # Remove internal columns for display
            display_df = responses_df.drop(columns=['id'], errors='ignore')
            
            # Format datetime columns
            if 'submitted_at' in display_df.columns:
                display_df['submitted_at'] = pd.to_datetime(display_df['submitted_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            st.dataframe(display_df, use_container_width=True)
            
            # Store data for analysis
            st.session_state.raw_data = responses_df
            st.success(f"✅ Data ready for analysis! {len(responses_df)} responses collected.")
        else:
            st.info("No responses found in database.")
    else:
        st.info("No responses collected yet. Share the form above to start collecting data.")
        
        # Always show sample data generation option when no responses exist
        st.markdown("### Generate Sample Data")
        st.markdown("Create realistic sample responses to test the analysis features.")
        
        # Option to add sample data for testing
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate Sample Data for Testing", type="primary"):
                with st.spinner("Generating realistic sample responses..."):
                    try:
                        sample_data = generate_sample_responses(questionnaire)
                        
                        # Create table and insert sample data
                        db_client = DatabaseClient()
                        table_name = db_client.create_survey_table(questionnaire)
                        
                        if table_name:
                            success_count = 0
                            for sample in sample_data:
                                if db_client.submit_survey_response(table_name, sample):
                                    success_count += 1
                            
                            st.success(f"Generated {success_count} realistic sample responses!")
                            st.rerun()
                        else:
                            st.error("Failed to create database table")
                    except Exception as e:
                        st.error(f"Error generating sample data: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
        
        with col2:
            if st.button("Clear All Data"):
                if st.session_state.get('confirm_clear'):
                    # Clear data
                    db_client = DatabaseClient()
                    table_name = f"survey_{questionnaire.get('id', 'default')}"
                    if db_client.table_exists(table_name):
                        db_client.clear_survey_responses(table_name)
                        st.success("All data cleared!")
                        st.session_state.confirm_clear = False
                        st.rerun()
                else:
                    st.session_state.confirm_clear = True
                    st.warning("Click again to confirm data deletion")
                    st.rerun()

with tab3:
    st.header("Data Export & Integration")
    
    if response_count and response_count > 0:
        responses_df = form_generator.get_form_responses(questionnaire)
        
        if responses_df is not None and not responses_df.empty:
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Download Options")
                
                # CSV download
                csv_buffer = io.StringIO()
                responses_df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="Download as CSV",
                    data=csv_data,
                    file_name=f"{questionnaire.get('title', 'survey')}_responses.csv",
                    mime="text/csv"
                )
                
                # JSON download
                json_data = responses_df.to_json(orient='records', date_format='iso')
                
                st.download_button(
                    label="Download as JSON",
                    data=json_data,
                    file_name=f"{questionnaire.get('title', 'survey')}_responses.json",
                    mime="application/json"
                )
            
            with col2:
                st.subheader("Data Preview")
                st.markdown(f"**Total Records:** {len(responses_df)}")
                st.markdown(f"**Columns:** {len(responses_df.columns)}")
                
                # Show column info
                with st.expander("Column Information"):
                    for col in responses_df.columns:
                        col_type = str(responses_df[col].dtype)
                        non_null_count = responses_df[col].count()
                        st.markdown(f"• **{col}**: {col_type} ({non_null_count} non-null)")
            
            # Continue to Analysis button
            if st.button("Continue to Data Analysis", type="primary"):
                st.session_state.raw_data = responses_df
                st.success("Data loaded for analysis!")
                st.switch_page("pages/4_Data_Preprocessing.py")
        
    else:
        st.info("No data available to export. Collect some responses first!")

# Function moved to top of file to avoid ordering issues

# Navigation help
st.sidebar.markdown("""
### Data Collection Guide

1. **Interactive Form**: Fill out questionnaire directly in the platform
2. **Response Management**: View and manage collected responses  
3. **Data Export**: Download data for external analysis

**Database Features:**
- Real-time data storage
- Automatic table creation
- Response validation
- Export capabilities
""")