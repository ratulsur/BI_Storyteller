import streamlit as st

st.set_page_config(
    page_title="Variables - BI StoryTeller",
    layout="wide"
)

st.title("Variable Extraction")
st.markdown("AI will analyze your business problem and identify key variables for data collection.")

# Check if business problem exists
if not st.session_state.get('business_problem'):
    st.warning("Please define your business problem on the main page first.")
    if st.button("Go to Main Page"):
        st.switch_page("app.py")
    st.stop()

# Display business problem
st.header("Business Problem")
st.info(st.session_state.business_problem)

# Variable extraction section
st.header("Variable Extraction")

col1, col2 = st.columns([2, 1])

with col1:
    if st.button("Extract Variables", type="primary", use_container_width=True):
        with st.spinner("Analyzing business problem and extracting variables..."):
            try:
                variables = st.session_state.groq_client.extract_variables(st.session_state.business_problem)
                
                if variables:
                    st.session_state.variables = variables
                    st.success(f"Successfully extracted {len(variables)} variables!")
                    st.rerun()
                else:
                    st.error("Failed to extract variables. Please try again or refine your business problem.")
            except Exception as e:
                st.error(f"Error extracting variables: {str(e)}")

with col2:
    if st.session_state.variables:
        st.metric("Variables Found", len(st.session_state.variables))

# Display extracted variables
if st.session_state.variables:
    st.header("Extracted Variables")
    st.markdown("These are the key variables identified from your business problem:")
    
    # Create tabs for different variable types
    variable_types = list(set(var['type'] for var in st.session_state.variables))
    
    if len(variable_types) > 1:
        tabs = st.tabs([f"{vtype.title()} Variables" for vtype in variable_types])
        
        for i, vtype in enumerate(variable_types):
            with tabs[i]:
                filtered_vars = [var for var in st.session_state.variables if var['type'] == vtype]
                for var in filtered_vars:
                    with st.expander(f"{var['name']}", expanded=True):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Description:** {var['description']}")
                        with col2:
                            st.markdown(f"**{var['type'].title()}**")
    else:
        # Single type, display directly
        for var in st.session_state.variables:
            with st.expander(f"{var['name']}", expanded=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Description:** {var['description']}")
                with col2:
                    st.markdown(f"**{var['type'].title()}**")
    
    # Edit variables section
    st.header("Edit Variables")
    st.markdown("You can modify, add, or remove variables before proceeding to questionnaire generation.")
    
    # Create a form for editing variables
    with st.form("edit_variables"):
        edited_variables = []
        
        for i, var in enumerate(st.session_state.variables):
            st.subheader(f"Variable {i+1}")
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                name = st.text_input(f"Name", value=var['name'], key=f"name_{i}")
            with col2:
                var_type = st.selectbox(
                    f"Type", 
                    options=['categorical', 'numerical', 'text', 'date', 'boolean'],
                    index=['categorical', 'numerical', 'text', 'date', 'boolean'].index(var['type']),
                    key=f"type_{i}"
                )
            with col3:
                description = st.text_area(f"Description", value=var['description'], key=f"desc_{i}", height=50)
            
            if name and description:
                edited_variables.append({
                    'name': name,
                    'type': var_type,
                    'description': description
                })
            
            st.divider()
        
        # Add new variable section
        st.subheader("Add New Variable")
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            new_name = st.text_input("New Variable Name", key="new_name")
        with col2:
            new_type = st.selectbox(
                "Type", 
                options=['categorical', 'numerical', 'text', 'date', 'boolean'],
                key="new_type"
            )
        with col3:
            new_description = st.text_area("Description", key="new_desc", height=50)
        
        if new_name and new_description:
            edited_variables.append({
                'name': new_name,
                'type': new_type,
                'description': new_description
            })
        
        # Form submission
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                if edited_variables:
                    st.session_state.variables = edited_variables
                    st.success("Variables updated successfully!")
                    st.rerun()
                else:
                    st.error("At least one variable is required.")
        
        with col2:
            if st.form_submit_button("🔄 Reset to Original", use_container_width=True):
                # Re-extract variables
                with st.spinner("Re-extracting variables..."):
                    try:
                        variables = st.session_state.groq_client.extract_variables(st.session_state.business_problem)
                        if variables:
                            st.session_state.variables = variables
                            st.success("Variables reset to original extraction!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error re-extracting variables: {str(e)}")
        
        with col3:
            if st.form_submit_button("Next Create Questionnaire", type="primary", use_container_width=True):
                if edited_variables:
                    st.session_state.variables = edited_variables
                    st.switch_page("pages/2_Questionnaire.py")
                else:
                    st.error("Please save your variables first.")

# Navigation
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("Back to Main", use_container_width=True):
        st.switch_page("app.py")

with col2:
    if st.button("Next: Create Questionnaire", use_container_width=True, disabled=not st.session_state.variables):
        st.switch_page("pages/2_Questionnaire.py")
