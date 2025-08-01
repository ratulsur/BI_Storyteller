import streamlit as st
from utils.questionnaire_generator import render_questionnaire_form, generate_form_html
import pandas as pd
import io

st.set_page_config(
    page_title="Data Collection - AI Data Analysis Platform",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Data Collection")
st.markdown("Deploy your questionnaire and collect responses from your target audience.")

# Check prerequisites
if not st.session_state.get('questionnaire'):
    st.warning("Please create a questionnaire first.")
    if st.button("Go to Questionnaire Page"):
        st.switch_page("pages/2_Questionnaire.py")
    st.stop()

# Display questionnaire info
st.header("📋 Questionnaire Information")
questionnaire = st.session_state.questionnaire
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Title", questionnaire.get('title', 'N/A'))

with col2:
    st.metric("Questions", len(questionnaire.get('questions', [])))

with col3:
    required_count = sum(1 for q in questionnaire.get('questions', []) if q.get('required', False))
    st.metric("Required Questions", required_count)

# Deployment section
st.header("🚀 Deploy Questionnaire")

if not st.session_state.get('questionnaire_approved'):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("Click 'Approve & Deploy' to make your questionnaire available for data collection.")
    
    with col2:
        if st.button("✅ Approve & Deploy", type="primary", use_container_width=True):
            st.session_state.questionnaire_approved = True
            
            # Create Google Sheet (if client is available)
            if hasattr(st.session_state, 'sheets_client') and st.session_state.sheets_client.client:
                with st.spinner("Creating Google Sheet for data collection..."):
                    try:
                        sheet_url = st.session_state.sheets_client.create_questionnaire_sheet(questionnaire)
                        if sheet_url:
                            st.session_state.questionnaire_link = sheet_url
                            st.success("Questionnaire deployed successfully!")
                        else:
                            st.warning("Failed to create Google Sheet. Using local data collection.")
                    except Exception as e:
                        st.error(f"Error creating Google Sheet: {str(e)}")
            else:
                st.session_state.questionnaire_link = "demo_link"
                st.success("Questionnaire approved for data collection!")
            
            st.rerun()

if st.session_state.get('questionnaire_approved'):
    st.success("✅ Questionnaire is approved and ready for data collection!")
    
    # Share questionnaire
    st.header("🔗 Share Questionnaire")
    
    tab1, tab2, tab3 = st.tabs(["📱 Interactive Form", "🔗 Shareable Link", "💻 HTML Code"])
    
    with tab1:
        st.markdown("### Fill out the questionnaire below:")
        
        # Render the questionnaire form directly
        responses = render_questionnaire_form(questionnaire)
        
        if responses:
            st.success("Response submitted successfully!")
            
            # Save to session state (simulate database storage)
            if 'collected_responses' not in st.session_state:
                st.session_state.collected_responses = []
            
            # Convert responses to a format suitable for DataFrame
            response_data = {}
            response_data['Timestamp'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            response_data['Response_ID'] = f"R{len(st.session_state.collected_responses) + 1}"
            
            for i, question in enumerate(questionnaire['questions']):
                question_key = f"q_{i}"
                column_name = f"Q{i+1}_{question['question_text'][:50]}"
                response_data[column_name] = responses.get(question_key, "")
            
            st.session_state.collected_responses.append(response_data)
            
            # Also try to save to Google Sheets if available
            if st.session_state.get('questionnaire_link') and st.session_state.get('questionnaire_link') != "demo_link":
                try:
                    success = st.session_state.sheets_client.save_response(
                        st.session_state.questionnaire_link,
                        list(responses.values())
                    )
                    if success:
                        st.info("Response also saved to Google Sheets!")
                except Exception as e:
                    st.warning(f"Could not save to Google Sheets: {str(e)}")
            
            st.rerun()
    
    with tab2:
        if st.session_state.get('questionnaire_link'):
            st.markdown("### Shareable Link")
            if st.session_state.questionnaire_link != "demo_link":
                st.code(st.session_state.questionnaire_link)
                st.markdown("Share this link with your target audience to collect responses.")
            else:
                st.info("In a production environment, this would be a shareable Google Forms or external survey link.")
        else:
            st.info("Generate a shareable link by deploying the questionnaire.")
    
    with tab3:
        st.markdown("### HTML Form Code")
        st.markdown("Use this HTML code to embed the form in your website:")
        
        html_code = generate_form_html(questionnaire, "/submit-response")
        st.code(html_code, language="html")
        
        # Download HTML file
        html_bytes = html_code.encode('utf-8')
        st.download_button(
            label="📥 Download HTML File",
            data=html_bytes,
            file_name=f"{questionnaire.get('title', 'questionnaire').replace(' ', '_')}.html",
            mime="text/html"
        )

# Data collection status
st.header("📈 Data Collection Status")

# Get responses
responses_df = None
if st.session_state.get('collected_responses'):
    responses_df = pd.DataFrame(st.session_state.collected_responses)
elif st.session_state.get('questionnaire_link') and st.session_state.get('questionnaire_link') != "demo_link":
    # Try to get responses from Google Sheets
    try:
        responses_df = st.session_state.sheets_client.get_responses(st.session_state.questionnaire_link)
    except Exception as e:
        st.warning(f"Could not retrieve responses from Google Sheets: {str(e)}")

# If no real responses, offer to generate sample data for demonstration
if responses_df is None or responses_df.empty:
    st.info("No responses collected yet.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Options:**")
        st.markdown("• Share the questionnaire link with your audience")
        st.markdown("• Use the interactive form above to test data collection")
        st.markdown("• Generate sample data for demonstration purposes")
    
    with col2:
        if st.button("🎲 Generate Sample Data", help="Create sample responses for demonstration"):
            with st.spinner("Generating sample data..."):
                sample_df = st.session_state.sheets_client.create_sample_data(questionnaire, 20)
                if not sample_df.empty:
                    st.session_state.raw_data = sample_df
                    st.success("Sample data generated!")
                    st.rerun()

else:
    # Display collection metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Responses", len(responses_df))
    
    with col2:
        if 'Timestamp' in responses_df.columns:
            try:
                responses_df['Timestamp'] = pd.to_datetime(responses_df['Timestamp'])
                today_responses = responses_df[responses_df['Timestamp'].dt.date == pd.Timestamp.now().date()]
                st.metric("Today's Responses", len(today_responses))
            except:
                st.metric("Today's Responses", "N/A")
        else:
            st.metric("Today's Responses", "N/A")
    
    with col3:
        # Calculate completion rate (assuming all responses are complete for now)
        st.metric("Completion Rate", "100%")
    
    with col4:
        if 'Timestamp' in responses_df.columns:
            try:
                latest_response = responses_df['Timestamp'].max()
                st.metric("Latest Response", latest_response.strftime("%H:%M"))
            except:
                st.metric("Latest Response", "N/A")
        else:
            st.metric("Latest Response", "N/A")
    
    # Display recent responses
    st.subheader("📋 Recent Responses")
    
    # Show last 5 responses
    display_df = responses_df.tail(5).copy()
    if not display_df.empty:
        # Truncate long text for display
        for col in display_df.columns:
            if display_df[col].dtype == 'object':
                display_df[col] = display_df[col].astype(str).apply(
                    lambda x: x[:50] + "..." if len(x) > 50 else x
                )
        
        st.dataframe(display_df, use_container_width=True)
    
    # Download responses
    st.subheader("📥 Download Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = responses_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv_data,
            file_name=f"{questionnaire.get('title', 'survey')}_responses.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        json_data = responses_df.to_json(orient='records', indent=2)
        st.download_button(
            label="📥 Download as JSON",
            data=json_data,
            file_name=f"{questionnaire.get('title', 'survey')}_responses.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Save to session state for next steps
    st.session_state.raw_data = responses_df
    
    # Next steps
    st.header("🎯 Next Steps")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Ready for Data Preprocessing**\nClean and prepare your collected data for analysis.")
        if st.button("🧹 Clean Data", type="primary", use_container_width=True):
            st.switch_page("pages/4_Data_Preprocessing.py")
    
    with col2:
        st.info("**Quick Analysis**\nJump directly to analysis with the raw data.")
        if st.button("📊 Analyze Data", use_container_width=True):
            st.switch_page("pages/5_Analysis.py")

# Navigation
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("⬅️ Back to Questionnaire", use_container_width=True):
        st.switch_page("pages/2_Questionnaire.py")

with col2:
    raw_data = st.session_state.get('raw_data')
    has_data = raw_data is not None and not raw_data.empty
    if st.button("➡️ Next: Data Preprocessing", use_container_width=True, disabled=not has_data):
        st.switch_page("pages/4_Data_Preprocessing.py")
