# Overview

BI StoryTeller is an AI-powered data analysis platform built with Streamlit that enables users to conduct comprehensive data analysis through a guided workflow. The platform starts with business problem definition, automatically extracts relevant variables, generates custom questionnaires, collects data via Google Sheets integration, processes and analyzes the data, and presents insights through interactive dashboards and AI chat assistance.

The application follows a step-by-step methodology: problem definition → variable extraction → questionnaire generation → data collection → preprocessing → analysis → dashboard visualization → AI-powered chat insights. Each step builds upon the previous one, creating a seamless end-to-end data analysis pipeline.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit with multi-page architecture using pages/ directory structure
- **Navigation**: Page-based workflow with sequential progression (app.py → 7 specialized pages)
- **State Management**: Streamlit session state for maintaining user context across pages including business problems, variables, questionnaires, data, and analysis results
- **UI Components**: Wide layout with sidebar navigation, interactive forms, real-time metrics, and responsive columns

## Backend Architecture
- **Core Processing**: Modular utility classes in utils/ directory for separated concerns
- **AI Integration**: GroqClient for LLM-powered variable extraction, questionnaire generation, and chat assistance using Llama models
- **Database Layer**: DatabaseClient handles PostgreSQL connections, table creation, and data operations
- **Form Engine**: FormGenerator creates interactive Streamlit forms with database integration
- **Data Pipeline**: DataProcessor handles cleaning, preprocessing, outlier removal, normalization, and encoding
- **Visualization Engine**: Visualizer creates interactive plots using Plotly for distributions, correlations, and statistical charts

## Data Storage Solutions
- **Primary Collection**: PostgreSQL database integration for questionnaire responses with automatic table creation
- **Interactive Forms**: Streamlit-based forms with real-time validation and database storage
- **Session Storage**: Streamlit session state for temporary data persistence during user sessions
- **Data Formats**: Pandas DataFrames for in-memory data manipulation and analysis
- **Legacy Support**: Google Sheets integration via gspread (alternative collection method)
- **File Support**: CSV/JSON upload/download capabilities for data import/export

## Authentication and Authorization
- **Google Sheets Access**: Service account credentials via environment variables or Streamlit secrets
- **API Authentication**: Groq API key management through environment variables
- **Access Control**: Public Google Sheets sharing for questionnaire form submissions

## External Service Integrations
- **Groq AI**: LLM API for natural language processing, variable extraction, and conversational AI
- **Google Sheets API**: Real-time data collection and storage for survey responses
- **Google Drive API**: Document management and sharing for questionnaire deployment

The architecture emphasizes modularity with clear separation between AI processing, data handling, visualization, and external integrations, enabling easy maintenance and feature expansion.

# External Dependencies

## AI and Machine Learning
- **Groq**: Primary LLM service for variable extraction, questionnaire generation, and chat assistance
- **TextBlob**: Natural language processing for sentiment analysis and text processing
- **scikit-learn**: Machine learning utilities for data preprocessing, scaling, and statistical analysis
- **scipy**: Statistical analysis and hypothesis testing

## Data Processing and Visualization
- **pandas**: Data manipulation and analysis framework
- **numpy**: Numerical computing and array operations
- **plotly**: Interactive visualization library for charts, graphs, and dashboards
- **matplotlib/seaborn**: Additional plotting capabilities for statistical visualizations

## Google Cloud Integration
- **gspread**: Google Sheets API client for spreadsheet operations
- **google-auth**: Authentication library for Google service account credentials
- **Google Sheets API**: Real-time data collection and response storage
- **Google Drive API**: File sharing and permission management

## Web Framework
- **streamlit**: Core web application framework providing the user interface and hosting platform

## Development Tools
- **python-dotenv**: Environment variable management for API keys and configuration
- **json**: Configuration and data serialization for API responses and questionnaire structures

The platform requires active API keys for Groq AI services and Google Cloud service account credentials for Sheets integration. All external dependencies are configured through environment variables for security and deployment flexibility.