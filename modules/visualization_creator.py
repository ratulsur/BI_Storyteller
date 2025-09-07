"""
Visualization Creator Module
Creates various types of charts and visualizations using ASCII art and data summaries
"""

import json
from typing import List, Dict, Any, Tuple
from collections import Counter


class VisualizationCreator:
    """Create visualizations from data analysis"""
    
    def __init__(self):
        self.visualization_data = {}
        self.chart_configs = {
            'bar_chart': {'width': 50, 'height': 20},
            'pie_chart': {'segments': 8},
            'line_chart': {'width': 60, 'height': 15},
            'histogram': {'bins': 10, 'width': 40}
        }
    
    def create_visualizations(self, data: List[Dict[str, Any]], 
                            selected_features: List[str]) -> Dict[str, Any]:
        """Create visualizations for selected features"""
        print(f"📊 Creating visualizations for {len(selected_features)} features...")
        
        visualizations = {
            'charts': [],
            'summaries': [],
            'export_data': {},
            'recommended_charts': []
        }
        
        # Extract data for selected features
        feature_data = self._extract_feature_data(data, selected_features)
        
        # Create different types of visualizations
        for feature in selected_features:
            if feature in feature_data:
                viz_data = feature_data[feature]
                
                # Determine best visualization type
                viz_type = self._determine_viz_type(viz_data)
                
                # Create visualization
                chart = self._create_chart(feature, viz_data, viz_type)
                if chart:
                    visualizations['charts'].append(chart)
                    
                # Create summary
                summary = self._create_summary(feature, viz_data)
                visualizations['summaries'].append(summary)
                
                # Prepare export data
                visualizations['export_data'][feature] = {
                    'chart_type': viz_type,
                    'data': viz_data,
                    'summary': summary
                }
        
        # Create combined visualizations
        combined_viz = self._create_combined_visualizations(feature_data)
        visualizations['charts'].extend(combined_viz)
        
        # Suggest additional visualizations
        visualizations['recommended_charts'] = self._suggest_additional_charts(feature_data)
        
        return visualizations
    
    def _extract_feature_data(self, data: List[Dict[str, Any]], 
                            features: List[str]) -> Dict[str, Dict[str, Any]]:
        """Extract data for visualization from survey responses"""
        feature_data = {}
        
        for response in data:
            answers = response.get('answers', {})
            
            for q_id, answer_data in answers.items():
                question = answer_data.get('question', '').lower()
                answer = answer_data.get('answer')
                question_type = answer_data.get('question_type', 'unknown')
                
                # Check if this question relates to any selected feature
                for feature in features:
                    if feature.lower() in question or any(word in question for word in feature.lower().split()):
                        
                        if feature not in feature_data:
                            feature_data[feature] = {
                                'question_id': q_id,
                                'question': answer_data.get('question', ''),
                                'type': question_type,
                                'category': answer_data.get('category', 'general'),
                                'responses': [],
                                'metadata': {}
                            }
                        
                        if answer:
                            feature_data[feature]['responses'].append(str(answer))
        
        # Process collected data
        for feature, data_info in feature_data.items():
            responses = data_info['responses']
            
            if data_info['type'] == 'MCQ':
                # Categorical data processing
                response_counts = Counter(responses)
                total = len(responses)
                
                data_info['metadata'] = {
                    'distribution': dict(response_counts),
                    'percentages': {k: (v/total)*100 for k, v in response_counts.items()},
                    'top_responses': response_counts.most_common(5),
                    'unique_count': len(response_counts),
                    'total_responses': total
                }
                
            elif data_info['type'] == 'Descriptive':
                # Text data processing
                response_lengths = [len(resp) for resp in responses]
                word_counts = []
                
                for resp in responses:
                    words = resp.split()
                    word_counts.append(len(words))
                
                data_info['metadata'] = {
                    'avg_length': sum(response_lengths) / len(response_lengths) if response_lengths else 0,
                    'avg_word_count': sum(word_counts) / len(word_counts) if word_counts else 0,
                    'total_responses': len(responses),
                    'sample_responses': responses[:3]  # First 3 for preview
                }
        
        return feature_data
    
    def _determine_viz_type(self, viz_data: Dict[str, Any]) -> str:
        """Determine the best visualization type for the data"""
        data_type = viz_data.get('type', 'unknown')
        category = viz_data.get('category', 'general')
        
        if data_type == 'MCQ':
            unique_count = viz_data.get('metadata', {}).get('unique_count', 0)
            
            if category == 'demographic':
                return 'pie_chart'
            elif category in ['satisfaction', 'rating']:
                return 'horizontal_bar'
            elif unique_count <= 5:
                return 'bar_chart'
            else:
                return 'horizontal_bar'
                
        elif data_type == 'Descriptive':
            return 'word_frequency'
        
        return 'bar_chart'
    
    def _create_chart(self, feature: str, viz_data: Dict[str, Any], 
                     viz_type: str) -> Dict[str, Any]:
        """Create a specific type of chart"""
        chart_methods = {
            'bar_chart': self._create_bar_chart,
            'horizontal_bar': self._create_horizontal_bar,
            'pie_chart': self._create_pie_chart,
            'word_frequency': self._create_word_frequency_chart
        }
        
        if viz_type in chart_methods:
            return chart_methods[viz_type](feature, viz_data)
        
        return None
    
    def _create_bar_chart(self, feature: str, viz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create ASCII bar chart"""
        metadata = viz_data.get('metadata', {})
        distribution = metadata.get('distribution', {})
        
        if not distribution:
            return None
        
        # Create ASCII bar chart
        max_count = max(distribution.values())
        chart_width = 50
        
        chart_lines = []
        chart_lines.append(f"📊 {feature} Distribution")
        chart_lines.append("=" * 60)
        
        for label, count in distribution.items():
            bar_length = int((count / max_count) * chart_width) if max_count > 0 else 0
            bar = "█" * bar_length
            percentage = (count / sum(distribution.values())) * 100
            
            chart_lines.append(f"{label[:15]:15} |{bar:50}| {count:4} ({percentage:5.1f}%)")
        
        chart_lines.append("=" * 60)
        
        return {
            'type': 'bar_chart',
            'feature': feature,
            'title': f"{feature} Distribution",
            'ascii_chart': '\n'.join(chart_lines),
            'data': distribution,
            'insights': [
                f"Most common response: {max(distribution, key=distribution.get)}",
                f"Total responses: {sum(distribution.values())}",
                f"Unique responses: {len(distribution)}"
            ]
        }
    
    def _create_horizontal_bar(self, feature: str, viz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create horizontal bar chart for satisfaction/rating data"""
        metadata = viz_data.get('metadata', {})
        distribution = metadata.get('distribution', {})
        
        if not distribution:
            return None
        
        # Order satisfaction/rating responses logically
        satisfaction_order = [
            'Very Satisfied', 'Satisfied', 'Neutral', 'Dissatisfied', 'Very Dissatisfied',
            'Excellent', 'Good', 'Average', 'Poor', 'Very Poor'
        ]
        
        ordered_items = []
        for item in satisfaction_order:
            if item in distribution:
                ordered_items.append((item, distribution[item]))
        
        # Add any remaining items
        for item, count in distribution.items():
            if item not in [x[0] for x in ordered_items]:
                ordered_items.append((item, count))
        
        # Create chart
        max_count = max(distribution.values())
        chart_width = 40
        
        chart_lines = []
        chart_lines.append(f"📊 {feature} Analysis")
        chart_lines.append("=" * 70)
        
        for label, count in ordered_items:
            bar_length = int((count / max_count) * chart_width) if max_count > 0 else 0
            bar = "█" * bar_length
            percentage = (count / sum(distribution.values())) * 100
            
            chart_lines.append(f"{label[:20]:20} |{bar:<40}| {percentage:5.1f}%")
        
        chart_lines.append("=" * 70)
        
        # Calculate satisfaction score for satisfaction/rating questions
        satisfaction_score = self._calculate_satisfaction_score(ordered_items)
        
        insights = [
            f"Satisfaction score: {satisfaction_score:.1f}/5.0",
            f"Most common response: {ordered_items[0][0] if ordered_items else 'N/A'}",
            f"Total responses: {sum(distribution.values())}"
        ]
        
        if satisfaction_score >= 4.0:
            insights.append("High satisfaction levels detected")
        elif satisfaction_score <= 2.5:
            insights.append("Low satisfaction - immediate attention needed")
        
        return {
            'type': 'horizontal_bar',
            'feature': feature,
            'title': f"{feature} Analysis",
            'ascii_chart': '\n'.join(chart_lines),
            'data': dict(ordered_items),
            'satisfaction_score': satisfaction_score,
            'insights': insights
        }
    
    def _create_pie_chart(self, feature: str, viz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create ASCII pie chart representation"""
        metadata = viz_data.get('metadata', {})
        distribution = metadata.get('distribution', {})
        percentages = metadata.get('percentages', {})
        
        if not distribution:
            return None
        
        chart_lines = []
        chart_lines.append(f"🥧 {feature} Distribution (Pie Chart)")
        chart_lines.append("=" * 50)
        
        # Create pie chart using ASCII
        total = sum(distribution.values())
        pie_chars = ["█", "▓", "▒", "░", "▪", "▫", "●", "○"]
        
        for i, (label, count) in enumerate(distribution.items()):
            percentage = (count / total) * 100
            char = pie_chars[i % len(pie_chars)]
            segment = char * int(percentage / 5)  # Scale down for display
            
            chart_lines.append(f"{char} {label[:20]:20} {segment:20} {percentage:5.1f}%")
        
        chart_lines.append("=" * 50)
        
        # Find dominant category
        dominant = max(distribution, key=distribution.get)
        dominant_pct = percentages.get(dominant, 0)
        
        insights = [
            f"Dominant category: {dominant} ({dominant_pct:.1f}%)",
            f"Number of categories: {len(distribution)}",
            f"Total responses: {total}"
        ]
        
        if dominant_pct > 50:
            insights.append(f"Strong dominance by {dominant}")
        elif len(distribution) > 5:
            insights.append("High diversity in responses")
        
        return {
            'type': 'pie_chart',
            'feature': feature,
            'title': f"{feature} Distribution",
            'ascii_chart': '\n'.join(chart_lines),
            'data': distribution,
            'insights': insights
        }
    
    def _create_word_frequency_chart(self, feature: str, viz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create word frequency visualization for text data"""
        responses = viz_data.get('responses', [])
        
        if not responses:
            return None
        
        # Extract words from all responses
        all_words = []
        for response in responses:
            words = response.lower().split()
            # Filter out common stop words and short words
            filtered_words = [word.strip('.,!?;:"()[]') for word in words 
                            if len(word.strip('.,!?;:"()[]')) > 3]
            all_words.extend(filtered_words)
        
        # Count word frequency
        word_freq = Counter(all_words)
        top_words = word_freq.most_common(10)
        
        if not top_words:
            return None
        
        # Create word frequency chart
        max_count = top_words[0][1]
        chart_width = 30
        
        chart_lines = []
        chart_lines.append(f"🔤 {feature} - Most Common Words")
        chart_lines.append("=" * 60)
        
        for word, count in top_words:
            bar_length = int((count / max_count) * chart_width) if max_count > 0 else 0
            bar = "█" * bar_length
            
            chart_lines.append(f"{word[:15]:15} |{bar:30}| {count:3}")
        
        chart_lines.append("=" * 60)
        
        insights = [
            f"Most mentioned word: '{top_words[0][0]}' ({top_words[0][1]} times)",
            f"Total unique words: {len(word_freq)}",
            f"Total word occurrences: {sum(word_freq.values())}",
            f"Average response length: {viz_data.get('metadata', {}).get('avg_word_count', 0):.1f} words"
        ]
        
        return {
            'type': 'word_frequency',
            'feature': feature,
            'title': f"{feature} - Word Frequency Analysis",
            'ascii_chart': '\n'.join(chart_lines),
            'data': dict(top_words),
            'insights': insights
        }
    
    def _create_combined_visualizations(self, feature_data: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create visualizations that combine multiple features"""
        combined_viz = []
        
        # Create satisfaction overview if multiple satisfaction questions exist
        satisfaction_features = [feature for feature, data in feature_data.items()
                               if data.get('category') in ['satisfaction', 'rating']]
        
        if len(satisfaction_features) >= 2:
            combined_viz.append(self._create_satisfaction_overview(satisfaction_features, feature_data))
        
        # Create demographic overview
        demographic_features = [feature for feature, data in feature_data.items()
                              if data.get('category') == 'demographic']
        
        if len(demographic_features) >= 2:
            combined_viz.append(self._create_demographic_overview(demographic_features, feature_data))
        
        return combined_viz
    
    def _create_satisfaction_overview(self, features: List[str], 
                                    feature_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Create combined satisfaction overview"""
        chart_lines = []
        chart_lines.append("📊 Overall Satisfaction Overview")
        chart_lines.append("=" * 70)
        
        satisfaction_scores = []
        
        for feature in features:
            data = feature_data[feature]
            distribution = data.get('metadata', {}).get('distribution', {})
            
            if distribution:
                # Calculate satisfaction score
                ordered_items = list(distribution.items())
                score = self._calculate_satisfaction_score(ordered_items)
                satisfaction_scores.append((feature, score))
                
                # Create mini bar
                bar_length = int(score * 10)  # Scale to 50 chars
                bar = "█" * bar_length + "░" * (50 - bar_length)
                
                chart_lines.append(f"{feature[:25]:25} |{bar}| {score:.1f}/5.0")
        
        chart_lines.append("=" * 70)
        
        # Calculate overall satisfaction
        if satisfaction_scores:
            avg_satisfaction = sum(score for _, score in satisfaction_scores) / len(satisfaction_scores)
            chart_lines.append(f"Overall Average Satisfaction: {avg_satisfaction:.1f}/5.0")
        
        insights = [
            f"Analyzed {len(features)} satisfaction metrics",
            f"Average satisfaction: {avg_satisfaction:.1f}/5.0" if satisfaction_scores else "No data",
        ]
        
        if satisfaction_scores:
            best_feature = max(satisfaction_scores, key=lambda x: x[1])
            worst_feature = min(satisfaction_scores, key=lambda x: x[1])
            
            insights.extend([
                f"Highest satisfaction: {best_feature[0]} ({best_feature[1]:.1f})",
                f"Lowest satisfaction: {worst_feature[0]} ({worst_feature[1]:.1f})"
            ])
        
        return {
            'type': 'satisfaction_overview',
            'feature': 'Overall Satisfaction',
            'title': 'Satisfaction Overview',
            'ascii_chart': '\n'.join(chart_lines),
            'data': dict(satisfaction_scores),
            'insights': insights
        }
    
    def _create_demographic_overview(self, features: List[str], 
                                   feature_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Create demographic overview visualization"""
        chart_lines = []
        chart_lines.append("👥 Demographic Overview")
        chart_lines.append("=" * 60)
        
        for feature in features:
            data = feature_data[feature]
            distribution = data.get('metadata', {}).get('distribution', {})
            
            if distribution:
                chart_lines.append(f"\n{feature}:")
                
                for category, count in list(distribution.items())[:3]:  # Top 3 categories
                    total = sum(distribution.values())
                    percentage = (count / total) * 100 if total > 0 else 0
                    
                    chart_lines.append(f"  {category[:20]:20} {count:4} ({percentage:5.1f}%)")
                
                if len(distribution) > 3:
                    chart_lines.append(f"  ... and {len(distribution) - 3} more categories")
        
        chart_lines.append("=" * 60)
        
        insights = [
            f"Analyzed {len(features)} demographic dimensions",
            "Demographic diversity supports representative analysis"
        ]
        
        return {
            'type': 'demographic_overview',
            'feature': 'Demographics',
            'title': 'Demographic Overview',
            'ascii_chart': '\n'.join(chart_lines),
            'data': {feature: feature_data[feature].get('metadata', {}).get('distribution', {}) 
                    for feature in features},
            'insights': insights
        }
    
    def _calculate_satisfaction_score(self, items: List[Tuple[str, int]]) -> float:
        """Calculate satisfaction score from response distribution"""
        satisfaction_values = {
            'Very Satisfied': 5, 'Satisfied': 4, 'Neutral': 3,
            'Dissatisfied': 2, 'Very Dissatisfied': 1,
            'Excellent': 5, 'Good': 4, 'Average': 3,
            'Poor': 2, 'Very Poor': 1
        }
        
        total_score = 0
        total_responses = 0
        
        for label, count in items:
            value = satisfaction_values.get(label, 3)  # Default to neutral
            total_score += value * count
            total_responses += count
        
        return total_score / max(total_responses, 1)
    
    def _suggest_additional_charts(self, feature_data: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
        """Suggest additional visualization opportunities"""
        suggestions = []
        
        # Suggest correlation matrix if multiple categorical features
        categorical_features = [f for f, data in feature_data.items()
                              if data.get('type') == 'MCQ']
        
        if len(categorical_features) >= 3:
            suggestions.append({
                'type': 'correlation_heatmap',
                'title': 'Feature Correlation Matrix',
                'description': f"Analyze relationships between {len(categorical_features)} categorical variables",
                'features': categorical_features
            })
        
        # Suggest trend analysis if satisfaction data exists
        satisfaction_features = [f for f, data in feature_data.items()
                               if data.get('category') in ['satisfaction', 'rating']]
        
        if satisfaction_features:
            suggestions.append({
                'type': 'satisfaction_radar',
                'title': 'Satisfaction Radar Chart',
                'description': f"Multi-dimensional view of {len(satisfaction_features)} satisfaction metrics",
                'features': satisfaction_features
            })
        
        # Suggest text analysis for descriptive features
        text_features = [f for f, data in feature_data.items()
                        if data.get('type') == 'Descriptive']
        
        if text_features:
            suggestions.append({
                'type': 'sentiment_analysis',
                'title': 'Sentiment Analysis Visualization',
                'description': f"Analyze sentiment patterns in {len(text_features)} text responses",
                'features': text_features
            })
        
        return suggestions
    
    def _create_summary(self, feature: str, viz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create data summary for a feature"""
        metadata = viz_data.get('metadata', {})
        data_type = viz_data.get('type', 'unknown')
        
        summary = {
            'feature': feature,
            'question': viz_data.get('question', ''),
            'type': data_type,
            'total_responses': len(viz_data.get('responses', []))
        }
        
        if data_type == 'MCQ':
            distribution = metadata.get('distribution', {})
            summary.update({
                'unique_values': len(distribution),
                'most_common': max(distribution, key=distribution.get) if distribution else None,
                'diversity_score': len(distribution) / max(sum(distribution.values()), 1)
            })
            
        elif data_type == 'Descriptive':
            summary.update({
                'avg_response_length': metadata.get('avg_length', 0),
                'avg_word_count': metadata.get('avg_word_count', 0)
            })
        
        return summary