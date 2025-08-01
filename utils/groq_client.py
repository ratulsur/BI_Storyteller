import os
import json
from groq import Groq
import streamlit as st

class GroqClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        if not self.api_key:
            st.error("Groq API key not found. Please set GROQ_API_KEY environment variable.")
            return
        
        try:
            self.client = Groq(api_key=self.api_key)
        except Exception as e:
            st.error(f"Failed to initialize Groq client: {str(e)}")
            self.client = None

    def extract_variables(self, business_problem):
        """Extract key variables from business problem"""
        if not self.client:
            return []
        
        prompt = f"""
        Analyze the following business problem and extract key variables that would be important to collect data about.
        Return ONLY a JSON array of variables, where each variable is an object with 'name', 'type', and 'description' fields.
        
        Variable types should be one of: 'categorical', 'numerical', 'text', 'date', 'boolean'
        
        Business Problem: {business_problem}
        
        Example format:
        [
            {{"name": "customer_satisfaction_score", "type": "numerical", "description": "Customer satisfaction rating from 1-10"}},
            {{"name": "product_category", "type": "categorical", "description": "Category of purchased product"}},
            {{"name": "purchase_date", "type": "date", "description": "Date when purchase was made"}}
        ]
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            # Clean up the response to extract JSON
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            
            variables = json.loads(content)
            return variables
        except Exception as e:
            st.error(f"Error extracting variables: {str(e)}")
            return []

    def generate_questionnaire(self, business_problem, variables):
        """Generate questionnaire based on business problem and variables"""
        if not self.client:
            return {}
        
        variables_text = "\n".join([f"- {var['name']}: {var['description']} (Type: {var['type']})" for var in variables])
        
        prompt = f"""
        Create a comprehensive questionnaire to collect data for this business problem.
        Return ONLY a JSON object with the questionnaire structure.
        
        Business Problem: {business_problem}
        
        Key Variables to Address:
        {variables_text}
        
        The questionnaire should have:
        1. A title
        2. A description
        3. Questions array with each question having: question_text, question_type, options (if applicable), required (boolean)
        
        Question types: 'text', 'number', 'select', 'multiselect', 'date', 'boolean'
        
        Example format:
        {{
            "title": "Customer Satisfaction Survey",
            "description": "Help us understand factors affecting customer satisfaction",
            "questions": [
                {{
                    "question_text": "How satisfied are you with our service?",
                    "question_type": "select",
                    "options": ["Very Dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very Satisfied"],
                    "required": true
                }},
                {{
                    "question_text": "Additional comments",
                    "question_type": "text",
                    "required": false
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            # Clean up the response
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            
            questionnaire = json.loads(content)
            return questionnaire
        except Exception as e:
            st.error(f"Error generating questionnaire: {str(e)}")
            return {}

    def analyze_data(self, data_summary, analysis_type="general"):
        """Analyze data and provide insights"""
        if not self.client:
            return ""
        
        prompt = f"""
        Analyze the following data summary and provide insights.
        Focus on {analysis_type} analysis.
        
        Data Summary:
        {data_summary}
        
        Provide actionable insights, patterns, and recommendations.
        Format your response in clear sections with bullet points.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Error analyzing data: {str(e)}")
            return ""

    def chat_response(self, user_message, context=""):
        """Generate chat response based on user message and context"""
        if not self.client:
            return "Sorry, I'm unable to process your request at the moment."
        
        prompt = f"""
        You are an AI data analyst assistant. Answer the user's question based on the provided context.
        Be helpful, accurate, and provide actionable insights when possible.
        
        Context: {context}
        
        User Question: {user_message}
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def generate_predictions(self, data_summary):
        """Generate predictions based on data analysis"""
        if not self.client:
            return ""
        
        prompt = f"""
        Based on the following data analysis, generate predictions and forecasts.
        Focus on trends, future outcomes, and potential scenarios.
        
        Data Summary:
        {data_summary}
        
        Provide:
        1. Short-term predictions (next 1-3 months)
        2. Long-term forecasts (6-12 months)
        3. Key factors that might influence outcomes
        4. Risk factors and mitigation strategies
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Error generating predictions: {str(e)}")
            return ""
