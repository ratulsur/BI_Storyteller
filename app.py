import streamlit as st
import os
from utils.groq_client import GroqClient
from utils.sheets_client import SheetsClient
from utils.data_processor import DataProcessor
from utils.visualizer import Visualizer
from utils.database_client import DatabaseClient
from utils.form_generator import FormGenerator

# Page configuration
st.set_page_config(
    page_title="BI StoryTeller",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'business_problem' not in st.session_state:
    st.session_state.business_problem = ""
if 'variables' not in st.session_state:
    st.session_state.variables = []
if 'questionnaire' not in st.session_state:
    st.session_state.questionnaire = {}
if 'questionnaire_approved' not in st.session_state:
    st.session_state.questionnaire_approved = False
if 'questionnaire_link' not in st.session_state:
    st.session_state.questionnaire_link = ""
if 'raw_data' not in st.session_state:
    st.session_state.raw_data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

# Initialize clients
@st.cache_resource
def init_clients():
    groq_client = GroqClient(api_key=os.getenv("GROQ_API_KEY", ""))
    sheets_client = SheetsClient()
    db_client = DatabaseClient()
    form_generator = FormGenerator()
    return groq_client, sheets_client, db_client, form_generator

try:
    groq_client, sheets_client, db_client, form_generator = init_clients()
    st.session_state.groq_client = groq_client
    st.session_state.sheets_client = sheets_client
    st.session_state.db_client = db_client
    st.session_state.form_generator = form_generator
except Exception as e:
    st.error(f"Failed to initialize clients: {str(e)}")
    st.stop()

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .stSelectbox > div > div {
        background-color: #262730;
        border: 1px solid #404040;
    }
    .stButton > button {
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(31, 119, 180, 0.3);
    }
    .metric-card {
        background-color: #262730;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .professional-card {
        background-color: #1a1a1a;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #333;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Main page
st.markdown('<div class="main-header"><h1 style="margin:0; color:white;">BI StoryTeller</h1><p style="margin:0.5rem 0 0 0; color:white;">Transform your business problems into actionable insights through AI-powered analysis</p></div>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("Follow the workflow step by step:")

workflow_steps = [
    "1. Variables",
    "2. Questionnaire", 
    "3. Data Collection",
    "4. Data Preprocessing",
    "5. Analysis",
    "6. Dashboard",
    "7. Chat"
]

for step in workflow_steps:
    st.sidebar.markdown(step)

# Business problem input
st.header("Business Problem")
st.markdown("Describe your business challenge or problem that you want to analyze:")

business_problem = st.text_area(
    "Business Problem Description",
    value=st.session_state.business_problem,
    height=150,
    placeholder="Example: Our e-commerce company is experiencing declining customer satisfaction scores over the past 6 months. We need to understand the factors contributing to this decline and identify areas for improvement."
)

if business_problem != st.session_state.business_problem:
    st.session_state.business_problem = business_problem
    # Reset downstream states when business problem changes
    st.session_state.variables = []
    st.session_state.questionnaire = {}
    st.session_state.questionnaire_approved = False
    st.session_state.questionnaire_link = ""
    st.session_state.raw_data = None
    st.session_state.processed_data = None
    st.session_state.analysis_results = {}

# Progress indicator
st.header("Workflow Progress")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.session_state.business_problem:
        st.success("Problem Defined")
    else:
        st.info("Define Problem")

with col2:
    if st.session_state.variables:
        st.success("Variables Extracted")
    else:
        st.info("Extract Variables")

with col3:
    if st.session_state.questionnaire_approved:
        st.success("Questionnaire Approved")
    else:
        st.info("Create Questionnaire")

with col4:
    if st.session_state.raw_data is not None:
        st.success("Data Collected")
    else:
        st.info("Collect Data")

# Quick actions
st.header("Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Extract Variables", disabled=not st.session_state.business_problem):
        st.switch_page("pages/1_Variables.py")

with col2:
    if st.button("Create Questionnaire", disabled=not st.session_state.variables):
        st.switch_page("pages/2_Questionnaire.py")

with col3:
    if st.button("Start Chat", disabled=not st.session_state.business_problem):
        st.switch_page("pages/7_Chat.py")

# Instructions
st.header("📖 How to Use")
st.markdown("""
1. **Define Problem**: Describe your business problem in detail
2. **Extract Variables**: AI will identify key variables from your problem
3. **Create Questionnaire**: Generate targeted questions to collect relevant data
4. **Collect Data**: Share the questionnaire link and gather responses
5. **Preprocess Data**: Clean and prepare your data for analysis
6. **Analyze Data**: Generate comprehensive insights and visualizations
7. **View Dashboard**: Explore trends, sentiments, and predictions
8. **Chat Interface**: Ask specific questions about your data and insights
""")

# Footer
st.markdown("---")
st.markdown("*Powered by Groq AI and Google Sheets*")
