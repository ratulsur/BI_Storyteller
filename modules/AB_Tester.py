"""
A/B Testing Module
Performs A/B test analysis and statistical significance testing
"""

import json
import random
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict, Counter
import statistics


class ABTester:
    """Perform A/B testing analysis on survey data"""
    
    def __init__(self):
        self.test_variants = ['A', 'B']
        self.significance_threshold = 0.05  # 95% confidence level
        self.min_sample_size = 30  # Minimum sample size per variant
    
    def run_ab_test(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive A/B testing analysis"""
        print("🧪 Setting up and analyzing A/B tests...")
        
        results = {
            'test_setup': {},
            'variant_performance': {},
            'statistical_analysis': {},
            'significance_tests': {},
            'recommendations': [],
            'insights': [],
            'test_results': []
        }
        
        # Identify potential test variables and metrics
        test_scenarios = self._identify_test_scenarios(data)
        
        if not test_scenarios:
            return {
                'error': 'Insufficient data for A/B testing',
                'recommendations': ['Collect more diverse data for meaningful A/B tests']
            }
        
        # Run A/B tests for each scenario
        for scenario in test_scenarios:
            test_result = self._conduct_ab_test(data, scenario)
            if test_result:
                results['test_results'].append(test_result)
        
        # Analyze overall results
        results['variant_performance'] = self._analyze_variant_performance(results['test_results'])
        results['statistical_analysis'] = self._perform_statistical_analysis(results['test_results'])
        results['significance_tests'] = self._calculate_significance(results['test_results'])
        
        # Generate insights and recommendations
        results['insights'] = self._generate_ab_insights(results)
        results['recommendations'] = self._generate_ab_recommendations(results)
        
        return results
    
    def _identify_test_scenarios(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify potential A/B testing scenarios from the data"""
        scenarios = []
        
        # Analyze data structure to identify segmentation possibilities
        demographic_vars = []
        outcome_vars = []
        
        sample_response = data[0] if data else {}
        answers = sample_response.get('answers', {})
        
        for q_id, answer_data in answers.items():
            category = answer_data.get('category', 'general')
            question_type = answer_data.get('question_type', 'unknown')
            
            if category == 'demographic' and question_type == 'MCQ':
                demographic_vars.append({
                    'question_id': q_id,
                    'question': answer_data.get('question', ''),
                    'category': category,
                    'type': 'segmentation'
                })
            
            elif category in ['satisfaction', 'rating'] and question_type == 'MCQ':
                outcome_vars.append({
                    'question_id': q_id,
                    'question': answer_data.get('question', ''),
                    'category': category,
                    'type': 'outcome'
                })
        
        # Create test scenarios by pairing segmentation variables with outcome variables
        for demo_var in demographic_vars:
            for outcome_var in outcome_vars:
                # Check if this combination has enough data
                if self._validate_test_scenario(data, demo_var['question_id'], outcome_var['question_id']):
                    scenarios.append({
                        'test_name': f"{demo_var['question'].split('?')[0]} vs {outcome_var['question'].split('?')[0]}",
                        'segmentation_var': demo_var,
                        'outcome_var': outcome_var,
                        'test_type': 'demographic_outcome'
                    })
        
        # Create artificial random split tests if not enough natural segments
        if len(scenarios) < 2 and len(outcome_vars) > 0:
            for outcome_var in outcome_vars[:2]:  # Limit to 2 to avoid overwhelming
                scenarios.append({
                    'test_name': f"Random Split Test - {outcome_var['question'].split('?')[0]}",
                    'segmentation_var': {'type': 'random_split'},
                    'outcome_var': outcome_var,
                    'test_type': 'random_split'
                })
        
        return scenarios[:5]  # Limit to 5 tests maximum
    
    def _validate_test_scenario(self, data: List[Dict[str, Any]], 
                              segment_var: str, outcome_var: str) -> bool:
        """Validate if a test scenario has sufficient data"""
        segment_groups = defaultdict(int)
        
        for response in data:
            answers = response.get('answers', {})
            
            segment_answer = answers.get(segment_var, {}).get('answer')
            outcome_answer = answers.get(outcome_var, {}).get('answer')
            
            if segment_answer and outcome_answer:
                segment_groups[segment_answer] += 1
        
        # Check if we have at least 2 groups with minimum sample size
        valid_groups = sum(1 for count in segment_groups.values() 
                          if count >= self.min_sample_size)
        
        return valid_groups >= 2
    
    def _conduct_ab_test(self, data: List[Dict[str, Any]], 
                        scenario: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Conduct an individual A/B test"""
        test_name = scenario['test_name']
        test_type = scenario['test_type']
        segmentation_var = scenario['segmentation_var']
        outcome_var = scenario['outcome_var']
        
        # Prepare test data
        if test_type == 'random_split':
            test_data = self._create_random_split_test(data, outcome_var)
        else:
            test_data = self._create_segment_test(data, segmentation_var, outcome_var)
        
        if not test_data or len(test_data['groups']) < 2:
            return None
        
        # Calculate metrics for each group
        group_metrics = {}
        for group_name, group_data in test_data['groups'].items():
            metrics = self._calculate_group_metrics(group_data)
            group_metrics[group_name] = metrics
        
        # Perform statistical comparison
        statistical_results = self._perform_group_comparison(group_metrics)
        
        return {
            'test_name': test_name,
            'test_type': test_type,
            'groups': group_metrics,
            'statistical_results': statistical_results,
            'sample_sizes': {group: len(data) for group, data in test_data['groups'].items()},
            'test_duration': 'Historical Analysis',
            'confidence_level': 95
        }
    
    def _create_random_split_test(self, data: List[Dict[str, Any]], 
                                outcome_var: Dict[str, Any]) -> Dict[str, Any]:
        """Create random A/B split test"""
        outcome_q_id = outcome_var['question_id']
        
        # Filter responses that have the outcome variable
        valid_responses = []
        for response in data:
            answers = response.get('answers', {})
            if outcome_q_id in answers and answers[outcome_q_id].get('answer'):
                valid_responses.append(response)
        
        if len(valid_responses) < self.min_sample_size * 2:
            return None
        
        # Randomly assign to A/B groups
        random.shuffle(valid_responses)
        mid_point = len(valid_responses) // 2
        
        group_a = valid_responses[:mid_point]
        group_b = valid_responses[mid_point:mid_point*2]
        
        return {
            'groups': {
                'Group A (Random)': group_a,
                'Group B (Random)': group_b
            },
            'outcome_variable': outcome_var
        }
    
    def _create_segment_test(self, data: List[Dict[str, Any]], 
                           segmentation_var: Dict[str, Any], 
                           outcome_var: Dict[str, Any]) -> Dict[str, Any]:
        """Create segmented A/B test based on demographic variable"""
        segment_q_id = segmentation_var['question_id']
        outcome_q_id = outcome_var['question_id']
        
        # Group responses by segmentation variable
        groups = defaultdict(list)
        
        for response in data:
            answers = response.get('answers', {})
            
            segment_answer = answers.get(segment_q_id, {}).get('answer')
            outcome_answer = answers.get(outcome_q_id, {}).get('answer')
            
            if segment_answer and outcome_answer:
                groups[segment_answer].append(response)
        
        # Select top 2 groups with sufficient sample size
        valid_groups = {name: group_data for name, group_data in groups.items() 
                       if len(group_data) >= self.min_sample_size}
        
        if len(valid_groups) < 2:
            return None
        
        # Take the two largest groups
        sorted_groups = sorted(valid_groups.items(), key=lambda x: len(x[1]), reverse=True)
        selected_groups = dict(sorted_groups[:2])
        
        return {
            'groups': selected_groups,
            'segmentation_variable': segmentation_var,
            'outcome_variable': outcome_var
        }
    
    def _calculate_group_metrics(self, group_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics for a test group"""
        metrics = {
            'sample_size': len(group_data),
            'satisfaction_scores': [],
            'response_quality': {},
            'demographic_profile': {}
        }
        
        satisfaction_scores = []
        response_lengths = []
        demographics = defaultdict(list)
        
        for response in group_data:
            answers = response.get('answers', {})
            
            for q_id, answer_data in answers.items():
                category = answer_data.get('category', 'general')
                answer = answer_data.get('answer', '')
                
                if category in ['satisfaction', 'rating'] and answer:
                    # Convert to numeric score
                    score = self._convert_satisfaction_to_score(answer)
                    satisfaction_scores.append(score)
                
                elif category == 'demographic' and answer:
                    question = answer_data.get('question', '').lower()
                    if 'age' in question:
                        demographics['age'].append(answer)
                    elif 'gender' in question:
                        demographics['gender'].append(answer)
                    elif 'income' in question:
                        demographics['income'].append(answer)
                
                elif answer_data.get('question_type') == 'Descriptive' and answer:
                    response_lengths.append(len(answer))
        
        # Calculate satisfaction metrics
        if satisfaction_scores:
            metrics['satisfaction_metrics'] = {
                'mean_satisfaction': statistics.mean(satisfaction_scores),
                'median_satisfaction': statistics.median(satisfaction_scores),
                'satisfaction_std': statistics.stdev(satisfaction_scores) if len(satisfaction_scores) > 1 else 0,
                'high_satisfaction_rate': sum(1 for score in satisfaction_scores if score >= 4) / len(satisfaction_scores)
            }
        
        # Calculate response quality metrics
        if response_lengths:
            metrics['response_quality'] = {
                'avg_response_length': statistics.mean(response_lengths),
                'engagement_score': min(statistics.mean(response_lengths) / 50, 1.0)  # Normalized engagement
            }
        
        # Demographic profile
        for demo_type, demo_values in demographics.items():
            if demo_values:
                demo_counts = Counter(demo_values)
                metrics['demographic_profile'][demo_type] = {
                    'distribution': dict(demo_counts),
                    'dominant_category': demo_counts.most_common(1)[0] if demo_counts else None
                }
        
        return metrics
    
    def _convert_satisfaction_to_score(self, answer: str) -> float:
        """Convert satisfaction answer to numeric score"""
        satisfaction_mapping = {
            'Very Satisfied': 5, 'Satisfied': 4, 'Neutral': 3,
            'Dissatisfied': 2, 'Very Dissatisfied': 1,
            'Excellent': 5, 'Good': 4, 'Average': 3,
            'Poor': 2, 'Very Poor': 1
        }
        
        return satisfaction_mapping.get(str(answer), 3)
    
    def _perform_group_comparison(self, group_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statistical comparison between groups"""
        groups = list(group_metrics.keys())
        
        if len(groups) != 2:
            return {'error': 'Need exactly 2 groups for comparison'}
        
        group_a, group_b = groups
        metrics_a = group_metrics[group_a]
        metrics_b = group_metrics[group_b]
        
        comparison_results = {
            'groups_compared': [group_a, group_b],
            'sample_sizes': {
                group_a: metrics_a['sample_size'],
                group_b: metrics_b['sample_size']
            }
        }
        
        # Compare satisfaction metrics if available
        sat_a = metrics_a.get('satisfaction_metrics', {})
        sat_b = metrics_b.get('satisfaction_metrics', {})
        
        if sat_a and sat_b:
            mean_a = sat_a.get('mean_satisfaction', 0)
            mean_b = sat_b.get('mean_satisfaction', 0)
            
            # Calculate effect size (Cohen's d approximation)
            pooled_std = ((sat_a.get('satisfaction_std', 0) + sat_b.get('satisfaction_std', 0)) / 2)
            effect_size = abs(mean_a - mean_b) / max(pooled_std, 0.1)
            
            # Simple statistical significance test (t-test approximation)
            statistical_significance = self._calculate_significance_simple(
                mean_a, mean_b, 
                metrics_a['sample_size'], metrics_b['sample_size'],
                sat_a.get('satisfaction_std', 0), sat_b.get('satisfaction_std', 0)
            )
            
            comparison_results['satisfaction_comparison'] = {
                'group_a_mean': mean_a,
                'group_b_mean': mean_b,
                'difference': mean_a - mean_b,
                'effect_size': effect_size,
                'winner': group_a if mean_a > mean_b else group_b,
                'confidence_interval': self._calculate_confidence_interval(mean_a, mean_b),
                'statistical_significance': statistical_significance
            }
        
        # Compare engagement metrics
        qual_a = metrics_a.get('response_quality', {})
        qual_b = metrics_b.get('response_quality', {})
        
        if qual_a and qual_b:
            eng_a = qual_a.get('engagement_score', 0)
            eng_b = qual_b.get('engagement_score', 0)
            
            comparison_results['engagement_comparison'] = {
                'group_a_engagement': eng_a,
                'group_b_engagement': eng_b,
                'engagement_winner': group_a if eng_a > eng_b else group_b,
                'engagement_difference': abs(eng_a - eng_b)
            }
        
        return comparison_results
    
    def _calculate_significance_simple(self, mean_a: float, mean_b: float,
                                     n_a: int, n_b: int,
                                     std_a: float, std_b: float) -> Dict[str, Any]:
        """Simple statistical significance calculation"""
        
        # Pooled standard error
        pooled_variance = ((n_a - 1) * std_a**2 + (n_b - 1) * std_b**2) / (n_a + n_b - 2)
        standard_error = (pooled_variance * (1/n_a + 1/n_b))**0.5
        
        if standard_error == 0:
            return {'is_significant': False, 'p_value_estimate': 1.0}
        
        # t-statistic
        t_stat = abs(mean_a - mean_b) / standard_error
        
        # Rough p-value estimation (simplified)
        # This is a very rough approximation - in practice, use proper statistical libraries
        degrees_of_freedom = n_a + n_b - 2
        
        # Critical t-value for 95% confidence (approximately 2.0 for large samples)
        critical_t = 2.0 if degrees_of_freedom > 30 else 2.5
        
        is_significant = t_stat > critical_t
        p_value_estimate = max(0.01, 1 / (1 + t_stat))  # Very rough estimate
        
        return {
            'is_significant': is_significant,
            'p_value_estimate': p_value_estimate,
            't_statistic': t_stat,
            'degrees_of_freedom': degrees_of_freedom,
            'confidence_level': 95
        }
    
    def _calculate_confidence_interval(self, mean_a: float, mean_b: float) -> Dict[str, float]:
        """Calculate rough confidence interval for the difference"""
        difference = mean_a - mean_b
        
        # Rough margin of error (simplified)
        margin_of_error = abs(difference) * 0.2  # Very rough approximation
        
        return {
            'lower_bound': difference - margin_of_error,
            'upper_bound': difference + margin_of_error,
            'point_estimate': difference
        }
    
    def _analyze_variant_performance(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall variant performance across all tests"""
        performance_analysis = {
            'test_count': len(test_results),
            'significant_results': 0,
            'winning_variants': defaultdict(int),
            'effect_sizes': [],
            'sample_size_analysis': {}
        }
        
        total_sample_size = 0
        
        for test in test_results:
            statistical_results = test.get('statistical_results', {})
            sample_sizes = test.get('sample_sizes', {})
            
            total_sample_size += sum(sample_sizes.values())
            
            # Check for significant results
            satisfaction_comparison = statistical_results.get('satisfaction_comparison', {})
            if satisfaction_comparison.get('statistical_significance', {}).get('is_significant', False):
                performance_analysis['significant_results'] += 1
                winner = satisfaction_comparison.get('winner', 'Unknown')
                performance_analysis['winning_variants'][winner] += 1
                
                effect_size = satisfaction_comparison.get('effect_size', 0)
                performance_analysis['effect_sizes'].append(effect_size)
        
        performance_analysis['sample_size_analysis'] = {
            'total_sample_size': total_sample_size,
            'average_per_test': total_sample_size / max(len(test_results), 1),
            'adequate_power': sum(sum(test.get('sample_sizes', {}).values()) for test in test_results) / len(test_results) > self.min_sample_size * 2 if test_results else False
        }
        
        if performance_analysis['effect_sizes']:
            performance_analysis['average_effect_size'] = statistics.mean(performance_analysis['effect_sizes'])
        
        return performance_analysis
    
    def _perform_statistical_analysis(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis"""
        analysis = {
            'power_analysis': {},
            'multiple_comparison_correction': {},
            'meta_analysis': {}
        }
        
        if not test_results:
            return analysis
        
        # Power analysis
        significant_tests = sum(1 for test in test_results 
                              if test.get('statistical_results', {})
                              .get('satisfaction_comparison', {})
                              .get('statistical_significance', {})
                              .get('is_significant', False))
        
        analysis['power_analysis'] = {
            'tests_conducted': len(test_results),
            'significant_results': significant_tests,
            'power_estimate': significant_tests / max(len(test_results), 1),
            'recommended_sample_size': self.min_sample_size * 2,
            'actual_average_sample_size': sum(sum(test.get('sample_sizes', {}).values()) 
                                            for test in test_results) / max(len(test_results), 1)
        }
        
        # Multiple comparison correction (Bonferroni)
        if len(test_results) > 1:
            corrected_alpha = self.significance_threshold / len(test_results)
            analysis['multiple_comparison_correction'] = {
                'original_alpha': self.significance_threshold,
                'corrected_alpha': corrected_alpha,
                'correction_method': 'Bonferroni',
                'tests_significant_after_correction': sum(1 for test in test_results 
                                                        if test.get('statistical_results', {})
                                                        .get('satisfaction_comparison', {})
                                                        .get('statistical_significance', {})
                                                        .get('p_value_estimate', 1.0) < corrected_alpha)
            }
        
        return analysis
    
    def _calculate_significance(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall significance metrics"""
        significance_summary = {
            'overall_significance': False,
            'significant_tests': [],
            'non_significant_tests': [],
            'borderline_tests': []
        }
        
        for test in test_results:
            test_name = test.get('test_name', 'Unknown Test')
            statistical_results = test.get('statistical_results', {})
            satisfaction_comparison = statistical_results.get('satisfaction_comparison', {})
            significance = satisfaction_comparison.get('statistical_significance', {})
            
            is_significant = significance.get('is_significant', False)
            p_value = significance.get('p_value_estimate', 1.0)
            
            test_summary = {
                'test_name': test_name,
                'is_significant': is_significant,
                'p_value': p_value,
                'effect_size': satisfaction_comparison.get('effect_size', 0)
            }
            
            if is_significant:
                significance_summary['significant_tests'].append(test_summary)
            elif p_value < 0.1:  # Borderline significance
                significance_summary['borderline_tests'].append(test_summary)
            else:
                significance_summary['non_significant_tests'].append(test_summary)
        
        significance_summary['overall_significance'] = len(significance_summary['significant_tests']) > 0
        
        return significance_summary
    
    def _generate_ab_insights(self, results: Dict[str, Any]) -> List[str]:
        """Generate insights from A/B testing results"""
        insights = []
        
        test_results = results.get('test_results', [])
        variant_performance = results.get('variant_performance', {})
        statistical_analysis = results.get('statistical_analysis', {})
        
        # Overall testing insights
        total_tests = len(test_results)
        significant_results = variant_performance.get('significant_results', 0)
        
        insights.append(f"Conducted {total_tests} A/B tests with {significant_results} statistically significant results")
        
        if significant_results > 0:
            insights.append(f"Found meaningful differences in {significant_results}/{total_tests} tests")
            
            # Winner analysis
            winning_variants = variant_performance.get('winning_variants', {})
            if winning_variants:
                top_winner = max(winning_variants, key=winning_variants.get)
                win_count = winning_variants[top_winner]
                insights.append(f"'{top_winner}' performed best in {win_count} test(s)")
        else:
            insights.append("No statistically significant differences found - may need larger sample sizes")
        
        # Effect size insights
        avg_effect_size = variant_performance.get('average_effect_size', 0)
        if avg_effect_size > 0:
            if avg_effect_size > 0.8:
                insights.append("Large effect sizes detected - differences are practically significant")
            elif avg_effect_size > 0.5:
                insights.append("Medium effect sizes found - moderate practical significance")
            else:
                insights.append("Small effect sizes - differences may not be practically significant")
        
        # Sample size insights
        sample_analysis = variant_performance.get('sample_size_analysis', {})
        adequate_power = sample_analysis.get('adequate_power', False)
        
        if not adequate_power:
            insights.append("Sample sizes may be insufficient for reliable results")
            recommended_size = statistical_analysis.get('power_analysis', {}).get('recommended_sample_size', 60)
            insights.append(f"Recommend minimum {recommended_size} responses per variant for future tests")
        
        # Multiple testing insights
        multiple_comparison = statistical_analysis.get('multiple_comparison_correction', {})
        if multiple_comparison:
            corrected_significant = multiple_comparison.get('tests_significant_after_correction', 0)
            if corrected_significant < significant_results:
                insights.append(f"After multiple comparison correction: {corrected_significant} tests remain significant")
        
        return insights
    
    def _generate_ab_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations from A/B testing"""
        recommendations = []
        
        test_results = results.get('test_results', [])
        variant_performance = results.get('variant_performance', {})
        significance_results = results.get('significance_tests', {})
        
        # Test design recommendations
        sample_analysis = variant_performance.get('sample_size_analysis', {})
        avg_sample_size = sample_analysis.get('average_per_test', 0)
        
        if avg_sample_size < self.min_sample_size * 2:
            recommendations.append(f"Increase sample size to at least {self.min_sample_size * 2} per variant for reliable results")
        
        # Significant results recommendations
        significant_tests = significance_results.get('significant_tests', [])
        
        for test in significant_tests:
            test_name = test['test_name']
            effect_size = test['effect_size']
            
            if effect_size > 0.5:
                recommendations.append(f"Implement winning variant from '{test_name}' - shows strong practical significance")
        
        # Non-significant results recommendations
        non_significant_tests = significance_results.get('non_significant_tests', [])
        
        if len(non_significant_tests) > len(significant_tests):
            recommendations.append("Focus resources on areas with proven differences rather than non-significant variations")
        
        # Borderline results recommendations
        borderline_tests = significance_results.get('borderline_tests', [])
        
        for test in borderline_tests:
            recommendations.append(f"Consider retesting '{test['test_name']}' with larger sample size - shows promising trends")
        
        # Testing strategy recommendations
        total_tests = len(test_results)
        
        if total_tests < 3:
            recommendations.append("Expand A/B testing to more variables for comprehensive optimization")
        
        # Winner analysis recommendations
        winning_variants = variant_performance.get('winning_variants', {})
        if winning_variants:
            consistent_winner = max(winning_variants, key=winning_variants.get)
            if winning_variants[consistent_winner] > 1:
                recommendations.append(f"'{consistent_winner}' shows consistent performance - consider as primary strategy")
        
        # Statistical recommendations
        multiple_comparison = results.get('statistical_analysis', {}).get('multiple_comparison_correction', {})
        if multiple_comparison and total_tests > 3:
            recommendations.append("Apply multiple comparison corrections when running many simultaneous tests")
        
        # Data collection recommendations
        if not test_results:
            recommendations.append("Collect more structured data with clear segmentation variables for future A/B testing")
        
        return recommendations