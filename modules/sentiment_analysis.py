"""
Sentiment Analysis Module
Analyzes sentiment in text responses using lexicon-based approach
"""

import json
import re
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict


class SentimentAnalyzer:
    """Analyze sentiment in survey text responses"""
    
    def __init__(self):
        # Predefined sentiment lexicons
        self.positive_words = {
            'excellent', 'great', 'good', 'amazing', 'fantastic', 'wonderful', 'perfect',
            'outstanding', 'superb', 'brilliant', 'awesome', 'love', 'like', 'enjoy',
            'satisfied', 'happy', 'pleased', 'delighted', 'impressed', 'recommend',
            'helpful', 'useful', 'valuable', 'effective', 'efficient', 'reliable',
            'quality', 'professional', 'friendly', 'quick', 'fast', 'easy', 'smooth',
            'convenient', 'affordable', 'reasonable', 'worth', 'benefit', 'advantage'
        }
        
        self.negative_words = {
            'terrible', 'awful', 'bad', 'horrible', 'disgusting', 'hate', 'dislike',
            'disappointing', 'frustrated', 'annoying', 'useless', 'worthless',
            'dissatisfied', 'unhappy', 'upset', 'angry', 'furious', 'worst', 'poor',
            'slow', 'difficult', 'hard', 'complicated', 'confusing', 'expensive',
            'overpriced', 'unreliable', 'broken', 'problem', 'issue', 'bug', 'error',
            'fail', 'failure', 'waste', 'regret', 'sorry', 'complain', 'complaint'
        }
        
        self.intensifiers = {
            'very': 1.5, 'really': 1.4, 'extremely': 1.8, 'incredibly': 1.7,
            'absolutely': 1.6, 'completely': 1.5, 'totally': 1.4, 'quite': 1.2,
            'pretty': 1.1, 'fairly': 1.1, 'rather': 1.1, 'somewhat': 0.8,
            'slightly': 0.7, 'a bit': 0.7, 'kind of': 0.6, 'sort of': 0.6
        }
        
        self.negators = {
            'not', 'no', 'never', 'nothing', 'nobody', 'nowhere', 'neither',
            'none', 'without', 'lacking', 'missing', 'absent', "don't", "won't",
            "can't", "couldn't", "shouldn't", "wouldn't", "isn't", "aren't"
        }
    
    def analyze_sentiment(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive sentiment analysis on text responses"""
        print("😊 Analyzing sentiment in text responses...")
        
        results = {
            'overall_sentiment': {},
            'sentiment_distribution': {},
            'sentiment_by_category': {},
            'sentiment_trends': {},
            'emotional_keywords': {},
            'sentiment_scores': {},
            'insights': [],
            'visualizations': []
        }
        
        # Extract text responses
        text_data = self._extract_text_responses(data)
        
        if not text_data['responses']:
            return {
                'error': 'No text responses found for sentiment analysis',
                'distribution': {'positive': 0, 'neutral': 0, 'negative': 0}
            }
        
        # Analyze sentiment for all responses
        sentiment_results = self._analyze_text_sentiment(text_data['responses'])
        
        # Calculate overall sentiment distribution
        results['sentiment_distribution'] = self._calculate_sentiment_distribution(sentiment_results)
        
        # Analyze sentiment by question category
        results['sentiment_by_category'] = self._analyze_sentiment_by_category(text_data, sentiment_results)
        
        # Extract emotional keywords
        results['emotional_keywords'] = self._extract_emotional_keywords(text_data['responses'])
        
        # Calculate detailed sentiment scores
        results['sentiment_scores'] = self._calculate_detailed_scores(sentiment_results)
        
        # Analyze sentiment trends (if timestamps available)
        results['sentiment_trends'] = self._analyze_sentiment_trends(data, sentiment_results)
        
        # Generate insights
        results['insights'] = self._generate_sentiment_insights(results)
        
        # Suggest visualizations
        results['visualizations'] = self._suggest_sentiment_visualizations(results)
        
        return results
    
    def _extract_text_responses(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract all text responses from survey data"""
        text_data = {
            'responses': [],
            'categories': {},
            'response_metadata': []
        }
        
        for response in data:
            answers = response.get('answers', {})
            response_timestamp = response.get('timestamp', '')
            
            for q_id, answer_data in answers.items():
                if answer_data.get('question_type') == 'Descriptive':
                    answer_text = answer_data.get('answer', '')
                    
                    if answer_text and len(answer_text.strip()) > 0:
                        category = answer_data.get('category', 'general')
                        
                        text_data['responses'].append(answer_text)
                        text_data['response_metadata'].append({
                            'question_id': q_id,
                            'question': answer_data.get('question', ''),
                            'category': category,
                            'timestamp': response_timestamp,
                            'response_id': response.get('response_id', '')
                        })
                        
                        if category not in text_data['categories']:
                            text_data['categories'][category] = []
                        text_data['categories'][category].append(answer_text)
        
        return text_data
    
    def _analyze_text_sentiment(self, responses: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment for each text response"""
        sentiment_results = []
        
        for i, response_text in enumerate(responses):
            sentiment = self._calculate_response_sentiment(response_text)
            
            sentiment_results.append({
                'index': i,
                'text': response_text,
                'sentiment_score': sentiment['score'],
                'sentiment_label': sentiment['label'],
                'confidence': sentiment['confidence'],
                'positive_words': sentiment['positive_words'],
                'negative_words': sentiment['negative_words'],
                'word_count': len(response_text.split())
            })
        
        return sentiment_results
    
    def _calculate_response_sentiment(self, text: str) -> Dict[str, Any]:
        """Calculate sentiment for a single response"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        sentiment_score = 0
        positive_words_found = []
        negative_words_found = []
        
        i = 0
        while i < len(words):
            word = words[i]
            
            # Check for negation
            is_negated = False
            if i > 0 and words[i-1] in self.negators:
                is_negated = True
            elif i > 1 and words[i-2] in self.negators:
                is_negated = True
            
            # Check for intensifiers
            intensifier = 1.0
            if i > 0 and words[i-1] in self.intensifiers:
                intensifier = self.intensifiers[words[i-1]]
            elif i > 1 and words[i-2] in self.intensifiers:
                intensifier = self.intensifiers[words[i-2]]
            
            # Calculate word sentiment
            if word in self.positive_words:
                score = 1 * intensifier
                if is_negated:
                    score = -score
                sentiment_score += score
                positive_words_found.append(word)
            
            elif word in self.negative_words:
                score = -1 * intensifier
                if is_negated:
                    score = -score
                sentiment_score += score
                negative_words_found.append(word)
            
            i += 1
        
        # Normalize score by text length
        word_count = len(words)
        if word_count > 0:
            normalized_score = sentiment_score / word_count
        else:
            normalized_score = 0
        
        # Determine sentiment label and confidence
        if normalized_score > 0.1:
            label = 'positive'
            confidence = min(abs(normalized_score) * 2, 1.0)
        elif normalized_score < -0.1:
            label = 'negative'
            confidence = min(abs(normalized_score) * 2, 1.0)
        else:
            label = 'neutral'
            confidence = 1.0 - abs(normalized_score)
        
        return {
            'score': normalized_score,
            'label': label,
            'confidence': confidence,
            'positive_words': positive_words_found,
            'negative_words': negative_words_found
        }
    
    def _calculate_sentiment_distribution(self, sentiment_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall sentiment distribution"""
        total_responses = len(sentiment_results)
        
        if total_responses == 0:
            return {'positive': 0, 'neutral': 0, 'negative': 0}
        
        sentiment_counts = Counter(result['sentiment_label'] for result in sentiment_results)
        
        distribution = {
            'positive': sentiment_counts.get('positive', 0),
            'neutral': sentiment_counts.get('neutral', 0),
            'negative': sentiment_counts.get('negative', 0)
        }
        
        # Calculate percentages
        distribution_pct = {
            sentiment: (count / total_responses) * 100
            for sentiment, count in distribution.items()
        }
        
        # Calculate average sentiment score
        avg_score = sum(result['sentiment_score'] for result in sentiment_results) / total_responses
        
        return {
            'counts': distribution,
            'percentages': distribution_pct,
            'total_responses': total_responses,
            'average_sentiment_score': avg_score
        }
    
    def _analyze_sentiment_by_category(self, text_data: Dict[str, Any], 
                                     sentiment_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment breakdown by question category"""
        category_sentiment = {}
        response_metadata = text_data.get('response_metadata', [])
        
        # Group sentiment results by category
        for i, sentiment in enumerate(sentiment_results):
            if i < len(response_metadata):
                metadata = response_metadata[i]
                category = metadata.get('category', 'general')
                
                if category not in category_sentiment:
                    category_sentiment[category] = {
                        'sentiments': [],
                        'questions': set()
                    }
                
                category_sentiment[category]['sentiments'].append(sentiment)
                category_sentiment[category]['questions'].add(metadata.get('question', ''))
        
        # Calculate statistics for each category
        results = {}
        for category, data in category_sentiment.items():
            sentiments = data['sentiments']
            
            if not sentiments:
                continue
            
            sentiment_labels = [s['sentiment_label'] for s in sentiments]
            sentiment_scores = [s['sentiment_score'] for s in sentiments]
            
            label_counts = Counter(sentiment_labels)
            total = len(sentiments)
            
            results[category] = {
                'total_responses': total,
                'question_count': len(data['questions']),
                'distribution': {
                    'positive': (label_counts.get('positive', 0) / total) * 100,
                    'neutral': (label_counts.get('neutral', 0) / total) * 100,
                    'negative': (label_counts.get('negative', 0) / total) * 100
                },
                'average_sentiment_score': sum(sentiment_scores) / len(sentiment_scores),
                'dominant_sentiment': max(label_counts, key=label_counts.get) if label_counts else 'neutral'
            }
        
        return results
    
    def _extract_emotional_keywords(self, responses: List[str]) -> Dict[str, Any]:
        """Extract and analyze emotional keywords from responses"""
        all_positive_words = []
        all_negative_words = []
        
        for response in responses:
            text_lower = response.lower()
            words = re.findall(r'\b\w+\b', text_lower)
            
            for word in words:
                if word in self.positive_words:
                    all_positive_words.append(word)
                elif word in self.negative_words:
                    all_negative_words.append(word)
        
        positive_freq = Counter(all_positive_words)
        negative_freq = Counter(all_negative_words)
        
        return {
            'most_common_positive': positive_freq.most_common(10),
            'most_common_negative': negative_freq.most_common(10),
            'total_positive_mentions': len(all_positive_words),
            'total_negative_mentions': len(all_negative_words),
            'emotional_word_ratio': len(all_positive_words) / max(len(all_negative_words), 1)
        }
    
    def _calculate_detailed_scores(self, sentiment_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate detailed sentiment scoring metrics"""
        if not sentiment_results:
            return {}
        
        scores = [result['sentiment_score'] for result in sentiment_results]
        confidences = [result['confidence'] for result in sentiment_results]
        
        # Calculate statistical measures
        import statistics
        
        return {
            'mean_sentiment': statistics.mean(scores),
            'median_sentiment': statistics.median(scores),
            'sentiment_std_dev': statistics.stdev(scores) if len(scores) > 1 else 0,
            'sentiment_range': max(scores) - min(scores),
            'average_confidence': statistics.mean(confidences),
            'most_positive_score': max(scores),
            'most_negative_score': min(scores),
            'sentiment_variability': statistics.stdev(scores) / max(abs(statistics.mean(scores)), 0.1) if len(scores) > 1 else 0
        }
    
    def _analyze_sentiment_trends(self, data: List[Dict[str, Any]], 
                                sentiment_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment trends over time"""
        trends = {
            'daily_sentiment': {},
            'trend_analysis': {},
            'sentiment_volatility': {}
        }
        
        # Group sentiment by date
        daily_sentiments = defaultdict(list)
        
        for i, sentiment in enumerate(sentiment_results):
            # Find corresponding response data
            response_data = None
            response_idx = 0
            
            # Match sentiment result to original response
            for response in data:
                answers = response.get('answers', {})
                text_response_count = sum(1 for answer in answers.values() 
                                        if answer.get('question_type') == 'Descriptive' 
                                        and answer.get('answer', '').strip())
                
                if response_idx <= i < response_idx + text_response_count:
                    response_data = response
                    break
                response_idx += text_response_count
            
            if response_data:
                timestamp = response_data.get('timestamp', '')
                if timestamp:
                    try:
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        date_str = date_obj.strftime('%Y-%m-%d')
                        daily_sentiments[date_str].append(sentiment['sentiment_score'])
                    except:
                        pass
        
        # Calculate daily averages
        if daily_sentiments:
            daily_averages = {}
            for date, scores in daily_sentiments.items():
                daily_averages[date] = sum(scores) / len(scores)
            
            trends['daily_sentiment'] = daily_averages
            
            # Analyze trend direction
            if len(daily_averages) > 1:
                sorted_dates = sorted(daily_averages.keys())
                values = [daily_averages[date] for date in sorted_dates]
                
                # Simple trend calculation
                if len(values) >= 2:
                    first_half = values[:len(values)//2]
                    second_half = values[len(values)//2:]
                    
                    first_avg = sum(first_half) / len(first_half)
                    second_avg = sum(second_half) / len(second_half)
                    
                    trend_direction = 'improving' if second_avg > first_avg else 'declining' if second_avg < first_avg else 'stable'
                    trend_magnitude = abs(second_avg - first_avg)
                    
                    trends['trend_analysis'] = {
                        'direction': trend_direction,
                        'magnitude': trend_magnitude,
                        'best_day': max(daily_averages, key=daily_averages.get),
                        'worst_day': min(daily_averages, key=daily_averages.get)
                    }
        
        return trends
    
    def _generate_sentiment_insights(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from sentiment analysis"""
        insights = []
        
        # Overall sentiment insights
        distribution = results.get('sentiment_distribution', {})
        percentages = distribution.get('percentages', {})
        
        if percentages:
            positive_pct = percentages.get('positive', 0)
            negative_pct = percentages.get('negative', 0)
            neutral_pct = percentages.get('neutral', 0)
            
            insights.append(f"Sentiment distribution: {positive_pct:.1f}% positive, {neutral_pct:.1f}% neutral, {negative_pct:.1f}% negative")
            
            if positive_pct > 50:
                insights.append("Predominantly positive sentiment indicates good customer satisfaction")
            elif negative_pct > 30:
                insights.append("High negative sentiment detected - urgent attention needed")
            elif neutral_pct > 60:
                insights.append("High neutral sentiment suggests opportunities for improvement")
        
        # Category-specific insights
        category_sentiment = results.get('sentiment_by_category', {})
        
        for category, data in category_sentiment.items():
            dominant = data.get('dominant_sentiment', 'neutral')
            avg_score = data.get('average_sentiment_score', 0)
            
            if dominant == 'positive':
                insights.append(f"{category.title()} responses show positive sentiment (avg: {avg_score:.2f})")
            elif dominant == 'negative' and avg_score < -0.1:
                insights.append(f"{category.title()} responses show concerning negative sentiment")
        
        # Emotional keywords insights
        emotional_keywords = results.get('emotional_keywords', {})
        positive_words = emotional_keywords.get('most_common_positive', [])
        negative_words = emotional_keywords.get('most_common_negative', [])
        
        if positive_words:
            top_positive = positive_words[0][0]
            insights.append(f"Most mentioned positive word: '{top_positive}'")
        
        if negative_words:
            top_negative = negative_words[0][0]
            insights.append(f"Most mentioned negative word: '{top_negative}' - investigate related issues")
        
        # Trend insights
        sentiment_trends = results.get('sentiment_trends', {})
        trend_analysis = sentiment_trends.get('trend_analysis', {})
        
        if trend_analysis:
            direction = trend_analysis.get('direction', 'stable')
            if direction == 'improving':
                insights.append("Sentiment is improving over time - positive trend")
            elif direction == 'declining':
                insights.append("Sentiment is declining over time - intervention needed")
        
        # Detailed scoring insights
        detailed_scores = results.get('sentiment_scores', {})
        if detailed_scores:
            variability = detailed_scores.get('sentiment_variability', 0)
            if variability > 1.0:
                insights.append("High sentiment variability - mixed customer experiences")
            
            avg_confidence = detailed_scores.get('average_confidence', 0)
            insights.append(f"Sentiment analysis confidence: {avg_confidence:.1%}")
        
        return insights
    
    def _suggest_sentiment_visualizations(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Suggest appropriate visualizations for sentiment data"""
        visualizations = []
        
        # Sentiment distribution pie chart
        distribution = results.get('sentiment_distribution', {})
        if distribution.get('total_responses', 0) > 0:
            visualizations.append({
                'type': 'pie_chart',
                'title': 'Overall Sentiment Distribution',
                'description': 'Pie chart showing distribution of positive, neutral, and negative sentiments',
                'data_source': 'sentiment_distribution'
            })
        
        # Sentiment by category
        category_sentiment = results.get('sentiment_by_category', {})
        if len(category_sentiment) > 1:
            visualizations.append({
                'type': 'stacked_bar',
                'title': 'Sentiment by Question Category',
                'description': 'Stacked bar chart comparing sentiment across different question categories',
                'data_source': 'sentiment_by_category'
            })
        
        # Emotional keywords word cloud
        emotional_keywords = results.get('emotional_keywords', {})
        if emotional_keywords.get('most_common_positive') or emotional_keywords.get('most_common_negative'):
            visualizations.append({
                'type': 'word_cloud',
                'title': 'Emotional Keywords',
                'description': 'Word cloud highlighting most frequently mentioned emotional terms',
                'data_source': 'emotional_keywords'
            })
        
        # Sentiment trends
        sentiment_trends = results.get('sentiment_trends', {})
        if sentiment_trends.get('daily_sentiment'):
            visualizations.append({
                'type': 'line_chart',
                'title': 'Sentiment Trends Over Time',
                'description': 'Line chart showing how sentiment changes over time',
                'data_source': 'sentiment_trends'
            })
        
        # Sentiment score distribution
        detailed_scores = results.get('sentiment_scores', {})
        if detailed_scores:
            visualizations.append({
                'type': 'histogram',
                'title': 'Sentiment Score Distribution',
                'description': 'Histogram showing distribution of sentiment scores',
                'data_source': 'sentiment_scores'
            })
        
        return visualizations