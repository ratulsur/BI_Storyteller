"""
Data Chat Module
Interactive chat interface for querying and exploring data
"""

import json
import re
from typing import List, Dict, Any, Optional
from collections import Counter, defaultdict
import statistics


class DataChat:
    """Interactive chat interface for data exploration"""
    
    def __init__(self):
        # Query patterns and their corresponding analysis functions
        self.query_patterns = {
            # Summary queries
            r'(how many|count|total).*(response|answer|people|customer)': self._handle_count_query,
            r'(what|show).*(most|top|highest|popular|common)': self._handle_top_query,
            r'(what|show).*(least|bottom|lowest|rare|uncommon)': self._handle_bottom_query,
            
            # Satisfaction queries
            r'(satisfaction|satisfied|rating|rate)': self._handle_satisfaction_query,
            r'(happy|pleased|content)': self._handle_positive_sentiment_query,
            r'(unhappy|dissatisfied|disappointed|frustrated)': self._handle_negative_sentiment_query,
            
            # Demographic queries
            r'(age|gender|income|education|demographic)': self._handle_demographic_query,
            r'(who|which group|what type).*customer': self._handle_customer_profile_query,
            
            # Comparison queries
            r'(compare|difference|versus|vs|between)': self._handle_comparison_query,
            r'(correlation|relationship|connection)': self._handle_correlation_query,
            
            # Trend queries
            r'(trend|over time|change|improve|decline)': self._handle_trend_query,
            r'(predict|forecast|future|next)': self._handle_prediction_query,
            
            # Insight queries
            r'(why|reason|cause|factor)': self._handle_insight_query,
            r'(recommend|suggest|advice|should)': self._handle_recommendation_query,
            
            # Statistical queries
            r'(average|mean|median|typical)': self._handle_average_query,
            r'(percent|percentage|ratio|proportion)': self._handle_percentage_query,
        }
        
        # Context for maintaining conversation state
        self.conversation_context = {
            'last_query': '',
            'last_results': {},
            'focus_area': None,
            'user_interests': []
        }
    
    def process_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Process user query and return analysis results"""
        query_lower = query.lower().strip()
        
        # Update conversation context
        self.conversation_context['last_query'] = query_lower
        
        # Handle greeting/help queries
        if any(word in query_lower for word in ['hello', 'hi', 'help', 'what can you do']):
            return self._handle_help_query()
        
        # Find matching pattern and execute corresponding handler
        for pattern, handler in self.query_patterns.items():
            if re.search(pattern, query_lower):
                try:
                    result = handler(data, query_lower)
                    self.conversation_context['last_results'] = result
                    return result
                except Exception as e:
                    return f"Sorry, I encountered an error processing your query: {str(e)}"
        
        # If no pattern matches, provide general analysis
        return self._handle_general_query(data, query_lower)
    
    def _handle_help_query(self) -> str:
        """Handle help and greeting queries"""
        return """Hello! I can help you explore your survey data. Here are some things you can ask me:

📊 **Data Overview:**
- "How many responses do we have?"
- "What's the most common response?"
- "Show me the summary"

😊 **Satisfaction Analysis:**
- "What's our satisfaction rating?"
- "Who are the most satisfied customers?"
- "What makes customers unhappy?"

👥 **Demographics:**
- "What age groups responded?"
- "Show me customer profiles"
- "Compare different demographics"

📈 **Trends & Insights:**
- "What are the main trends?"
- "Why are customers satisfied/dissatisfied?"
- "What do you recommend?"

Just ask naturally - I'll do my best to help you understand your data!"""
    
    def _handle_count_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle counting queries"""
        total_responses = len(data)
        
        # Count by different dimensions
        question_counts = defaultdict(int)
        category_counts = defaultdict(int)
        
        for response in data:
            answers = response.get('answers', {})
            for q_id, answer_data in answers.items():
                if answer_data.get('answer'):
                    question_counts[answer_data.get('question', 'Unknown')] += 1
                    category_counts[answer_data.get('category', 'general')] += 1
        
        result = f"📊 **Response Count Analysis**\n\n"
        result += f"**Total Responses:** {total_responses}\n\n"
        
        if category_counts:
            result += "**Responses by Category:**\n"
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                result += f"- {category.title()}: {count} responses\n"
        
        return result
    
    def _handle_top_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle queries about top/most common responses"""
        all_responses = defaultdict(list)
        
        # Collect all responses by category
        for response in data:
            answers = response.get('answers', {})
            for q_id, answer_data in answers.items():
                answer = answer_data.get('answer', '')
                category = answer_data.get('category', 'general')
                
                if answer and answer_data.get('question_type') == 'MCQ':
                    all_responses[category].append(answer)
        
        result = "🔝 **Most Popular Responses**\n\n"
        
        for category, responses in all_responses.items():
            if responses:
                response_counts = Counter(responses)
                top_3 = response_counts.most_common(3)
                
                result += f"**{category.title()} Questions:**\n"
                for i, (response, count) in enumerate(top_3, 1):
                    percentage = (count / len(responses)) * 100
                    result += f"{i}. {response} ({count} responses, {percentage:.1f}%)\n"
                result += "\n"
        
        return result
    
    def _handle_bottom_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle queries about least common responses"""
        all_responses = defaultdict(list)
        
        # Collect all responses by category
        for response in data:
            answers = response.get('answers', {})
            for q_id, answer_data in answers.items():
                answer = answer_data.get('answer', '')
                category = answer_data.get('category', 'general')
                
                if answer and answer_data.get('question_type') == 'MCQ':
                    all_responses[category].append(answer)
        
        result = "📉 **Least Common Responses**\n\n"
        
        for category, responses in all_responses.items():
            if responses:
                response_counts = Counter(responses)
                # Get least common (but not zero counts)
                sorted_responses = sorted(response_counts.items(), key=lambda x: x[1])
                bottom_3 = sorted_responses[:3]
                
                result += f"**{category.title()} Questions:**\n"
                for i, (response, count) in enumerate(bottom_3, 1):
                    percentage = (count / len(responses)) * 100
                    result += f"{i}. {response} ({count} responses, {percentage:.1f}%)\n"
                result += "\n"
        
        return result
    
    def _handle_satisfaction_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle satisfaction-related queries"""
        satisfaction_responses = []
        satisfaction_questions = []
        
        for response in data:
            answers = response.get('answers', {})
            for q_id, answer_data in answers.items():
                category = answer_data.get('category', 'general')
                answer = answer_data.get('answer', '')
                
                if category in ['satisfaction', 'rating'] and answer:
                    satisfaction_responses.append(answer)
                    satisfaction_questions.append(answer_data.get('question', 'Unknown'))
        
        if not satisfaction_responses:
            return "I couldn't find any satisfaction or rating questions in your data."
        
        # Calculate satisfaction metrics
        satisfaction_counts = Counter(satisfaction_responses)
        total = len(satisfaction_responses)
        
        # Convert to scores for average calculation
        score_mapping = {
            'Very Satisfied': 5, 'Satisfied': 4, 'Neutral': 3,
            'Dissatisfied': 2, 'Very Dissatisfied': 1,
            'Excellent': 5, 'Good': 4, 'Average': 3,
            'Poor': 2, 'Very Poor': 1
        }
        
        scores = [score_mapping.get(resp, 3) for resp in satisfaction_responses]
        avg_score = statistics.mean(scores) if scores else 0
        
        # Calculate satisfaction rate (4-5 scores)
        high_satisfaction = sum(1 for score in scores if score >= 4)
        satisfaction_rate = (high_satisfaction / len(scores)) * 100 if scores else 0
        
        result = f"😊 **Satisfaction Analysis**\n\n"
        result += f"**Overall Satisfaction Score:** {avg_score:.1f}/5.0\n"
        result += f"**Satisfaction Rate:** {satisfaction_rate:.1f}% (satisfied or very satisfied)\n\n"
        
        result += "**Detailed Breakdown:**\n"
        for response, count in satisfaction_counts.most_common():
            percentage = (count / total) * 100
            result += f"- {response}: {count} ({percentage:.1f}%)\n"
        
        # Add insights
        result += f"\n**Insights:**\n"
        if avg_score >= 4.0:
            result += "✅ Excellent satisfaction levels - customers are very happy!\n"
        elif avg_score >= 3.5:
            result += "✅ Good satisfaction levels with room for improvement\n"
        elif avg_score >= 3.0:
            result += "⚠️ Moderate satisfaction - investigate improvement opportunities\n"
        else:
            result += "🚨 Low satisfaction levels - immediate action needed\n"
        
        return result
    
    def _handle_demographic_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle demographic-related queries"""
        demographics = defaultdict(list)
        
        for response in data:
            answers = response.get('answers', {})
            for q_id, answer_data in answers.items():
                if answer_data.get('category') == 'demographic':
                    question = answer_data.get('question', '').lower()
                    answer = answer_data.get('answer', '')
                    
                    if 'age' in question:
                        demographics['Age'].append(answer)
                    elif 'gender' in question:
                        demographics['Gender'].append(answer)
                    elif 'income' in question:
                        demographics['Income'].append(answer)
                    elif 'education' in question:
                        demographics['Education'].append(answer)
                    else:
                        demographics['Other Demographics'].append(answer)
        
        if not demographics:
            return "I couldn't find demographic information in your data."
        
        result = "👥 **Demographic Breakdown**\n\n"
        
        for demo_type, values in demographics.items():
            if values:
                value_counts = Counter(values)
                total = len(values)
                
                result += f"**{demo_type}:**\n"
                for value, count in value_counts.most_common():
                    percentage = (count / total) * 100
                    result += f"- {value}: {count} ({percentage:.1f}%)\n"
                result += "\n"
        
        # Add diversity insights
        result += "**Insights:**\n"
        for demo_type, values in demographics.items():
            unique_values = len(set(values))
            if unique_values > 3:
                result += f"✅ Good diversity in {demo_type} ({unique_values} categories)\n"
            elif unique_values <= 2:
                result += f"⚠️ Limited diversity in {demo_type} - consider broader outreach\n"
        
        return result
    
    def _handle_comparison_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle comparison queries between different groups"""
        # Try to identify what to compare
        demographics = ['age', 'gender', 'income', 'education']
        outcomes = ['satisfaction', 'rating']
        
        # Find demographic and outcome variables
        demo_data = {}
        outcome_data = {}
        
        for response in data:
            answers = response.get('answers', {})
            response_demo = {}
            response_outcomes = {}
            
            for q_id, answer_data in answers.items():
                category = answer_data.get('category', 'general')
                question = answer_data.get('question', '').lower()
                answer = answer_data.get('answer', '')
                
                if category == 'demographic' and answer:
                    for demo in demographics:
                        if demo in question:
                            response_demo[demo] = answer
                            break
                
                elif category in ['satisfaction', 'rating'] and answer:
                    # Convert to score
                    score_mapping = {
                        'Very Satisfied': 5, 'Satisfied': 4, 'Neutral': 3,
                        'Dissatisfied': 2, 'Very Dissatisfied': 1,
                        'Excellent': 5, 'Good': 4, 'Average': 3,
                        'Poor': 2, 'Very Poor': 1
                    }
                    score = score_mapping.get(answer, 3)
                    response_outcomes['satisfaction'] = score
            
            # Store grouped data
            for demo_type, demo_value in response_demo.items():
                if demo_type not in demo_data:
                    demo_data[demo_type] = defaultdict(list)
                
                for outcome_type, outcome_value in response_outcomes.items():
                    demo_data[demo_type][demo_value].append(outcome_value)
        
        if not demo_data:
            return "I need demographic and satisfaction data to make comparisons."
        
        result = "⚖️ **Group Comparison Analysis**\n\n"
        
        # Compare satisfaction across demographic groups
        for demo_type, groups in demo_data.items():
            if len(groups) > 1:
                result += f"**Satisfaction by {demo_type.title()}:**\n"
                
                group_averages = {}
                for group, scores in groups.items():
                    if scores:
                        avg_score = statistics.mean(scores)
                        group_averages[group] = avg_score
                        result += f"- {group}: {avg_score:.1f}/5.0 ({len(scores)} responses)\n"
                
                # Find best and worst performing groups
                if group_averages:
                    best_group = max(group_averages, key=group_averages.get)
                    worst_group = min(group_averages, key=group_averages.get)
                    
                    result += f"\n**Key Findings:**\n"
                    result += f"🏆 Highest satisfaction: {best_group} ({group_averages[best_group]:.1f}/5.0)\n"
                    result += f"📉 Lowest satisfaction: {worst_group} ({group_averages[worst_group]:.1f}/5.0)\n"
                    
                    difference = group_averages[best_group] - group_averages[worst_group]
                    if difference > 0.5:
                        result += f"⚠️ Significant gap detected ({difference:.1f} points)\n"
                
                result += "\n"
        
        return result
    
    def _handle_trend_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle trend and time-based queries"""
        # Group responses by date
        daily_responses = defaultdict(int)
        daily_satisfaction = defaultdict(list)
        
        for response in data:
            timestamp = response.get('timestamp', '')
            if timestamp:
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%Y-%m-%d')
                    daily_responses[date_str] += 1
                    
                    # Extract satisfaction scores for this day
                    answers = response.get('answers', {})
                    for q_id, answer_data in answers.items():
                        if answer_data.get('category') in ['satisfaction', 'rating']:
                            answer = answer_data.get('answer', '')
                            if answer:
                                score_mapping = {
                                    'Very Satisfied': 5, 'Satisfied': 4, 'Neutral': 3,
                                    'Dissatisfied': 2, 'Very Dissatisfied': 1,
                                    'Excellent': 5, 'Good': 4, 'Average': 3,
                                    'Poor': 2, 'Very Poor': 1
                                }
                                score = score_mapping.get(answer, 3)
                                daily_satisfaction[date_str].append(score)
                except:
                    pass
        
        if not daily_responses:
            return "I don't have timestamp information to analyze trends over time."
        
        result = "📈 **Trend Analysis**\n\n"
        
        # Response volume trends
        sorted_dates = sorted(daily_responses.keys())
        if len(sorted_dates) > 1:
            first_day_responses = daily_responses[sorted_dates[0]]
            last_day_responses = daily_responses[sorted_dates[-1]]
            
            result += f"**Response Volume:**\n"
            result += f"- First day ({sorted_dates[0]}): {first_day_responses} responses\n"
            result += f"- Last day ({sorted_dates[-1]}): {last_day_responses} responses\n"
            
            if last_day_responses > first_day_responses:
                result += "📈 Increasing response trend\n\n"
            elif last_day_responses < first_day_responses:
                result += "📉 Decreasing response trend\n\n"
            else:
                result += "➡️ Stable response trend\n\n"
        
        # Satisfaction trends
        daily_avg_satisfaction = {}
        for date, scores in daily_satisfaction.items():
            if scores:
                daily_avg_satisfaction[date] = statistics.mean(scores)
        
        if len(daily_avg_satisfaction) > 1:
            sorted_sat_dates = sorted(daily_avg_satisfaction.keys())
            first_day_sat = daily_avg_satisfaction[sorted_sat_dates[0]]
            last_day_sat = daily_avg_satisfaction[sorted_sat_dates[-1]]
            
            result += f"**Satisfaction Trends:**\n"
            result += f"- First day satisfaction: {first_day_sat:.1f}/5.0\n"
            result += f"- Last day satisfaction: {last_day_sat:.1f}/5.0\n"
            
            satisfaction_change = last_day_sat - first_day_sat
            if satisfaction_change > 0.2:
                result += f"😊 Improving satisfaction trend (+{satisfaction_change:.1f} points)\n"
            elif satisfaction_change < -0.2:
                result += f"😟 Declining satisfaction trend ({satisfaction_change:.1f} points)\n"
            else:
                result += "➡️ Stable satisfaction trend\n"
        
        return result
    
    def _handle_insight_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle why/insight queries"""
        # Analyze patterns in satisfaction and text responses
        satisfaction_insights = []
        text_insights = []
        
        # Group responses by satisfaction level
        satisfaction_groups = defaultdict(list)
        
        for response in data:
            answers = response.get('answers', {})
            satisfaction_level = None
            text_responses = []
            
            for q_id, answer_data in answers.items():
                category = answer_data.get('category', 'general')
                answer = answer_data.get('answer', '')
                
                if category in ['satisfaction', 'rating'] and answer:
                    satisfaction_level = answer
                elif answer_data.get('question_type') == 'Descriptive' and answer:
                    text_responses.append(answer.lower())
            
            if satisfaction_level:
                satisfaction_groups[satisfaction_level].extend(text_responses)
        
        result = "🔍 **Insights & Patterns**\n\n"
        
        # Analyze text patterns by satisfaction level
        positive_words = ['good', 'great', 'excellent', 'love', 'amazing', 'helpful', 'easy', 'fast', 'professional']
        negative_words = ['bad', 'poor', 'slow', 'difficult', 'expensive', 'confusing', 'problem', 'issue', 'terrible']
        
        for satisfaction_level, text_responses in satisfaction_groups.items():
            if text_responses:
                all_text = ' '.join(text_responses)
                
                positive_mentions = sum(1 for word in positive_words if word in all_text)
                negative_mentions = sum(1 for word in negative_words if word in all_text)
                
                result += f"**{satisfaction_level} Customers:**\n"
                result += f"- {len(text_responses)} text responses analyzed\n"
                
                if positive_mentions > negative_mentions:
                    result += f"- Generally positive language ({positive_mentions} positive vs {negative_mentions} negative words)\n"
                elif negative_mentions > positive_mentions:
                    result += f"- Generally negative language ({negative_mentions} negative vs {positive_mentions} positive words)\n"
                else:
                    result += f"- Neutral language patterns\n"
                
                # Find common themes
                words = all_text.split()
                word_freq = Counter(word for word in words if len(word) > 4)
                common_words = word_freq.most_common(3)
                
                if common_words:
                    result += f"- Common themes: {', '.join([word for word, count in common_words])}\n"
                
                result += "\n"
        
        # General insights
        result += "**Key Insights:**\n"
        
        if 'Very Satisfied' in satisfaction_groups or 'Satisfied' in satisfaction_groups:
            result += "✅ Satisfied customers mention positive experiences more frequently\n"
        
        if 'Dissatisfied' in satisfaction_groups or 'Very Dissatisfied' in satisfaction_groups:
            result += "⚠️ Dissatisfied customers highlight specific problems and pain points\n"
        
        # Compare word usage between satisfied and dissatisfied
        satisfied_text = ' '.join(satisfaction_groups.get('Very Satisfied', []) + satisfaction_groups.get('Satisfied', []))
        dissatisfied_text = ' '.join(satisfaction_groups.get('Dissatisfied', []) + satisfaction_groups.get('Very Dissatisfied', []))
        
        if satisfied_text and dissatisfied_text:
            satisfied_positive = sum(1 for word in positive_words if word in satisfied_text)
            dissatisfied_negative = sum(1 for word in negative_words if word in dissatisfied_text)
            
            if satisfied_positive > 0:
                result += f"💡 Satisfied customers use {satisfied_positive} positive descriptors\n"
            if dissatisfied_negative > 0:
                result += f"💡 Dissatisfied customers use {dissatisfied_negative} negative descriptors\n"
        
        return result
    
    def _handle_recommendation_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle recommendation queries"""
        # Analyze satisfaction levels and patterns
        satisfaction_distribution = Counter()
        improvement_areas = []
        strengths = []
        
        for response in data:
            answers = response.get('answers', {})
            for q_id, answer_data in answers.items():
                category = answer_data.get('category', 'general')
                answer = answer_data.get('answer', '')
                
                if category in ['satisfaction', 'rating'] and answer:
                    satisfaction_distribution[answer] += 1
        
        total_responses = sum(satisfaction_distribution.values())
        if total_responses == 0:
            return "I need satisfaction data to provide recommendations."
        
        # Calculate satisfaction metrics
        dissatisfied_count = (satisfaction_distribution.get('Dissatisfied', 0) + 
                            satisfaction_distribution.get('Very Dissatisfied', 0))
        satisfied_count = (satisfaction_distribution.get('Satisfied', 0) + 
                         satisfaction_distribution.get('Very Satisfied', 0))
        
        dissatisfied_rate = (dissatisfied_count / total_responses) * 100
        satisfied_rate = (satisfied_count / total_responses) * 100
        
        result = "💡 **Recommendations**\n\n"
        
        # Strategic recommendations based on satisfaction levels
        if satisfied_rate > 70:
            result += "🎉 **Maintain Excellence:**\n"
            result += "- Continue current strategies - high satisfaction levels\n"
            result += "- Leverage satisfied customers for referrals and testimonials\n"
            result += "- Document and replicate successful practices\n\n"
        
        if dissatisfied_rate > 20:
            result += "🚨 **Immediate Action Required:**\n"
            result += "- High dissatisfaction rate needs urgent attention\n"
            result += "- Conduct detailed analysis of dissatisfied customer feedback\n"
            result += "- Implement quick wins to address common complaints\n\n"
        
        if satisfaction_distribution.get('Neutral', 0) / total_responses > 0.3:
            result += "⚡ **Opportunity for Improvement:**\n"
            result += "- Large neutral segment represents untapped potential\n"
            result += "- Focus on converting neutral customers to satisfied\n"
            result += "- Enhance engagement and value proposition\n\n"
        
        # Data collection recommendations
        result += "📊 **Data & Analysis Recommendations:**\n"
        
        # Check data quality
        demographic_coverage = 0
        text_response_coverage = 0
        
        for response in data:
            answers = response.get('answers', {})
            has_demo = any(answer_data.get('category') == 'demographic' for answer_data in answers.values())
            has_text = any(answer_data.get('question_type') == 'Descriptive' for answer_data in answers.values())
            
            if has_demo:
                demographic_coverage += 1
            if has_text:
                text_response_coverage += 1
        
        demo_rate = (demographic_coverage / len(data)) * 100 if data else 0
        text_rate = (text_response_coverage / len(data)) * 100 if data else 0
        
        if demo_rate < 80:
            result += "- Improve demographic data collection for better segmentation\n"
        
        if text_rate < 60:
            result += "- Increase open-ended questions for deeper insights\n"
        
        if len(data) < 100:
            result += "- Expand sample size for more reliable insights\n"
        
        result += "\n🎯 **Next Steps:**\n"
        result += "1. Prioritize addressing dissatisfied customer concerns\n"
        result += "2. Leverage strengths identified in satisfied customer feedback\n"
        result += "3. Develop targeted strategies for neutral customers\n"
        result += "4. Establish regular monitoring and feedback loops\n"
        
        return result
    
    def _handle_general_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle general queries that don't match specific patterns"""
        # Provide general data summary
        total_responses = len(data)
        
        # Count different types of data
        satisfaction_responses = 0
        demographic_responses = 0
        text_responses = 0
        
        for response in data:
            answers = response.get('answers', {})
            for q_id, answer_data in answers.items():
                category = answer_data.get('category', 'general')
                question_type = answer_data.get('question_type', 'unknown')
                
                if category in ['satisfaction', 'rating']:
                    satisfaction_responses += 1
                elif category == 'demographic':
                    demographic_responses += 1
                elif question_type == 'Descriptive':
                    text_responses += 1
        
        result = f"📋 **Data Overview**\n\n"
        result += f"I found {total_responses} survey responses with:\n"
        result += f"- {satisfaction_responses} satisfaction/rating responses\n"
        result += f"- {demographic_responses} demographic responses\n"
        result += f"- {text_responses} text responses\n\n"
        
        result += "**What would you like to explore?**\n"
        result += "- Ask about satisfaction levels\n"
        result += "- Explore demographic breakdowns\n"
        result += "- Compare different groups\n"
        result += "- Look for trends over time\n"
        result += "- Get recommendations for improvement\n\n"
        
        result += "Just ask me naturally - for example:\n"
        result += "- 'What's our satisfaction rating?'\n"
        result += "- 'Show me the age breakdown'\n"
        result += "- 'Compare satisfaction by gender'\n"
        
        return result
    
    def _handle_positive_sentiment_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle queries about positive sentiment/happiness"""
        return self._handle_satisfaction_query(data, query)
    
    def _handle_negative_sentiment_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle queries about negative sentiment/dissatisfaction"""
        # Focus on dissatisfied responses
        dissatisfied_responses = []
        
        for response in data:
            answers = response.get('answers', {})
            for q_id, answer_data in answers.items():
                category = answer_data.get('category', 'general')
                answer = answer_data.get('answer', '')
                
                if (category in ['satisfaction', 'rating'] and 
                    answer in ['Dissatisfied', 'Very Dissatisfied', 'Poor', 'Very Poor']):
                    dissatisfied_responses.append(response)
                    break
        
        if not dissatisfied_responses:
            return "Great news! I didn't find any clearly dissatisfied responses in your data."
        
        result = f"😟 **Dissatisfied Customer Analysis**\n\n"
        result += f"Found {len(dissatisfied_responses)} dissatisfied responses ({(len(dissatisfied_responses)/len(data)*100):.1f}% of total)\n\n"
        
        # Analyze text from dissatisfied customers
        dissatisfied_text = []
        for response in dissatisfied_responses:
            answers = response.get('answers', {})
            for q_id, answer_data in answers.items():
                if answer_data.get('question_type') == 'Descriptive':
                    text = answer_data.get('answer', '')
                    if text:
                        dissatisfied_text.append(text.lower())
        
        if dissatisfied_text:
            # Find common complaint themes
            all_text = ' '.join(dissatisfied_text)
            complaint_words = ['slow', 'expensive', 'difficult', 'confusing', 'poor', 'bad', 'problem', 'issue', 'terrible', 'awful']
            
            mentioned_issues = []
            for word in complaint_words:
                if word in all_text:
                    mentioned_issues.append(word)
            
            if mentioned_issues:
                result += f"**Common Issues Mentioned:**\n"
                for issue in mentioned_issues[:5]:
                    result += f"- {issue.title()}\n"
                result += "\n"
        
        result += "**Recommendations:**\n"
        result += "🎯 Prioritize addressing these dissatisfied customers\n"
        result += "📞 Consider direct outreach to understand specific issues\n"
        result += "🔧 Implement quick fixes for commonly mentioned problems\n"
        result += "📊 Monitor satisfaction trends to prevent future dissatisfaction\n"
        
        return result
    
    def _handle_customer_profile_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle customer profile queries"""
        return self._handle_demographic_query(data, query)
    
    def _handle_correlation_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle correlation and relationship queries"""
        return self._handle_comparison_query(data, query)
    
    def _handle_prediction_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle prediction and forecasting queries"""
        return self._handle_trend_query(data, query)
    
    def _handle_average_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle average/statistical queries"""
        return self._handle_satisfaction_query(data, query)
    
    def _handle_percentage_query(self, data: List[Dict[str, Any]], query: str) -> str:
        """Handle percentage and proportion queries"""
        return self._handle_satisfaction_query(data, query)