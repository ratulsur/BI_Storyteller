"""
EDA (Exploratory Data Analysis) Analyzer Module
Comprehensive statistical analysis and insights generation
"""

import json
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
import statistics


class EDAAnalyzer:
    """Perform comprehensive exploratory data analysis"""
    
    def __init__(self):
        self.analysis_results = {}
        self.insights = []
    
    def perform_eda(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive EDA on cleaned data"""
        print("📊 Performing Exploratory Data Analysis...")
        
        # Initialize results structure
        results = {
            'summary_statistics': {},
            'categorical_analysis': {},
            'text_analysis': {},
            'correlation_analysis': {},
            'insights': [],
            'visualizations': []
        }
        
        # Extract structured data for analysis
        structured_data = self._extract_structured_data(data)
        
        # Perform different types of analysis
        results['summary_statistics'] = self._calculate_summary_stats(structured_data)
        results['categorical_analysis'] = self._analyze_categorical_data(structured_data)
        results['text_analysis'] = self._analyze_text_responses(data)
        results['correlation_analysis'] = self._analyze_correlations(structured_data)
        
        # Generate insights
        results['insights'] = self._generate_insights(results)
        
        # Suggest visualizations
        results['visualizations'] = self._suggest_visualizations(structured_data)
        
        return results
    
    def _extract_structured_data(self, data: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
        """Extract structured data for statistical analysis"""
        structured = defaultdict(list)
        question_metadata = {}
        
        for response in data:
            answers = response.get('answers', {})
            
            for q_id, answer_data in answers.items():
                question = answer_data.get('question', '')
                answer = answer_data.get('answer', '')
                question_type = answer_data.get('question_type', 'unknown')
                category = answer_data.get('category', 'general')
                
                if answer:
                    structured[q_id].append(answer)
                    question_metadata[q_id] = {
                        'question': question,
                        'type': question_type,
                        'category': category
                    }
        
        # Store metadata for later use
        self.question_metadata = question_metadata
        
        return dict(structured)
    
    def _calculate_summary_stats(self, structured_data: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for all questions"""
        summary_stats = {}
        
        for q_id, responses in structured_data.items():
            metadata = self.question_metadata.get(q_id, {})
            question_type = metadata.get('type', 'unknown')
            
            stats = {
                'total_responses': len(responses),
                'question_type': question_type,
                'category': metadata.get('category', 'general'),
                'question': metadata.get('question', '')
            }
            
            if question_type == 'MCQ':
                # Categorical statistics
                response_counts = Counter(responses)
                total = len(responses)
                
                stats.update({
                    'unique_values': len(response_counts),
                    'most_common': response_counts.most_common(3),
                    'distribution': {value: (count/total)*100 
                                   for value, count in response_counts.items()},
                    'mode': response_counts.most_common(1)[0][0] if response_counts else None
                })
            
            elif question_type == 'Descriptive':
                # Text statistics
                text_lengths = [len(str(response)) for response in responses]
                
                if text_lengths:
                    stats.update({
                        'avg_response_length': statistics.mean(text_lengths),
                        'min_length': min(text_lengths),
                        'max_length': max(text_lengths),
                        'median_length': statistics.median(text_lengths)
                    })
            
            summary_stats[q_id] = stats
        
        return summary_stats
    
    def _analyze_categorical_data(self, structured_data: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Detailed analysis of categorical variables"""
        categorical_analysis = {}
        
        for q_id, responses in structured_data.items():
            metadata = self.question_metadata.get(q_id, {})
            
            if metadata.get('type') == 'MCQ':
                category = metadata.get('category', 'general')
                response_counts = Counter(responses)
                total = len(responses)
                
                analysis = {
                    'category': category,
                    'distribution': dict(response_counts),
                    'percentages': {k: (v/total)*100 for k, v in response_counts.items()},
                    'entropy': self._calculate_entropy(response_counts, total),
                    'top_responses': response_counts.most_common(5)
                }
                
                # Category-specific analysis
                if category == 'demographic':
                    analysis['demographic_insights'] = self._analyze_demographic_distribution(response_counts)
                elif category in ['satisfaction', 'rating']:
                    analysis['satisfaction_score'] = self._calculate_satisfaction_score(response_counts)
                
                categorical_analysis[q_id] = analysis
        
        return categorical_analysis
    
    def _analyze_text_responses(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze descriptive text responses"""
        text_analysis = {
            'word_frequency': Counter(),
            'common_themes': [],
            'sentiment_indicators': {
                'positive': 0,
                'neutral': 0,
                'negative': 0
            },
            'response_patterns': {}
        }
        
        all_text = []
        
        for response in data:
            answers = response.get('answers', {})
            
            for q_id, answer_data in answers.items():
                if answer_data.get('question_type') == 'Descriptive':
                    answer_text = str(answer_data.get('answer', '')).lower()
                    if answer_text:
                        all_text.append(answer_text)
        
        # Word frequency analysis
        words = []
        for text in all_text:
            # Simple word extraction (in real implementation, use NLTK)
            text_words = [word.strip('.,!?;:"()[]') for word in text.split()]
            text_words = [word for word in text_words if len(word) > 3]
            words.extend(text_words)
        
        text_analysis['word_frequency'] = Counter(words).most_common(20)
        
        # Basic sentiment analysis (simplified)
        positive_words = ['good', 'great', 'excellent', 'satisfied', 'happy', 'love', 'amazing', 'perfect']
        negative_words = ['bad', 'terrible', 'awful', 'dissatisfied', 'hate', 'poor', 'worst', 'horrible']
        
        for text in all_text:
            positive_count = sum(1 for word in positive_words if word in text)
            negative_count = sum(1 for word in negative_words if word in text)
            
            if positive_count > negative_count:
                text_analysis['sentiment_indicators']['positive'] += 1
            elif negative_count > positive_count:
                text_analysis['sentiment_indicators']['negative'] += 1
            else:
                text_analysis['sentiment_indicators']['neutral'] += 1
        
        # Common themes (simplified pattern matching)
        themes = {
            'price_cost': ['price', 'cost', 'expensive', 'cheap', 'affordable', 'budget'],
            'quality': ['quality', 'reliable', 'durable', 'robust', 'solid'],
            'service': ['service', 'support', 'help', 'assistance', 'customer'],
            'usability': ['easy', 'difficult', 'simple', 'complex', 'intuitive'],
            'features': ['feature', 'function', 'capability', 'option', 'tool']
        }
        
        theme_counts = {}
        for theme, keywords in themes.items():
            count = sum(1 for text in all_text 
                       for keyword in keywords if keyword in text)
            if count > 0:
                theme_counts[theme] = count
        
        text_analysis['common_themes'] = sorted(theme_counts.items(), 
                                              key=lambda x: x[1], reverse=True)
        
        return text_analysis
    
    def _analyze_correlations(self, structured_data: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Analyze correlations between different variables"""
        correlations = {
            'demographic_correlations': {},
            'satisfaction_correlations': {},
            'behavioral_patterns': {}
        }
        
        # Group questions by category
        questions_by_category = defaultdict(list)
        for q_id, metadata in self.question_metadata.items():
            category = metadata.get('category', 'general')
            questions_by_category[category].append(q_id)
        
        # Analyze demographic vs other categories
        demo_questions = questions_by_category.get('demographic', [])
        
        for demo_q in demo_questions:
            if demo_q not in structured_data:
                continue
                
            demo_responses = structured_data[demo_q]
            demo_metadata = self.question_metadata[demo_q]
            
            correlations['demographic_correlations'][demo_q] = {
                'question': demo_metadata.get('question', ''),
                'correlations_with': {}
            }
            
            # Compare with satisfaction questions
            satisfaction_questions = [q for q in questions_by_category.get('satisfaction', []) + 
                                    questions_by_category.get('rating', [])
                                    if q in structured_data]
            
            for sat_q in satisfaction_questions:
                correlation = self._calculate_categorical_correlation(
                    demo_responses, structured_data[sat_q]
                )
                
                if correlation['strength'] > 0.1:  # Only significant correlations
                    correlations['demographic_correlations'][demo_q]['correlations_with'][sat_q] = {
                        'question': self.question_metadata[sat_q].get('question', ''),
                        'correlation_strength': correlation['strength'],
                        'patterns': correlation['patterns']
                    }
        
        return correlations
    
    def _calculate_entropy(self, response_counts: Counter, total: int) -> float:
        """Calculate entropy for categorical distribution"""
        if total == 0:
            return 0
        
        entropy = 0
        for count in response_counts.values():
            if count > 0:
                p = count / total
                entropy -= p * (p.bit_length() - 1)  # Simplified log2
        
        return entropy
    
    def _analyze_demographic_distribution(self, response_counts: Counter) -> Dict[str, Any]:
        """Analyze demographic distribution patterns"""
        total = sum(response_counts.values())
        
        analysis = {
            'diversity_score': len(response_counts) / max(total, 1),
            'dominant_group': response_counts.most_common(1)[0] if response_counts else None,
            'representation_balance': {}
        }
        
        # Check for balanced representation
        if len(response_counts) > 1:
            percentages = [(count/total)*100 for count in response_counts.values()]
            balance_score = 1 - (max(percentages) - min(percentages)) / 100
            analysis['representation_balance']['score'] = balance_score
            analysis['representation_balance']['is_balanced'] = balance_score > 0.7
        
        return analysis
    
    def _calculate_satisfaction_score(self, response_counts: Counter) -> Dict[str, Any]:
        """Calculate overall satisfaction metrics"""
        # Map satisfaction levels to scores
        satisfaction_scores = {
            'Very Satisfied': 5, 'Satisfied': 4, 'Neutral': 3,
            'Dissatisfied': 2, 'Very Dissatisfied': 1,
            'Excellent': 5, 'Good': 4, 'Average': 3,
            'Poor': 2, 'Very Poor': 1
        }
        
        total_score = 0
        total_responses = 0
        
        for response, count in response_counts.items():
            score = satisfaction_scores.get(response, 3)  # Default to neutral
            total_score += score * count
            total_responses += count
        
        avg_score = total_score / max(total_responses, 1)
        
        # Calculate satisfaction percentage
        positive_responses = sum(count for response, count in response_counts.items()
                               if satisfaction_scores.get(response, 3) >= 4)
        satisfaction_percentage = (positive_responses / max(total_responses, 1)) * 100
        
        return {
            'average_score': avg_score,
            'satisfaction_percentage': satisfaction_percentage,
            'total_responses': total_responses,
            'distribution': dict(response_counts)
        }
    
    def _calculate_categorical_correlation(self, var1: List[str], var2: List[str]) -> Dict[str, Any]:
        """Calculate correlation between two categorical variables"""
        if len(var1) != len(var2):
            return {'strength': 0, 'patterns': {}}
        
        # Create contingency table
        contingency = defaultdict(lambda: defaultdict(int))
        
        for v1, v2 in zip(var1, var2):
            contingency[v1][v2] += 1
        
        # Calculate correlation strength (simplified Cramér's V approximation)
        total = len(var1)
        
        # Find patterns
        patterns = {}
        for v1, v2_counts in contingency.items():
            most_common_v2 = max(v2_counts.items(), key=lambda x: x[1])
            patterns[v1] = {
                'most_associated_with': most_common_v2[0],
                'strength': most_common_v2[1] / sum(v2_counts.values())
            }
        
        # Calculate overall correlation strength
        max_association = max(p['strength'] for p in patterns.values()) if patterns else 0
        
        return {
            'strength': max_association,
            'patterns': patterns
        }
    
    def _generate_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from analysis"""
        insights = []
        
        # Summary statistics insights
        summary_stats = analysis_results.get('summary_statistics', {})
        total_responses = sum(stats.get('total_responses', 0) for stats in summary_stats.values())
        
        insights.append(f"Analyzed {total_responses} total responses across {len(summary_stats)} questions")
        
        # Categorical analysis insights
        categorical_analysis = analysis_results.get('categorical_analysis', {})
        
        # Satisfaction insights
        satisfaction_questions = [q_id for q_id, analysis in categorical_analysis.items()
                                if analysis.get('category') in ['satisfaction', 'rating']]
        
        if satisfaction_questions:
            avg_satisfaction = []
            for q_id in satisfaction_questions:
                sat_score = categorical_analysis[q_id].get('satisfaction_score', {})
                if 'satisfaction_percentage' in sat_score:
                    avg_satisfaction.append(sat_score['satisfaction_percentage'])
            
            if avg_satisfaction:
                overall_satisfaction = sum(avg_satisfaction) / len(avg_satisfaction)
                insights.append(f"Overall satisfaction rate: {overall_satisfaction:.1f}%")
                
                if overall_satisfaction > 70:
                    insights.append("High satisfaction levels indicate positive user experience")
                elif overall_satisfaction < 50:
                    insights.append("Low satisfaction levels suggest areas for improvement")
        
        # Text analysis insights
        text_analysis = analysis_results.get('text_analysis', {})
        sentiment = text_analysis.get('sentiment_indicators', {})
        total_sentiment = sum(sentiment.values())
        
        if total_sentiment > 0:
            positive_pct = (sentiment.get('positive', 0) / total_sentiment) * 100
            insights.append(f"Text sentiment: {positive_pct:.1f}% positive responses")
        
        # Theme insights
        themes = text_analysis.get('common_themes', [])
        if themes:
            top_theme = themes[0]
            insights.append(f"Most mentioned theme: {top_theme[0]} ({top_theme[1]} mentions)")
        
        # Demographic insights
        demo_questions = [q_id for q_id, analysis in categorical_analysis.items()
                         if analysis.get('category') == 'demographic']
        
        if demo_questions:
            for q_id in demo_questions:
                demo_analysis = categorical_analysis[q_id]
                demo_insights = demo_analysis.get('demographic_insights', {})
                
                if demo_insights.get('representation_balance', {}).get('is_balanced'):
                    question = summary_stats[q_id].get('question', 'Demographic question')
                    insights.append(f"Well-balanced representation in: {question}")
        
        # Correlation insights
        correlation_analysis = analysis_results.get('correlation_analysis', {})
        demo_correlations = correlation_analysis.get('demographic_correlations', {})
        
        for demo_q, corr_data in demo_correlations.items():
            correlations_with = corr_data.get('correlations_with', {})
            if correlations_with:
                strong_correlations = [q for q, data in correlations_with.items()
                                     if data.get('correlation_strength', 0) > 0.3]
                
                if strong_correlations:
                    demo_question = corr_data.get('question', 'Demographics')
                    insights.append(f"{demo_question} shows strong correlation with {len(strong_correlations)} other factors")
        
        return insights
    
    def _suggest_visualizations(self, structured_data: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """Suggest appropriate visualizations for the data"""
        visualizations = []
        
        for q_id, responses in structured_data.items():
            metadata = self.question_metadata.get(q_id, {})
            question_type = metadata.get('type', 'unknown')
            category = metadata.get('category', 'general')
            
            if question_type == 'MCQ':
                # Suggest bar charts for categorical data
                viz = {
                    'type': 'bar_chart',
                    'question_id': q_id,
                    'question': metadata.get('question', ''),
                    'data_type': 'categorical',
                    'description': f"Bar chart showing distribution of responses for: {metadata.get('question', '')}"
                }
                
                if category == 'demographic':
                    viz['type'] = 'pie_chart'
                    viz['description'] = f"Pie chart showing demographic distribution for: {metadata.get('question', '')}"
                
                visualizations.append(viz)
                
                # Suggest additional visualizations for satisfaction
                if category in ['satisfaction', 'rating']:
                    visualizations.append({
                        'type': 'gauge_chart',
                        'question_id': q_id,
                        'question': metadata.get('question', ''),
                        'data_type': 'satisfaction',
                        'description': f"Gauge chart showing satisfaction level for: {metadata.get('question', '')}"
                    })
        
        # Suggest correlation heatmap if multiple categorical variables
        categorical_questions = [q_id for q_id, metadata in self.question_metadata.items()
                               if metadata.get('type') == 'MCQ']
        
        if len(categorical_questions) >= 3:
            visualizations.append({
                'type': 'heatmap',
                'question_ids': categorical_questions,
                'data_type': 'correlation',
                'description': "Correlation heatmap showing relationships between variables"
            })
        
        # Suggest word cloud for text analysis
        descriptive_questions = [q_id for q_id, metadata in self.question_metadata.items()
                               if metadata.get('type') == 'Descriptive']
        
        if descriptive_questions:
            visualizations.append({
                'type': 'word_cloud',
                'question_ids': descriptive_questions,
                'data_type': 'text',
                'description': "Word cloud showing most frequently mentioned terms"
            })
        
        return visualizations