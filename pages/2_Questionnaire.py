import streamlit as st
from utils.questionnaire_generator import validate_questionnaire, generate_form_html
import json

st.set_page_config(
    page_title="Questionnaire - BI StoryTeller",

    layout="wide"
)

st.title("Questionnaire Generation")
st.markdown("Generate a comprehensive questionnaire based on your extracted variables.")

# Check prerequisites
if not st.session_state.get('business_problem'):
    st.warning("Please define your business problem on the main page first.")
    if st.button("Go to Main Page"):
        st.switch_page("app.py")
    st.stop()

if not st.session_state.get('variables'):
    st.warning("Please extract variables first.")
    if st.button("Go to Variables Page"):
        st.switch_page("pages/1_Variables.py")
    st.stop()

# Display context
st.header("Context")
with st.expander("View Business Problem and Variables", expanded=False):
    st.markdown("**Business Problem:**")
    st.info(st.session_state.business_problem)
    
    st.markdown("**Extracted Variables:**")
    for var in st.session_state.variables:
        st.markdown(f"• **{var['name']}** ({var['type']}): {var['description']}")

# Questionnaire generation section
st.header("🤖 Generate Questionnaire")

col1, col2 = st.columns([2, 1])

with col1:
    if st.button("Form Generate Questionnaire", type="primary", use_container_width=True):
        with st.spinner("Generating questionnaire based on your business problem and variables..."):
            try:
                questionnaire = st.session_state.groq_client.generate_questionnaire(
                    st.session_state.business_problem,
                    st.session_state.variables
                )
                
                if questionnaire:
                    # Validate questionnaire
                    is_valid, message = validate_questionnaire(questionnaire)
                    if is_valid:
                        st.session_state.questionnaire = questionnaire
                        st.success("Questionnaire generated successfully!")
                        st.rerun()
                    else:
                        st.error(f"Generated questionnaire is invalid: {message}")
                else:
                    st.error("Failed to generate questionnaire. Please try again.")
            except Exception as e:
                st.error(f"Error generating questionnaire: {str(e)}")

with col2:
    if st.session_state.questionnaire:
        st.metric("Questions Generated", len(st.session_state.questionnaire.get('questions', [])))

# Display generated questionnaire
if st.session_state.questionnaire:
    st.header("Generated Questionnaire")
    
    questionnaire = st.session_state.questionnaire
    
    # Questionnaire header
    st.subheader(questionnaire.get('title', 'Survey'))
    st.markdown(questionnaire.get('description', ''))
    
    # Display questions
    questions = questionnaire.get('questions', [])
    
    if questions:
        st.markdown("**Questions:**")
        
        for i, question in enumerate(questions):
            with st.expander(f"Question {i+1}: {question['question_text']}", expanded=False):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Question:** {question['question_text']}")
                    if question.get('options'):
                        st.markdown("**Options:**")
                        for option in question['options']:
                            st.markdown(f"• {option}")
                
                with col2:
                    st.markdown(f"**{question['question_type'].title()}**")
                
                with col3:
                    required_badge = "Approve Required" if question.get('required', False) else "OptionalOptional"
                    st.markdown(required_badge)
    
    # Edit questionnaire section
    st.header("Edit Questionnaire")
    
    with st.form("edit_questionnaire"):
        # Edit title and description
        title = st.text_input("Title", value=questionnaire.get('title', ''))
        description = st.text_area("Description", value=questionnaire.get('description', ''), height=100)
        
        st.subheader("Questions")
        
        edited_questions = []
        
        for i, question in enumerate(questions):
            st.markdown(f"**Question {i+1}**")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                q_text = st.text_area(
                    f"Question Text",
                    value=question['question_text'],
                    key=f"q_text_{i}",
                    height=60
                )
            
            with col2:
                q_type = st.selectbox(
                    f"Type",
                    options=['text', 'number', 'select', 'multiselect', 'date', 'boolean'],
                    index=['text', 'number', 'select', 'multiselect', 'date', 'boolean'].index(question['question_type']),
                    key=f"q_type_{i}"
                )
                
                required = st.checkbox(
                    f"Required",
                    value=question.get('required', False),
                    key=f"q_required_{i}"
                )
            
            # Options for select/multiselect questions
            options = []
            if q_type in ['select', 'multiselect']:
                existing_options = question.get('options', [])
                options_text = st.text_area(
                    f"Options (one per line)",
                    value='\n'.join(existing_options),
                    key=f"q_options_{i}",
                    height=80
                )
                options = [opt.strip() for opt in options_text.split('\n') if opt.strip()]
            
            if q_text:
                edited_question = {
                    'question_text': q_text,
                    'question_type': q_type,
                    'required': required
                }
                if options:
                    edited_question['options'] = options
                
                edited_questions.append(edited_question)
            
            st.divider()
        
        # Add new question
        st.subheader("Add New Question")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            new_q_text = st.text_area("New Question Text", key="new_q_text", height=60)
        
        with col2:
            new_q_type = st.selectbox(
                "Type",
                options=['text', 'number', 'select', 'multiselect', 'date', 'boolean'],
                key="new_q_type"
            )
            
            new_required = st.checkbox("Required", key="new_q_required")
        
        new_options = []
        if new_q_type in ['select', 'multiselect']:
            new_options_text = st.text_area("Options (one per line)", key="new_q_options", height=80)
            new_options = [opt.strip() for opt in new_options_text.split('\n') if opt.strip()]
        
        if new_q_text:
            new_question = {
                'question_text': new_q_text,
                'question_type': new_q_type,
                'required': new_required
            }
            if new_options:
                new_question['options'] = new_options
            
            edited_questions.append(new_question)
        
        # Form submission
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                if title and edited_questions:
                    updated_questionnaire = {
                        'title': title,
                        'description': description,
                        'questions': edited_questions
                    }
                    
                    is_valid, message = validate_questionnaire(updated_questionnaire)
                    if is_valid:
                        st.session_state.questionnaire = updated_questionnaire
                        st.success("Questionnaire updated successfully!")
                        st.rerun()
                    else:
                        st.error(f"Invalid questionnaire: {message}")
                else:
                    st.error("Title and at least one question are required.")
        
        with col2:
            if st.form_submit_button("🔄 Regenerate", use_container_width=True):
                with st.spinner("Regenerating questionnaire..."):
                    try:
                        new_questionnaire = st.session_state.groq_client.generate_questionnaire(
                            st.session_state.business_problem,
                            st.session_state.variables
                        )
                        if new_questionnaire:
                            st.session_state.questionnaire = new_questionnaire
                            st.success("Questionnaire regenerated!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error regenerating questionnaire: {str(e)}")
        
        with col3:
            if st.form_submit_button("Approve Approve & Deploy", type="primary", use_container_width=True):
                if title and edited_questions:
                    updated_questionnaire = {
                        'title': title,
                        'description': description,
                        'questions': edited_questions
                    }
                    
                    is_valid, message = validate_questionnaire(updated_questionnaire)
                    if is_valid:
                        st.session_state.questionnaire = updated_questionnaire
                        st.session_state.questionnaire_approved = True
                        st.switch_page("pages/3_Data_Collection.py")
                    else:
                        st.error(f"Cannot approve invalid questionnaire: {message}")

# Preview section
if st.session_state.questionnaire:
    st.header("👀 Preview")
    st.markdown("This is how your questionnaire will appear to respondents:")
    
    with st.container(border=True):
        st.markdown(f"### {st.session_state.questionnaire.get('title', 'Survey')}")
        st.markdown(st.session_state.questionnaire.get('description', ''))
        
        for i, question in enumerate(st.session_state.questionnaire.get('questions', [])):
            question_text = question['question_text']
            if question.get('required', False):
                question_text += " *"
            
            if question['question_type'] == 'text':
                st.text_area(question_text, disabled=True, key=f"preview_text_{i}")
            elif question['question_type'] == 'number':
                st.number_input(question_text, disabled=True, key=f"preview_number_{i}")
            elif question['question_type'] == 'select':
                options = question.get('options', [])
                st.selectbox(question_text, options, disabled=True, key=f"preview_select_{i}")
            elif question['question_type'] == 'multiselect':
                options = question.get('options', [])
                st.multiselect(question_text, options, disabled=True, key=f"preview_multiselect_{i}")
            elif question['question_type'] == 'date':
                st.date_input(question_text, disabled=True, key=f"preview_date_{i}")
            elif question['question_type'] == 'boolean':
                st.checkbox(question_text, disabled=True, key=f"preview_bool_{i}")

# Navigation
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("Back to Variables", use_container_width=True):
        st.switch_page("pages/1_Variables.py")

with col2:
    if st.button("Next: Data Collection", use_container_width=True, disabled=not st.session_state.questionnaire):
        if st.session_state.questionnaire:
            st.session_state.questionnaire_approved = True
        st.switch_page("pages/3_Data_Collection.py")
