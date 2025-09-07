"""
Trend Analysis Module
Analyzes temporal patterns and trends in survey data
"""

import json
from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import statistics


class TrendAnalyzer:
    """Analyze trends and temporal patterns in data"""
    
    def __init__(self):
        self.time_periods = ['daily', 'weekly', 'monthly']
        self.trend_types = ['increasing', 'decreasing', 'stable', 'cyclical', 'volatile']
    
    def analyze_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive trend analysis"""
        print("📈 Analyzing trends and temporal patterns...")
        
        results = {
            'temporal_patterns': {},
            'satisfaction_trends': {},
            'demographic_trends': {},
            'response_trends': {},
            'seasonal_patterns': {},
            'trend_predictions': {},
            'insights': [],
            'visualizations': []
        }
        
        # Extract temporal data
        temporal_data = self._extract_temporal_data(data)
        
        # Analyze response patterns over time
        results['response_trends'] = self._analyze_response_trends(temporal_data)
        
        # Analyze satisfaction trends
        results['satisfaction_trends'] = self._analyze_satisfaction_trends(temporal_data)
        
        # Analyze demographic trends
        results['demographic_trends'] = self._analyze_demographic_trends(temporal_data)
        
        # Detect seasonal patterns
        results['seasonal_patterns'] = self._detect_seasonal_patterns(temporal_data)
        
        # Generate trend predictions
        results['trend_predictions'] = self._predict_trends(results)
        
        # Generate insights
        results['insights'] = self._generate_trend_insights(results)
        
        # Suggest visualizations
        results['visualizations'] = self._suggest_trend_visualizations(results)
        
        return results
    
    def _extract_temporal_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract and organize data by time periods"""
        temporal_data = {
            'daily': defaultdict(list),
            'weekly': defaultdict(list),
            'monthly': defaultdict(list),
            'responses_by_time': {},
            'satisfaction_by_time': {},
            'demographics_by_time': {}
        }
        
        for response in data:
            # Extract timestamp
            timestamp_str = response.get('timestamp', '')
            try:
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    # Use current time if no timestamp
                    timestamp = datetime.now()
            except:
                timestamp = datetime.now()
            
            # Group by time periods
            day_key = timestamp.strftime('%Y-%m-%d')
            week_key = timestamp.strftime('%Y-W%W')
            month_key = timestamp.strftime('%Y-%m')
            
            # Store response data by time period
            temporal_data['daily'][day_key].append(response)
            temporal_data['weekly'][week_key].append(response)
            temporal_data['monthly'][month_key].append(response)
            
            # Extract specific data types
            answers = response.get('answers', {})
            
            for q_id, answer_data in answers.items():
                category = answer_data.get('category', 'general')
                answer = answer_data.get('answer', '')
                
                if category in ['satisfaction', 'rating'] and answer:
                    # Satisfaction trends
                    if day_key not in temporal_data['satisfaction_by_time']:
                        temporal_data['satisfaction_by_time'][day_key] = []
                    
                    score = self._convert_to_numeric_score(answer)
                    temporal_data['satisfaction_by_time'][day_key].append(score)
                
                elif category == 'demographic' and answer:
                    # Demographic trends
                    if day_key not in temporal_data['demographics_by_time']:
                        temporal_data['demographics_by_time'][day_key] = {}
                    
                    if q_id not in temporal_data['demographics_by_time'][day_key]:
                        temporal_data['demographics_by_time'][day_key][q_id] = []
                    
                    temporal_data['demographics_by_time'][day_key][q_id].append(answer)
        
        return temporal_data
    
    def _convert_to_numeric_score(self, answer: str) -> float:
        """Convert satisfaction answer to numeric score"""
        satisfaction_scores = {
            'Very Satisfied': 5, 'Satisfied': 4, 'Neutral': 3,
            'Dissatisfied': 2, 'Very Dissatisfied': 1,
            'Excellent': 5, 'Good': 4, 'Average': 3,
            'Poor': 2, 'Very Poor': 1
        }
        
        return satisfaction_scores.get(str(answer), 3)
    
    def _analyze_response_trends(self, temporal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends in response volume and patterns"""
        response_trends = {
            'volume_trends': {},
            'response_rate_patterns': {},
            'peak_periods': {},
            'trend_analysis': {}
        }
        
        # Analyze daily response volumes
        daily_data = temporal_data['daily']
        daily_counts = {day: len(responses) for day, responses in daily_data.items()}
        
        if daily_counts:
            # Calculate trend metrics
            sorted_days = sorted(daily_counts.keys())
            values = [daily_counts[day] for day in sorted_days]
            
            if len(values) > 1:
                trend_direction = self._calculate_trend_direction(values)
                trend_strength = self._calculate_trend_strength(values)
                
                response_trends['volume_trends'] = {
                    'direction': trend_direction,
                    'strength': trend_strength,
                    'daily_average': statistics.mean(values),
                    'peak_day': max(daily_counts, key=daily_counts.get),
                    'lowest_day': min(daily_counts, key=daily_counts.get),
                    'total_responses': sum(values)
                }
        
        # Analyze weekly patterns
        weekly_data = temporal_data['weekly']
        weekly_counts = {week: len(responses) for week, responses in weekly_data.items()}
        
        if weekly_counts:
            response_trends['response_rate_patterns']['weekly'] = {
                'average_per_week': statistics.mean(weekly_counts.values()),
                'best_week': max(weekly_counts, key=weekly_counts.get),
                'total_weeks': len(weekly_counts)
            }
        
        return response_trends
    
    def _analyze_satisfaction_trends(self, temporal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends in satisfaction scores over time"""
        satisfaction_trends = {
            'overall_trend': {},
            'daily_satisfaction': {},
            'satisfaction_volatility': {},
            'improvement_periods': []
        }
        
        satisfaction_by_time = temporal_data['satisfaction_by_time']
        
        if not satisfaction_by_time:
            return satisfaction_trends
        
        # Calculate daily average satisfaction
        daily_avg_satisfaction = {}
        for day, scores in satisfaction_by_time.items():
            if scores:
                daily_avg_satisfaction[day] = statistics.mean(scores)
        
        if daily_avg_satisfaction:
            sorted_days = sorted(daily_avg_satisfaction.keys())
            satisfaction_values = [daily_avg_satisfaction[day] for day in sorted_days]
            
            # Overall trend analysis
            trend_direction = self._calculate_trend_direction(satisfaction_values)
            trend_strength = self._calculate_trend_strength(satisfaction_values)
            
            satisfaction_trends['overall_trend'] = {
                'direction': trend_direction,
                'strength': trend_strength,
                'average_satisfaction': statistics.mean(satisfaction_values),
                'satisfaction_range': max(satisfaction_values) - min(satisfaction_values),
                'best_day': max(daily_avg_satisfaction, key=daily_avg_satisfaction.get),
                'worst_day': min(daily_avg_satisfaction, key=daily_avg_satisfaction.get)
            }
            
            # Identify improvement/decline periods
            improvement_periods = self._identify_trend_periods(sorted_days, satisfaction_values)
            satisfaction_trends['improvement_periods'] = improvement_periods
            
            # Calculate volatility
            if len(satisfaction_values) > 1:
                volatility = statistics.stdev(satisfaction_values)
                satisfaction_trends['satisfaction_volatility'] = {
                    'volatility_score': volatility,
                    'stability_rating': 'High' if volatility < 0.5 else 'Medium' if volatility < 1.0 else 'Low'
                }
        
        return satisfaction_trends
    
    def _analyze_demographic_trends(self, temporal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends in demographic composition over time"""
        demographic_trends = {
            'composition_changes': {},
            'diversity_trends': {},
            'demographic_shifts': []
        }
        
        demographics_by_time = temporal_data['demographics_by_time']
        
        if not demographics_by_time:
            return demographic_trends
        
        # Analyze changes in demographic composition
        for day, demographic_data in demographics_by_time.items():
            for q_id, answers in demographic_data.items():
                if q_id not in demographic_trends['composition_changes']:
                    demographic_trends['composition_changes'][q_id] = {}
                
                # Count demographics for this day
                answer_counts = Counter(answers)
                total = len(answers)
                
                demographic_trends['composition_changes'][q_id][day] = {
                    'distribution': dict(answer_counts),
                    'diversity_score': len(answer_counts) / max(total, 1),
                    'dominant_group': answer_counts.most_common(1)[0] if answer_counts else None
                }
        
        # Detect significant demographic shifts
        for q_id, daily_data in demographic_trends['composition_changes'].items():
            shifts = self._detect_demographic_shifts(daily_data)
            if shifts:
                demographic_trends['demographic_shifts'].extend(shifts)
        
        return demographic_trends
    
    def _detect_seasonal_patterns(self, temporal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect seasonal and cyclical patterns in the data"""
        seasonal_patterns = {
            'weekly_patterns': {},
            'monthly_patterns': {},
            'cyclical_trends': {},
            'seasonal_insights': []
        }
        
        # Analyze weekly patterns (day of week effects)
        daily_data = temporal_data['daily']
        
        day_of_week_responses = defaultdict(list)
        for day_str, responses in daily_data.items():
            try:
                day_date = datetime.strptime(day_str, '%Y-%m-%d')
                day_of_week = day_date.strftime('%A')
                day_of_week_responses[day_of_week].append(len(responses))
            except:
                continue
        
        if day_of_week_responses:
            weekly_averages = {}
            for day, response_counts in day_of_week_responses.items():
                weekly_averages[day] = statistics.mean(response_counts)
            
            seasonal_patterns['weekly_patterns'] = {
                'day_averages': weekly_averages,
                'peak_day': max(weekly_averages, key=weekly_averages.get),
                'low_day': min(weekly_averages, key=weekly_averages.get)
            }
        
        # Analyze monthly patterns
        monthly_data = temporal_data['monthly']
        monthly_responses = {}
        
        for month_str, responses in monthly_data.items():
            monthly_responses[month_str] = len(responses)
        
        if len(monthly_responses) > 2:
            # Look for seasonal trends
            sorted_months = sorted(monthly_responses.keys())
            monthly_values = [monthly_responses[month] for month in sorted_months]
            
            seasonal_patterns['monthly_patterns'] = {
                'monthly_averages': monthly_responses,
                'peak_month': max(monthly_responses, key=monthly_responses.get),
                'low_month': min(monthly_responses, key=monthly_responses.get),
                'seasonal_variation': max(monthly_values) - min(monthly_values)
            }
        
        return seasonal_patterns
    
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate the overall direction of a trend"""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear trend calculation
        n = len(values)
        x_values = list(range(n))
        
        # Calculate slope using simple linear regression
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return 'stable'
        
        slope = numerator / denominator
        
        # Classify trend direction
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_trend_strength(self, values: List[float]) -> float:
        """Calculate the strength of a trend (0-1 scale)"""
        if len(values) < 3:
            return 0
        
        # Calculate coefficient of determination (R²) approximation
        try:
            # Simple measure: how much the values change relative to their variance
            value_range = max(values) - min(values)
            value_std = statistics.stdev(values)
            
            if value_std == 0:
                return 0
            
            strength = min(value_range / (2 * value_std), 1.0)
            return strength
        except:
            return 0
    
    def _identify_trend_periods(self, days: List[str], values: List[float]) -> List[Dict[str, Any]]:
        """Identify periods of improvement or decline"""
        periods = []
        
        if len(values) < 3:
            return periods
        
        # Look for consecutive periods of increase/decrease
        current_trend = None
        period_start = 0
        
        for i in range(1, len(values)):
            if values[i] > values[i-1]:
                trend = 'improvement'
            elif values[i] < values[i-1]:
                trend = 'decline'
            else:
                trend = 'stable'
            
            if current_trend is None:
                current_trend = trend
                period_start = i - 1
            elif current_trend != trend:
                # End current period
                if i - period_start >= 2:  # At least 2 data points
                    periods.append({
                        'type': current_trend,
                        'start_date': days[period_start],
                        'end_date': days[i-1],
                        'duration_days': i - period_start,
                        'value_change': values[i-1] - values[period_start]
                    })
                
                current_trend = trend
                period_start = i - 1
        
        # Add final period if significant
        if current_trend and len(values) - period_start >= 2:
            periods.append({
                'type': current_trend,
                'start_date': days[period_start],
                'end_date': days[-1],
                'duration_days': len(values) - period_start,
                'value_change': values[-1] - values[period_start]
            })
        
        return periods
    
    def _detect_demographic_shifts(self, daily_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect significant shifts in demographic composition"""
        shifts = []
        
        if len(daily_data) < 2:
            return shifts
        
        sorted_days = sorted(daily_data.keys())
        
        # Compare first and last periods
        first_day = daily_data[sorted_days[0]]
        last_day = daily_data[sorted_days[-1]]
        
        first_dist = first_day.get('distribution', {})
        last_dist = last_day.get('distribution', {})
        
        # Look for significant changes in proportions
        all_groups = set(first_dist.keys()) | set(last_dist.keys())
        
        for group in all_groups:
            first_count = first_dist.get(group, 0)
            last_count = last_dist.get(group, 0)
            
            first_total = sum(first_dist.values()) or 1
            last_total = sum(last_dist.values()) or 1
            
            first_prop = first_count / first_total
            last_prop = last_count / last_total
            
            prop_change = last_prop - first_prop
            
            # Significant change threshold: 20% change in proportion
            if abs(prop_change) > 0.2:
                shifts.append({
                    'group': group,
                    'change_type': 'increase' if prop_change > 0 else 'decrease',
                    'magnitude': abs(prop_change),
                    'from_proportion': first_prop,
                    'to_proportion': last_prop,
                    'period': f"{sorted_days[0]} to {sorted_days[-1]}"
                })
        
        return shifts
    
    def _predict_trends(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trend predictions based on historical patterns"""
        predictions = {
            'satisfaction_forecast': {},
            'response_volume_forecast': {},
            'demographic_projections': {},
            'confidence_levels': {}
        }
        
        # Satisfaction trend predictions
        satisfaction_trends = results.get('satisfaction_trends', {})
        overall_trend = satisfaction_trends.get('overall_trend', {})
        
        if overall_trend:
            direction = overall_trend.get('direction', 'stable')
            strength = overall_trend.get('strength', 0)
            current_avg = overall_trend.get('average_satisfaction', 3)
            
            # Simple trend extrapolation
            if direction == 'increasing':
                predicted_change = strength * 0.5  # Conservative prediction
                forecast = min(5.0, current_avg + predicted_change)
            elif direction == 'decreasing':
                predicted_change = strength * 0.5
                forecast = max(1.0, current_avg - predicted_change)
            else:
                forecast = current_avg
            
            predictions['satisfaction_forecast'] = {
                'next_period_prediction': forecast,
                'trend_direction': direction,
                'confidence': min(0.9, strength + 0.3)
            }
        
        # Response volume predictions
        response_trends = results.get('response_trends', {})
        volume_trends = response_trends.get('volume_trends', {})
        
        if volume_trends:
            direction = volume_trends.get('direction', 'stable')
            current_avg = volume_trends.get('daily_average', 0)
            
            if direction == 'increasing':
                forecast = current_avg * 1.1
            elif direction == 'decreasing':
                forecast = current_avg * 0.9
            else:
                forecast = current_avg
            
            predictions['response_volume_forecast'] = {
                'daily_volume_prediction': forecast,
                'trend_direction': direction
            }
        
        return predictions
    
    def _generate_trend_insights(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from trend analysis"""
        insights = []
        
        # Satisfaction trend insights
        satisfaction_trends = results.get('satisfaction_trends', {})
        overall_trend = satisfaction_trends.get('overall_trend', {})
        
        if overall_trend:
            direction = overall_trend.get('direction', 'stable')
            avg_satisfaction = overall_trend.get('average_satisfaction', 0)
            
            insights.append(f"Satisfaction trend: {direction} (average: {avg_satisfaction:.1f}/5.0)")
            
            if direction == 'increasing':
                insights.append("Positive momentum in satisfaction - continue current strategies")
            elif direction == 'decreasing':
                insights.append("Declining satisfaction trend - immediate intervention needed")
            
            volatility = satisfaction_trends.get('satisfaction_volatility', {})
            if volatility:
                stability = volatility.get('stability_rating', 'Unknown')
                insights.append(f"Satisfaction stability: {stability}")
        
        # Response pattern insights
        response_trends = results.get('response_trends', {})
        volume_trends = response_trends.get('volume_trends', {})
        
        if volume_trends:
            total_responses = volume_trends.get('total_responses', 0)
            peak_day = volume_trends.get('peak_day', 'Unknown')
            insights.append(f"Total responses analyzed: {total_responses}")
            insights.append(f"Peak response day: {peak_day}")
        
        # Seasonal pattern insights
        seasonal_patterns = results.get('seasonal_patterns', {})
        weekly_patterns = seasonal_patterns.get('weekly_patterns', {})
        
        if weekly_patterns:
            peak_day = weekly_patterns.get('peak_day', 'Unknown')
            low_day = weekly_patterns.get('low_day', 'Unknown')
            insights.append(f"Best response day: {peak_day}, Lowest: {low_day}")
        
        # Demographic shift insights
        demographic_trends = results.get('demographic_trends', {})
        demographic_shifts = demographic_trends.get('demographic_shifts', [])
        
        if demographic_shifts:
            insights.append(f"Detected {len(demographic_shifts)} significant demographic shifts")
            for shift in demographic_shifts[:2]:  # Top 2 shifts
                group = shift.get('group', 'Unknown')
                change_type = shift.get('change_type', 'change')
                insights.append(f"Notable {change_type} in {group} demographic")
        
        # Trend predictions insights
        trend_predictions = results.get('trend_predictions', {})
        satisfaction_forecast = trend_predictions.get('satisfaction_forecast', {})
        
        if satisfaction_forecast:
            forecast = satisfaction_forecast.get('next_period_prediction', 0)
            confidence = satisfaction_forecast.get('confidence', 0)
            insights.append(f"Next period satisfaction forecast: {forecast:.1f}/5.0 (confidence: {confidence:.1%})")
        
        return insights
    
    def _suggest_trend_visualizations(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Suggest appropriate visualizations for trend data"""
        visualizations = []
        
        # Satisfaction trend line chart
        satisfaction_trends = results.get('satisfaction_trends', {})
        if satisfaction_trends:
            visualizations.append({
                'type': 'line_chart',
                'title': 'Satisfaction Trends Over Time',
                'description': 'Line chart showing satisfaction score changes over time',
                'data_source': 'satisfaction_trends'
            })
        
        # Response volume trend
        response_trends = results.get('response_trends', {})
        if response_trends:
            visualizations.append({
                'type': 'area_chart',
                'title': 'Response Volume Trends',
                'description': 'Area chart showing response volume patterns over time',
                'data_source': 'response_trends'
            })
        
        # Seasonal patterns
        seasonal_patterns = results.get('seasonal_patterns', {})
        if seasonal_patterns.get('weekly_patterns'):
            visualizations.append({
                'type': 'radar_chart',
                'title': 'Weekly Response Patterns',
                'description': 'Radar chart showing response patterns by day of week',
                'data_source': 'weekly_patterns'
            })
        
        # Demographic trends
        demographic_trends = results.get('demographic_trends', {})
        if demographic_trends.get('demographic_shifts'):
            visualizations.append({
                'type': 'stacked_bar',
                'title': 'Demographic Composition Changes',
                'description': 'Stacked bar chart showing demographic changes over time',
                'data_source': 'demographic_trends'
            })
        
        # Trend predictions
        trend_predictions = results.get('trend_predictions', {})
        if trend_predictions:
            visualizations.append({
                'type': 'forecast_chart',
                'title': 'Trend Predictions',
                'description': 'Chart showing historical data with trend predictions',
                'data_source': 'trend_predictions'
            })
        
        return visualizations