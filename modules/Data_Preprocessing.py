"""
Data Cleaner Module
Comprehensive data cleaning and balancing for survey responses
"""

import json
import re
from typing import List, Dict, Any, Optional
from collections import Counter


class DataCleaner:
    """Clean and balance survey response data"""
    
    def __init__(self):
        self.cleaning_stats = {
            'original_count': 0,
            'removed_duplicates': 0,
            'fixed_missing_values': 0,
            'standardized_responses': 0,
            'removed_outliers': 0,
            'balanced_groups': 0
        }
    
    def clean_and_balance(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Main cleaning and balancing pipeline"""
        self.cleaning_stats['original_count'] = len(raw_data)
        
        print("🧹 Starting data cleaning process...")
        
        # Step 1: Remove duplicates
        cleaned_data = self._remove_duplicates(raw_data)
        print(f"   ✓ Removed {self.cleaning_stats['removed_duplicates']} duplicates")
        
        # Step 2: Handle missing values
        cleaned_data = self._handle_missing_values(cleaned_data)
        print(f"   ✓ Fixed {self.cleaning_stats['fixed_missing_values']} missing values")
        
        # Step 3: Standardize responses
        cleaned_data = self._standardize_responses(cleaned_data)
        print(f"   ✓ Standardized {self.cleaning_stats['standardized_responses']} responses")
        
        # Step 4: Remove outliers
        cleaned_data = self._remove_outliers(cleaned_data)
        print(f"   ✓ Removed {self.cleaning_stats['removed_outliers']} outlier responses")
        
        # Step 5: Balance data
        cleaned_data = self._balance_data(cleaned_data)
        print(f"   ✓ Balanced {self.cleaning_stats['balanced_groups']} demographic groups")
        
        # Step 6: Validate data quality
        quality_score = self._validate_data_quality(cleaned_data)
        print(f"   ✓ Data quality score: {quality_score:.1f}%")
        
        return cleaned_data
    
    def _remove_duplicates(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate responses based on answer patterns"""
        seen_patterns = set()
        unique_data = []
        
        for response in data:
            # Create a pattern from answers for duplicate detection
            answers = response.get('answers', {})
            pattern_parts = []
            
            for q_id, answer_data in sorted(answers.items()):
                answer = answer_data.get('answer', '')
                if answer:
                    pattern_parts.append(str(answer).strip().lower())
            
            pattern = '|'.join(pattern_parts)
            
            if pattern not in seen_patterns:
                seen_patterns.add(pattern)
                unique_data.append(response)
            else:
                self.cleaning_stats['removed_duplicates'] += 1
        
        return unique_data
    
    def _handle_missing_values(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Handle missing values using various imputation strategies"""
        # Analyze missing patterns first
        missing_patterns = self._analyze_missing_patterns(data)
        
        for response in data:
            answers = response.get('answers', {})
            
            for q_id, answer_data in answers.items():
                if answer_data.get('answer') is None or answer_data.get('answer') == '':
                    # Impute based on question type and category
                    imputed_value = self._impute_missing_value(answer_data, missing_patterns)
                    if imputed_value:
                        answer_data['answer'] = imputed_value
                        answer_data['imputed'] = True
                        self.cleaning_stats['fixed_missing_values'] += 1
        
        return data
    
    def _analyze_missing_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in missing data"""
        question_stats = {}
        
        for response in data:
            answers = response.get('answers', {})
            
            for q_id, answer_data in answers.items():
                if q_id not in question_stats:
                    question_stats[q_id] = {
                        'total': 0,
                        'missing': 0,
                        'values': Counter(),
                        'category': answer_data.get('category', 'general'),
                        'question_type': answer_data.get('question_type', 'unknown')
                    }
                
                question_stats[q_id]['total'] += 1
                
                if answer_data.get('answer') is None or answer_data.get('answer') == '':
                    question_stats[q_id]['missing'] += 1
                else:
                    question_stats[q_id]['values'][str(answer_data['answer'])] += 1
        
        return question_stats
    
    def _impute_missing_value(self, answer_data: Dict[str, Any], patterns: Dict[str, Any]) -> Optional[str]:
        """Impute missing value based on question characteristics"""
        category = answer_data.get('category', 'general')
        question_type = answer_data.get('question_type', 'unknown')
        
        # Find corresponding question stats
        question_stats = None
        for q_id, stats in patterns.items():
            if (stats['category'] == category and 
                stats['question_type'] == question_type and 
                stats['values']):
                question_stats = stats
                break
        
        if not question_stats or not question_stats['values']:
            return None
        
        # Imputation strategies
        if question_type == 'MCQ':
            # Use most common response for MCQ
            most_common = question_stats['values'].most_common(1)
            return most_common[0][0] if most_common else None
        
        elif question_type == 'Descriptive':
            # Use category-appropriate default responses
            default_responses = {
                'feedback': "No specific feedback provided.",
                'experience': "Limited experience with this topic.",
                'motivation': "Standard considerations apply.",
                'factors': "Multiple factors influence this decision.",
                'additional': "No additional comments."
            }
            return default_responses.get(category, "No response provided.")
        
        return None
    
    def _standardize_responses(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Standardize response formats and values"""
        for response in data:
            answers = response.get('answers', {})
            
            for q_id, answer_data in answers.items():
                answer = answer_data.get('answer')
                if answer and isinstance(answer, str):
                    original_answer = answer
                    
                    # Standardize text responses
                    answer = answer.strip()  # Remove whitespace
                    answer = re.sub(r'\s+', ' ', answer)  # Normalize spaces
                    
                    # Standardize common variations
                    standardizations = {
                        # Age groups
                        r'\b(18|19|20|21|22|23|24|25)\b': '18-25',
                        r'\b(26|27|28|29|30|31|32|33|34|35)\b': '26-35',
                        
                        # Yes/No variations
                        r'\b(yes|yeah|yep|y)\b': 'Yes',
                        r'\b(no|nope|n)\b': 'No',
                        
                        # Satisfaction levels
                        r'\b(very\s*satisfied|excellent)\b': 'Very Satisfied',
                        r'\b(satisfied|good)\b': 'Satisfied',
                        r'\b(neutral|okay|ok|average)\b': 'Neutral',
                        r'\b(dissatisfied|poor)\b': 'Dissatisfied',
                        r'\b(very\s*dissatisfied|terrible|awful)\b': 'Very Dissatisfied'
                    }
                    
                    for pattern, replacement in standardizations.items():
                        if re.search(pattern, answer, re.IGNORECASE):
                            answer = replacement
                            break
                    
                    if answer != original_answer:
                        answer_data['answer'] = answer
                        answer_data['standardized'] = True
                        self.cleaning_stats['standardized_responses'] += 1
        
        return data
    
    def _remove_outliers(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove outlier responses based on response patterns"""
        outliers_removed = []
        
        for response in data:
            is_outlier = False
            
            # Check for response time outliers (if timestamp available)
            if 'timestamp' in response:
                # This is a placeholder - in real implementation, 
                # you'd analyze response times
                pass
            
            # Check for response length outliers in descriptive questions
            descriptive_lengths = []
            answers = response.get('answers', {})
            
            for q_id, answer_data in answers.items():
                if (answer_data.get('question_type') == 'Descriptive' and 
                    answer_data.get('answer')):
                    length = len(str(answer_data['answer']))
                    descriptive_lengths.append(length)
            
            # Flag as outlier if responses are extremely short or long
            if descriptive_lengths:
                avg_length = sum(descriptive_lengths) / len(descriptive_lengths)
                if avg_length < 10 or avg_length > 500:  # Too short or too long
                    is_outlier = True
            
            # Check for nonsensical response patterns
            answer_texts = []
            for q_id, answer_data in answers.items():
                if answer_data.get('answer'):
                    answer_texts.append(str(answer_data['answer']).lower())
            
            # Flag responses with too many repeated characters
            for text in answer_texts:
                if len(text) > 20 and len(set(text)) / len(text) < 0.3:
                    is_outlier = True
                    break
            
            if not is_outlier:
                outliers_removed.append(response)
            else:
                self.cleaning_stats['removed_outliers'] += 1
        
        return outliers_removed
    
    def _balance_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Balance demographic groups for fair representation"""
        # Analyze demographic distribution
        demographic_dist = self._analyze_demographics(data)
        
        # Identify underrepresented groups
        target_sizes = self._calculate_target_sizes(demographic_dist)
        
        # Balance by sampling
        balanced_data = self._sample_for_balance(data, target_sizes)
        
        return balanced_data
    
    def _analyze_demographics(self, data: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        """Analyze demographic distribution in the data"""
        demographics = {}
        
        for response in data:
            answers = response.get('answers', {})
            
            for q_id, answer_data in answers.items():
                if answer_data.get('category') == 'demographic':
                    question = answer_data.get('question', '').lower()
                    answer = answer_data.get('answer', '')
                    
                    # Identify demographic type
                    demo_type = 'other'
                    if 'age' in question:
                        demo_type = 'age'
                    elif 'gender' in question:
                        demo_type = 'gender'
                    elif 'income' in question:
                        demo_type = 'income'
                    elif 'education' in question:
                        demo_type = 'education'
                    
                    if demo_type not in demographics:
                        demographics[demo_type] = Counter()
                    
                    demographics[demo_type][str(answer)] += 1
        
        return demographics
    
    def _calculate_target_sizes(self, demographics: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, int]]:
        """Calculate target sizes for balanced representation"""
        targets = {}
        
        for demo_type, distribution in demographics.items():
            total = sum(distribution.values())
            if total == 0:
                continue
            
            # Aim for more balanced distribution
            num_categories = len(distribution)
            target_per_category = max(20, total // (num_categories * 2))  # Minimum 20 per category
            
            targets[demo_type] = {}
            for category in distribution.keys():
                targets[demo_type][category] = min(target_per_category, distribution[category])
        
        return targets
    
    def _sample_for_balance(self, data: List[Dict[str, Any]], 
                          targets: Dict[str, Dict[str, int]]) -> List[Dict[str, Any]]:
        """Sample data to achieve demographic balance"""
        # Group responses by demographics
        demographic_groups = self._group_by_demographics(data)
        
        balanced_data = []
        
        # Sample from each group according to targets
        for demo_key, group_data in demographic_groups.items():
            # Parse demographic key
            demo_info = self._parse_demo_key(demo_key)
            
            # Determine sample size
            sample_size = len(group_data)
            for demo_type, demo_value in demo_info.items():
                if demo_type in targets and demo_value in targets[demo_type]:
                    target_size = targets[demo_type][demo_value]
                    sample_size = min(sample_size, target_size)
            
            # Sample from this group
            if sample_size > 0:
                import random
                sampled = random.sample(group_data, min(sample_size, len(group_data)))
                balanced_data.extend(sampled)
                
                if len(sampled) < len(group_data):
                    self.cleaning_stats['balanced_groups'] += 1
        
        return balanced_data
    
    def _group_by_demographics(self, data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group responses by demographic characteristics"""
        groups = {}
        
        for response in data:
            # Extract demographic info
            demo_info = {}
            answers = response.get('answers', {})
            
            for q_id, answer_data in answers.items():
                if answer_data.get('category') == 'demographic':
                    question = answer_data.get('question', '').lower()
                    answer = answer_data.get('answer', '')
                    
                    if 'age' in question:
                        demo_info['age'] = str(answer)
                    elif 'gender' in question:
                        demo_info['gender'] = str(answer)
                    elif 'income' in question:
                        demo_info['income'] = str(answer)
            
            # Create group key
            demo_key = '|'.join([f"{k}:{v}" for k, v in sorted(demo_info.items())])
            
            if demo_key not in groups:
                groups[demo_key] = []
            groups[demo_key].append(response)
        
        return groups
    
    def _parse_demo_key(self, demo_key: str) -> Dict[str, str]:
        """Parse demographic key back to dictionary"""
        demo_info = {}
        if demo_key:
            pairs = demo_key.split('|')
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    demo_info[key] = value
        return demo_info
    
    def _validate_data_quality(self, data: List[Dict[str, Any]]) -> float:
        """Calculate overall data quality score"""
        if not data:
            return 0.0
        
        total_score = 0
        total_questions = 0
        
        for response in data:
            answers = response.get('answers', {})
            
            for q_id, answer_data in answers.items():
                total_questions += 1
                
                # Score this answer
                answer_score = 0
                
                # Has answer
                if answer_data.get('answer'):
                    answer_score += 40
                
                # Answer length appropriate
                answer = str(answer_data.get('answer', ''))
                if answer_data.get('question_type') == 'Descriptive':
                    if 20 <= len(answer) <= 200:
                        answer_score += 30
                elif answer_data.get('question_type') == 'MCQ':
                    if answer.strip():
                        answer_score += 30
                
                # Not imputed (original data)
                if not answer_data.get('imputed'):
                    answer_score += 20
                
                # Standardized properly
                if answer_data.get('standardized'):
                    answer_score += 10
                
                total_score += answer_score
        
        if total_questions == 0:
            return 0.0
        
        return (total_score / total_questions)
    
    def get_cleaning_report(self) -> Dict[str, Any]:
        """Generate comprehensive cleaning report"""
        return {
            'statistics': self.cleaning_stats.copy(),
            'summary': {
                'original_records': self.cleaning_stats['original_count'],
                'final_records': self.cleaning_stats['original_count'] - 
                               self.cleaning_stats['removed_duplicates'] - 
                               self.cleaning_stats['removed_outliers'],
                'data_retention_rate': ((self.cleaning_stats['original_count'] - 
                                       self.cleaning_stats['removed_duplicates'] - 
                                       self.cleaning_stats['removed_outliers']) / 
                                      max(self.cleaning_stats['original_count'], 1)) * 100,
                'quality_improvements': {
                    'missing_values_fixed': self.cleaning_stats['fixed_missing_values'],
                    'responses_standardized': self.cleaning_stats['standardized_responses'],
                    'groups_balanced': self.cleaning_stats['balanced_groups']
                }
            }
        }