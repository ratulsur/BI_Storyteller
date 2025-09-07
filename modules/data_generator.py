"""
Data Generator Module
Generates realistic sample data for questionnaire responses
"""

import random
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta


class DataGenerator:
    """Generate sample survey response data"""
    
    def __init__(self):
        # Response patterns for realistic data generation
        self.response_patterns = {
            'age': {
                '18-25': 0.20,
                '26-35': 0.25,
                '36-45': 0.20,
                '46-55': 0.15,
                '56-65': 0.12,
                '65+': 0.08
            },
            'gender': {
                'Male': 0.48,
                'Female': 0.50,
                'Non-binary': 0.015,
                'Prefer not to say': 0.005
            },
            'satisfaction': {
                'Very Satisfied': 0.15,
                'Satisfied': 0.35,
                'Neutral': 0.25,
                'Dissatisfied': 0.15,
                'Very Dissatisfied': 0.10
            },
            'frequency': {
                'Daily': 0.10,
                'Weekly': 0.25,
                'Monthly': 0.30,
                'Rarely': 0.25,
                'Never': 0.10
            }
        }
        
        # Correlation patterns for realistic responses
        self.correlations = {
            ('age', '18-25'): {'frequency': {'Daily': 0.2, 'Weekly': 0.4}},
            ('age', '65+'): {'frequency': {'Rarely': 0.4, 'Never': 0.3}},
            ('satisfaction', 'Very Satisfied'): {'rating': {'Excellent': 0.8}},
            ('satisfaction', 'Very Dissatisfied'): {'rating': {'Poor': 0.4, 'Very Poor': 0.4}}
        }
    
    def generate_sample_data(self, questionnaire: List[Dict[str, Any]], num_responses: int = 1000) -> List[Dict[str, Any]]:
        """Generate sample responses for the questionnaire"""
        responses = []
        
        for i in range(num_responses):
            response = {
                'response_id': f"R{i+1:06d}",
                'timestamp': self._generate_timestamp(),
                'answers': {}
            }
            
            # Generate correlated responses
            demographic_context = {}
            
            for j, question in enumerate(questionnaire):
                question_id = f"Q{j+1}"
                
                if question['type'] == 'MCQ':
                    answer = self._generate_mcq_response(question, demographic_context)
                    
                    # Store demographic context for correlations
                    if question['category'] == 'demographic':
                        demographic_context[question['category']] = answer
                
                elif question['type'] == 'Descriptive':
                    answer = self._generate_descriptive_response(question, demographic_context)
                
                response['answers'][question_id] = {
                    'question': question['question'],
                    'answer': answer,
                    'question_type': question['type'],
                    'category': question.get('category', 'general')
                }
            
            responses.append(response)
        
        return responses
    
    def _generate_timestamp(self) -> str:
        """Generate realistic timestamp for responses"""
        # Generate timestamps over the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Random time between start and end
        time_diff = end_date - start_date
        random_seconds = random.randint(0, int(time_diff.total_seconds()))
        random_time = start_date + timedelta(seconds=random_seconds)
        
        return random_time.isoformat()
    
    def _generate_mcq_response(self, question: Dict[str, Any], context: Dict[str, str]) -> str:
        """Generate MCQ response with realistic distribution"""
        options = question['options']
        category = question.get('category', 'general')
        
        # Use predefined patterns if available
        if category in self.response_patterns:
            pattern = self.response_patterns[category]
            # Filter options that exist in the question
            valid_options = {opt: weight for opt, weight in pattern.items() if opt in options}
            
            if valid_options:
                return self._weighted_choice(valid_options)
        
        # Check for correlations
        correlated_response = self._get_correlated_response(question, context)
        if correlated_response:
            return correlated_response
        
        # Default: random choice
        return random.choice(options)
    
    def _generate_descriptive_response(self, question: Dict[str, Any], context: Dict[str, str]) -> str:
        """Generate realistic descriptive responses"""
        category = question.get('category', 'general')
        question_text = question['question'].lower()
        
        # Response templates based on question category
        response_templates = {
            'feedback': [
                "The service could be improved in terms of response time.",
                "Overall satisfied with the experience, but pricing could be better.",
                "Great quality products, would recommend to others.",
                "Customer support was very helpful and professional.",
                "The interface is user-friendly and intuitive."
            ],
            'experience': [
                "I have been using this for about 2 years now.",
                "My experience has been mostly positive with some minor issues.",
                "Started using recently, still learning the features.",
                "Very experienced user, have tried many alternatives.",
                "New to this, but finding it quite useful so far."
            ],
            'motivation': [
                "Primarily motivated by cost-effectiveness and quality.",
                "Need this for work-related projects and tasks.",
                "Personal interest and hobby purposes.",
                "Recommended by friends and colleagues.",
                "Looking for better alternatives to current solution."
            ],
            'factors': [
                "Price, quality, and customer reviews are main factors.",
                "Brand reputation and warranty terms matter most.",
                "Ease of use and customer support availability.",
                "Features offered and compatibility with existing tools.",
                "Delivery time and return policy considerations."
            ]
        }
        
        # Generate response based on category
        if category in response_templates:
            base_response = random.choice(response_templates[category])
            
            # Add variation based on context
            if 'age' in context:
                age_group = context['age']
                if age_group in ['18-25', '26-35']:
                    base_response += " Tech-savvy approach is important."
                elif age_group in ['56-65', '65+']:
                    base_response += " Simplicity and reliability are key."
        
        elif 'satisfaction' in question_text or 'rating' in question_text:
            return random.choice(response_templates['feedback'])
        elif 'experience' in question_text or 'familiar' in question_text:
            return random.choice(response_templates['experience'])
        elif 'motivate' in question_text or 'influence' in question_text:
            return random.choice(response_templates['motivation'])
        elif 'factor' in question_text or 'important' in question_text:
            return random.choice(response_templates['factors'])
        else:
            # Generic responses
            generic_responses = [
                "This is an important consideration for my decision-making process.",
                "I believe this aspect significantly impacts the overall value proposition.",
                "From my perspective, this plays a crucial role in user satisfaction.",
                "This factor should definitely be taken into account moving forward.",
                "In my opinion, this area has room for improvement and optimization."
            ]
            base_response = random.choice(generic_responses)
        
        # Add length variation
        if random.random() < 0.3:  # 30% chance for shorter response
            return base_response.split('.')[0] + '.'
        elif random.random() < 0.2:  # 20% chance for longer response
            additional = " I think this could lead to better outcomes in the future."
            return base_response + additional
        
        return base_response
    
    def _weighted_choice(self, choices: Dict[str, float]) -> str:
        """Make weighted random choice"""
        total = sum(choices.values())
        r = random.uniform(0, total)
        
        cumulative = 0
        for choice, weight in choices.items():
            cumulative += weight
            if r <= cumulative:
                return choice
        
        return list(choices.keys())[0]  # Fallback
    
    def _get_correlated_response(self, question: Dict[str, Any], context: Dict[str, str]) -> str:
        """Get correlated response based on previous answers"""
        for (context_key, context_value), correlations in self.correlations.items():
            if context_key in context and context[context_key] == context_value:
                question_category = question.get('category', '')
                
                if question_category in correlations:
                    correlation_pattern = correlations[question_category]
                    # Filter valid options
                    valid_options = {opt: weight for opt, weight in correlation_pattern.items() 
                                   if opt in question.get('options', [])}
                    
                    if valid_options and random.random() < 0.7:  # 70% chance to use correlation
                        return self._weighted_choice(valid_options)
        
        return None
    
    def add_data_quality_issues(self, data: List[Dict[str, Any]], 
                              missing_rate: float = 0.02, 
                              inconsistency_rate: float = 0.01) -> List[Dict[str, Any]]:
        """Add realistic data quality issues for cleaning demonstration"""
        modified_data = []
        
        for response in data:
            new_response = response.copy()
            
            # Add missing values
            if random.random() < missing_rate:
                # Skip one random answer
                answers_keys = list(new_response['answers'].keys())
                if answers_keys:
                    skip_key = random.choice(answers_keys)
                    new_response['answers'][skip_key]['answer'] = None
            
            # Add inconsistencies
            if random.random() < inconsistency_rate:
                # Modify answer format slightly
                answers_keys = list(new_response['answers'].keys())
                if answers_keys:
                    modify_key = random.choice(answers_keys)
                    answer = new_response['answers'][modify_key]['answer']
                    if isinstance(answer, str) and answer:
                        # Add extra spaces or case variations
                        if random.random() < 0.5:
                            new_response['answers'][modify_key]['answer'] = f"  {answer}  "
                        else:
                            new_response['answers'][modify_key]['answer'] = answer.upper()
            
            modified_data.append(new_response)
        
        return modified_data
    
    def generate_time_series_data(self, base_data: List[Dict[str, Any]], 
                                periods: int = 12) -> Dict[str, List[Dict[str, Any]]]:
        """Generate time series data for trend analysis"""
        time_series = {}
        
        # Generate monthly data
        current_date = datetime.now()
        
        for i in range(periods):
            month_date = current_date - timedelta(days=30 * i)
            month_key = month_date.strftime("%Y-%m")
            
            # Generate data for this month with some variation
            month_responses = []
            num_responses = random.randint(50, 150)  # Varying monthly responses
            
            for j in range(num_responses):
                # Use base structure but with temporal variation
                response = random.choice(base_data).copy()
                response['response_id'] = f"{month_key}-R{j+1:04d}"
                response['timestamp'] = month_date.isoformat()
                
                month_responses.append(response)
            
            time_series[month_key] = month_responses
        
        return time_series