"""
Variable Extractor Module
Extracts key variables from business problems using NLP techniques
"""

import re
from typing import List, Dict, Any


class VariableExtractor:
    """Extract variables from business problem descriptions"""
    
    def __init__(self):
        # Common business variable keywords
        self.variable_keywords = [
            'customer', 'price', 'revenue', 'cost', 'profit', 'sales', 'marketing',
            'conversion', 'retention', 'satisfaction', 'engagement', 'traffic',
            'demographic', 'geographic', 'behavioral', 'psychographic',
            'age', 'gender', 'income', 'education', 'location', 'time', 'season',
            'product', 'service', 'brand', 'quality', 'quantity', 'frequency',
            'channel', 'source', 'campaign', 'advertisement', 'promotion',
            'competition', 'market', 'industry', 'segment', 'target',
            'performance', 'efficiency', 'productivity', 'growth', 'trend'
        ]
        
        # Business metrics patterns
        self.metric_patterns = [
            r'\b(\w+)\s+(rate|ratio|percentage|percent|score|index|metric)\b',
            r'\b(number|count|total|sum|average|mean|median)\s+of\s+(\w+)\b',
            r'\b(\w+)\s+(per|by|across)\s+(\w+)\b',
            r'\b(\w+)\s+(analysis|measurement|evaluation)\b'
        ]
    
    def extract_variables(self, business_problem: str) -> List[str]:
        """Extract variables from business problem description"""
        variables = []
        problem_lower = business_problem.lower()
        
        # Extract keyword-based variables
        for keyword in self.variable_keywords:
            if keyword in problem_lower:
                variables.append(f"{keyword.title()} Analysis")
        
        # Extract metric-based variables using patterns
        for pattern in self.metric_patterns:
            matches = re.findall(pattern, problem_lower)
            for match in matches:
                if isinstance(match, tuple):
                    var_name = ' '.join([word.title() for word in match if word])
                    variables.append(var_name)
                else:
                    variables.append(match.title())
        
        # Extract custom variables from context
        custom_vars = self._extract_custom_variables(business_problem)
        variables.extend(custom_vars)
        
        # Remove duplicates and return top 10 most relevant
        unique_vars = list(dict.fromkeys(variables))
        
        # Score and rank variables by relevance
        scored_vars = self._score_variables(unique_vars, business_problem)
        
        return scored_vars[:10]  # Return top 10 variables
    
    def _extract_custom_variables(self, problem: str) -> List[str]:
        """Extract custom variables specific to the business context"""
        custom_variables = []
        
        # Look for question words indicating variables
        question_patterns = [
            r'what\s+(factors?|variables?|elements?)\s+(affect|influence|impact)',
            r'how\s+(does|do)\s+(\w+)\s+(affect|influence|impact)',
            r'which\s+(\w+)\s+(are|is)\s+(important|significant|relevant)',
            r'why\s+(does|do)\s+(\w+)\s+(vary|change|differ)'
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, problem.lower())
            for match in matches:
                if isinstance(match, tuple):
                    for word in match:
                        if len(word) > 2 and word not in ['does', 'do', 'are', 'is']:
                            custom_variables.append(f"{word.title()} Factor")
        
        return custom_variables
    
    def _score_variables(self, variables: List[str], problem: str) -> List[str]:
        """Score and rank variables by relevance to the business problem"""
        scored_vars = []
        problem_words = set(problem.lower().split())
        
        for var in variables:
            score = 0
            var_words = set(var.lower().split())
            
            # Calculate relevance score
            common_words = problem_words.intersection(var_words)
            score += len(common_words) * 2
            
            # Bonus for business-critical terms
            critical_terms = {'customer', 'revenue', 'sales', 'profit', 'conversion'}
            if any(term in var.lower() for term in critical_terms):
                score += 3
            
            scored_vars.append((var, score))
        
        # Sort by score (descending) and return variable names
        scored_vars.sort(key=lambda x: x[1], reverse=True)
        return [var for var, score in scored_vars]
    
    def suggest_additional_variables(self, existing_vars: List[str]) -> List[str]:
        """Suggest additional variables based on existing ones"""
        suggestions = []
        
        # Define variable relationships
        relationships = {
            'customer': ['Customer Satisfaction', 'Customer Lifetime Value', 'Customer Acquisition Cost'],
            'sales': ['Sales Performance', 'Sales Conversion Rate', 'Sales Seasonality'],
            'marketing': ['Marketing ROI', 'Marketing Channel Effectiveness', 'Marketing Budget Allocation'],
            'price': ['Price Sensitivity', 'Price Elasticity', 'Competitive Pricing'],
            'product': ['Product Quality', 'Product Features', 'Product Lifecycle Stage']
        }
        
        for var in existing_vars:
            var_lower = var.lower()
            for key, related_vars in relationships.items():
                if key in var_lower:
                    suggestions.extend(related_vars)
        
        # Remove duplicates and variables already in the list
        suggestions = [s for s in set(suggestions) if s not in existing_vars]
        
        return suggestions[:5]  