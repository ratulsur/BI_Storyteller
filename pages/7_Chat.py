import streamlit as st
from utils.data_processor import DataProcessor
import pandas as pd
import json
from datetime import datetime

st.set_page_config(
    page_title="Chat - BI StoryTeller",

    layout="wide"
)

st.title("AI Chat Assistant")
st.markdown("Ask questions about your data and get AI-powered insights in real-time.")

# Check if we have data and context
data_to_analyze = st.session_state.get('processed_data')
if data_to_analyze is None or data_to_analyze.empty:
    data_to_analyze = st.session_state.get('raw_data')

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize data context
if 'data_context' not in st.session_state:
    st.session_state.data_context = ""

# Create data context for AI
def create_data_context():
    """Create a comprehensive context about the data for the AI"""
    if data_to_analyze is None or data_to_analyze.empty:
        return "No data is currently loaded for analysis."
    
    context = f"""
Data Overview:
- Total records: {data_to_analyze.shape[0]}
- Total variables: {data_to_analyze.shape[1]}
- Columns: {', '.join(data_to_analyze.columns.tolist())}

Data Types:
"""
    
    for col in data_to_analyze.columns:
        dtype = str(data_to_analyze[col].dtype)
        unique_count = data_to_analyze[col].nunique()
        missing_count = data_to_analyze[col].isnull().sum()
        context += f"- {col}: {dtype} ({unique_count} unique values, {missing_count} missing)\n"
    
    # Add statistical summary for numerical columns
    numerical_cols = data_to_analyze.select_dtypes(include=['number']).columns
    if len(numerical_cols) > 0:
        context += f"\nNumerical Statistics:\n"
        for col in numerical_cols:
            if col not in ['Response_ID']:
                mean_val = data_to_analyze[col].mean()
                std_val = data_to_analyze[col].std()
                min_val = data_to_analyze[col].min()
                max_val = data_to_analyze[col].max()
                context += f"- {col}: mean={mean_val:.2f}, std={std_val:.2f}, range=[{min_val:.2f}, {max_val:.2f}]\n"
    
    # Add categorical summaries
    categorical_cols = data_to_analyze.select_dtypes(include=['object']).columns
    categorical_cols = [col for col in categorical_cols if col not in ['Timestamp', 'Response_ID']]
    if len(categorical_cols) > 0:
        context += f"\nCategorical Data:\n"
        for col in categorical_cols:
            top_values = data_to_analyze[col].value_counts().head(3)
            context += f"- {col}: Top values - {dict(top_values)}\n"
    
    # Add business context if available
    if st.session_state.get('business_problem'):
        context += f"\nBusiness Problem: {st.session_state.business_problem}\n"
    
    if st.session_state.get('variables'):
        context += f"\nKey Variables: {[var['name'] for var in st.session_state.variables]}\n"
    
    return context

# Update data context
st.session_state.data_context = create_data_context()

# Sidebar with data summary
with st.sidebar:
    st.header("Data Context")
    
    if data_to_analyze is not None and not data_to_analyze.empty:
        st.metric("Records", data_to_analyze.shape[0])
        st.metric("Variables", data_to_analyze.shape[1])
        
        # Show available columns
        st.subheader("Available Columns")
        for col in data_to_analyze.columns:
            col_type = str(data_to_analyze[col].dtype)
            if col_type == 'object':
                st.text(f"Data: {col}")
            elif col_type in ['int64', 'float64']:
                st.text(f"🔢 {col}")
            else:
                st.text(f"📅 {col}")
    else:
        st.warning("No data loaded")
        st.info("Load data from previous steps to get contextual responses.")
    
    # Business context
    if st.session_state.get('business_problem'):
        st.subheader("Business Problem")
        st.text_area(
            "Current Problem:",
            value=st.session_state.business_problem[:200] + "..." if len(st.session_state.business_problem) > 200 else st.session_state.business_problem,
            height=100,
            disabled=True
        )
    
    # Quick action buttons
    st.subheader("Quick Actions")
    
    if st.button("Summarize Data", use_container_width=True):
        if data_to_analyze is not None and not data_to_analyze.empty:
            summary_message = "Can you provide a comprehensive summary of my data including key patterns, distributions, and insights?"
            st.session_state.chat_history.append({
                "role": "user",
                "content": summary_message,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            st.rerun()
    
    if st.button("Identify Trends", use_container_width=True):
        trend_message = "What trends and patterns can you identify in my data? Please highlight the most significant findings."
        st.session_state.chat_history.append({
            "role": "user", 
            "content": trend_message,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        st.rerun()
    
    if st.button("💡 Get Recommendations", use_container_width=True):
        rec_message = "Based on my data analysis, what actionable recommendations do you have for addressing my business problem?"
        st.session_state.chat_history.append({
            "role": "user",
            "content": rec_message, 
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        st.rerun()
    
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Main chat interface
st.header("Chat Interface")

# Display chat history
chat_container = st.container()

with chat_container:
    if not st.session_state.chat_history:
        # Welcome message
        st.info("""
        👋 **Welcome to your AI Data Analysis Assistant!**
        
        I can help you with:
        - Data summaries and insights
        - Trend analysis and patterns
        - Statistical interpretations
        - 💡 Business recommendations
        - ❓ Answering specific questions about your data
        
        **Sample questions you can ask:**
        - "What are the key patterns in my data?"
        - "Which variables are most important?"
        - "What recommendations do you have based on this analysis?"
        - "How can I improve my data collection?"
        """)
    else:
        # Display chat messages
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
                    st.caption(f"Sent at {message['timestamp']}")
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    st.caption(f"Response at {message['timestamp']}")

# Process pending user messages
if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
    user_message = st.session_state.chat_history[-1]["content"]
    
    with st.spinner("AI is thinking..."):
        try:
            # Get AI response
            ai_response = st.session_state.groq_client.chat_response(
                user_message, 
                st.session_state.data_context
            )
            
            # Add AI response to chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error getting AI response: {str(e)}")
            # Add error message to chat
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try rephrasing your question or check your API connection.",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            st.rerun()

# Chat input
st.header("Ask a Question")

# Example questions
with st.expander("💡 Example Questions"):
    st.markdown("""
    **Data Analysis Questions:**
    - What are the main insights from my survey data?
    - Which responses show the strongest correlations?
    - What patterns emerge from the categorical responses?
    
    **Business Intelligence Questions:**
    - How can I improve customer satisfaction based on this data?
    - What are the key factors affecting my business metrics?
    - Which areas should I focus on for improvement?
    
    **Statistical Questions:**
    - Are there any outliers I should be concerned about?
    - What is the statistical significance of my findings?
    - How reliable are these results?
    
    **Predictive Questions:**
    - What trends should I expect to continue?
    - How might these patterns change in the future?
    - What scenarios should I plan for?
    """)

# Chat input form
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_area(
        "Ask me anything about your data:",
        placeholder="E.g., What are the key insights from my survey responses? How can I improve based on this data?",
        height=100
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        submit_button = st.form_submit_button("📤 Send", use_container_width=True)
    
    with col2:
        if st.form_submit_button("Generate Random Question", use_container_width=True):
            random_questions = [
                "What are the most significant patterns in my data?",
                "How does the data relate to my original business problem?",
                "What recommendations do you have for next steps?",
                "Are there any unexpected findings in the analysis?",
                "Which variables have the strongest relationships?",
                "What quality issues should I address in my data?",
                "How can I improve my data collection process?",
                "What predictions can you make based on current trends?"
            ]
            import random
            user_input = random.choice(random_questions)
            submit_button = True
    
    if submit_button and user_input.strip():
        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input.strip(),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        st.rerun()

# Chat statistics and export
if st.session_state.chat_history:
    st.header("Chat Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        user_messages = [msg for msg in st.session_state.chat_history if msg["role"] == "user"]
        st.metric("Questions Asked", len(user_messages))
    
    with col2:
        ai_messages = [msg for msg in st.session_state.chat_history if msg["role"] == "assistant"]
        st.metric("AI Responses", len(ai_messages))
    
    with col3:
        total_words = sum(len(msg["content"].split()) for msg in st.session_state.chat_history)
        st.metric("Total Words", total_words)
    
    with col4:
        if st.session_state.chat_history:
            first_time = st.session_state.chat_history[0]["timestamp"]
            last_time = st.session_state.chat_history[-1]["timestamp"]
            st.metric("Session Duration", f"{first_time} - {last_time}")
    
    # Export chat
    st.subheader("Download Export Chat")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download Chat Log", use_container_width=True):
            chat_log = f"# Chat Session - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            for message in st.session_state.chat_history:
                role = "User" if message["role"] == "user" else "AI Assistant"
                chat_log += f"## {role} ({message['timestamp']})\n"
                chat_log += f"{message['content']}\n\n"
            
            st.download_button(
                label="💾 Save Chat",
                data=chat_log,
                file_name=f"chat_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
    
    with col2:
        if st.button("Form Copy Last Response", use_container_width=True):
            if ai_messages:
                last_response = ai_messages[-1]["content"]
                st.code(last_response)
                st.success("Response copied! You can manually copy from the code block above.")

# Navigation and quick links
st.markdown("---")
st.header("Quick Navigation")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Main Page", use_container_width=True):
        st.switch_page("app.py")

with col2:
    if st.button("Dashboard", use_container_width=True):
        st.switch_page("pages/6_Dashboard.py")

with col3:
    if st.button("Analysis", use_container_width=True):
        st.switch_page("pages/5_Analysis.py")

with col4:
    if st.button("Data Collection", use_container_width=True):
        st.switch_page("pages/3_Data_Collection.py")

# Footer with tips
st.markdown("---")
st.markdown("""
**💡 Pro Tips:**
- Be specific in your questions for better responses
- Reference specific column names or data points when asking questions
- Ask follow-up questions to dive deeper into insights
- Use the quick action buttons in the sidebar for common queries
""")
