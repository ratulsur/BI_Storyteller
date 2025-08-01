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
        
        IMPORTANT RULES:
        1. Every "select" or "multiselect" question MUST include an "options" array with at least 3-5 options
        2. Create a mix of question types to gather comprehensive data
        3. Include 8-12 questions total for thorough data collection
        4. Use clear, specific question text
        
        Question types: 'text', 'number', 'select', 'multiselect', 'date', 'boolean'
        
        Required format:
        {{
            "title": "Data Collection Survey",
            "description": "Help us gather data to analyze your business problem",
            "questions": [
                {{
                    "question_text": "How satisfied are you with our service?",
                    "question_type": "select",
                    "options": ["Very Dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very Satisfied"],
                    "required": true
                }},
                {{
                    "question_text": "Which features do you use most?",
                    "question_type": "multiselect",
                    "options": ["Feature A", "Feature B", "Feature C", "Feature D"],
                    "required": false
                }},
                {{
                    "question_text": "Additional comments",
                    "question_type": "text",
                    "required": false
                }}
            ]
        }}
        
        CRITICAL: Every select/multiselect question MUST have valid options array!
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
            
            # Post-process to fix any missing options for select/multiselect questions
            questionnaire = self._fix_questionnaire_options(questionnaire)
            
            return questionnaire
        except Exception as e:
            st.error(f"Error generating questionnaire: {str(e)}")
            return {}
    
    def _fix_questionnaire_options(self, questionnaire):
        """Fix questionnaire by adding default options to select/multiselect questions that are missing them"""
        if not questionnaire or 'questions' not in questionnaire:
            return questionnaire
        
        default_options_map = {
            'satisfaction': ["Very Dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very Satisfied"],
            'frequency': ["Never", "Rarely", "Sometimes", "Often", "Always"],
            'quality': ["Poor", "Below Average", "Average", "Good", "Excellent"],
            'importance': ["Not Important", "Slightly Important", "Moderately Important", "Very Important", "Extremely Important"],
            'agreement': ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
            'rating': ["1 - Poor", "2 - Fair", "3 - Good", "4 - Very Good", "5 - Excellent"],
            'experience': ["Very Negative", "Negative", "Neutral", "Positive", "Very Positive"],
            'likelihood': ["Very Unlikely", "Unlikely", "Neutral", "Likely", "Very Likely"],
            'size': ["Small", "Medium", "Large", "Very Large"],
            'duration': ["Less than 1 month", "1-3 months", "3-6 months", "6-12 months", "More than 1 year"],
            'category': ["Category A", "Category B", "Category C", "Category D", "Other"]
        }
        
        for i, question in enumerate(questionnaire['questions']):
            if question.get('question_type') in ['select', 'multiselect']:
                if 'options' not in question or not question['options']:
                    # Try to determine appropriate options based on question text
                    question_text = question.get('question_text', '').lower()
                    
                    # Find the best matching default options
                    best_options = None
                    for keyword, options in default_options_map.items():
                        if keyword in question_text:
                            best_options = options
                            break
                    
                    # If no match found, use generic options based on question type
                    if not best_options:
                        if 'satisfy' in question_text or 'satisfaction' in question_text:
                            best_options = default_options_map['satisfaction']
                        elif 'rate' in question_text or 'rating' in question_text:
                            best_options = default_options_map['rating']
                        elif 'agree' in question_text or 'opinion' in question_text:
                            best_options = default_options_map['agreement']
                        elif 'experience' in question_text:
                            best_options = default_options_map['experience']
                        elif 'quality' in question_text:
                            best_options = default_options_map['quality']
                        elif 'important' in question_text:
                            best_options = default_options_map['importance']
                        elif 'often' in question_text or 'frequency' in question_text:
                            best_options = default_options_map['frequency']
                        elif 'likely' in question_text:
                            best_options = default_options_map['likelihood']
                        else:
                            # Generic fallback options
                            best_options = ["Option 1", "Option 2", "Option 3", "Option 4", "Other"]
                    
                    question['options'] = best_options
                    
        return questionnaire

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
