#!/usr/bin/env python3
"""
BI Storyteller - End-to-End Marketing Analysis Automation
Main application entry point
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import all modules
from modules.Variables import VariableExtractor
from modules.Questionnaire import QuestionnaireGenerator
from modules.data_generator import DataGenerator
from modules.Data_Preprocessing import DataCleaner
from modules.eda_analyzer import EDAAnalyzer
from modules.visualization_creator import VisualizationCreator
from modules.predictive_analysis import PredictiveAnalyzer
from modules.trend_analysis import TrendAnalyzer
from modules.sentiment_analysis import SentimentAnalyzer
from modules.AB_Tester import ABTester
from modules.Chat import DataChat
from utils.presentation_generator import PPTGenerator



class BIStorytellerApp:
    """Main application class for BI Storyteller"""
    
    def __init__(self):
        self.logger = Logger()
        self.state_manager = StateManager()
        self.current_step = 1
        self.max_steps = 12
        
        # Initialize all modules
        self.variable_extractor = VariableExtractor()
        self.questionnaire_generator = QuestionnaireGenerator()
        self.data_generator = DataGenerator()
        self.data_cleaner = DataCleaner()
        self.eda_analyzer = EDAAnalyzer()
        self.visualization_creator = VisualizationCreator()
        self.predictive_analyzer = PredictiveAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.ab_tester = ABTester()
        self.data_chat = DataChat()
        self.ppt_generator = PPTGenerator()
        
        self.logger.log("BI Storyteller initialized successfully")
    
    def display_welcome(self):
        """Display welcome message and application overview"""
        print("\n" + "="*60)
        print(" Welcome to BI Storyteller")
        print("   End-to-End Marketing Analysis Automation")
        print("="*60)
        print("\nThis application will guide you through:")
        print("1.  Variable Extraction from Business Problems")
        print("2.  Questionnaire Generation & Approval")
        print("3.  Sample Data Generation")
        print("4.  Data Cleaning & Balancing")
        print("5.  Exploratory Data Analysis (EDA)")
        print("6.  Visualization Creation")
        print("7.  Predictive Analytics")
        print("8.  Trend Analysis")
        print("9.  Sentiment Analysis")
        print("10. A/B Testing")
        print("11. Data Chat Interface")
        print("12. Automated PPT Generation")
        print("\n" + "="*60)
    
    def display_menu(self):
        """Display main navigation menu"""
        print(f"\n📍 Current Step: {self.current_step}/{self.max_steps}")
        print("\nSelect an option:")
        print("1. Start/Continue Current Step")
        print("2. Jump to Specific Step")
        print("3. View Current State")
        print("4. Export Current Data to PPT Dashboard")
        print("5. Exit Application")
        print("-" * 40)
    
    def get_user_choice(self, prompt: str = "Enter your choice: ") -> str:
        """Get user input with error handling"""
        try:
            return input(prompt).strip()
        except KeyboardInterrupt:
            print("\n\nApplication terminated by user.")
            sys.exit(0)
        except Exception as e:
            self.logger.log(f"Error getting user input: {e}", "ERROR")
            return ""
    
    def execute_current_step(self):
        """Execute the current step in the workflow"""
        step_methods = {
            1: self.step_1_variable_extraction,
            2: self.step_2_questionnaire_generation,
            3: self.step_3_data_generation,
            4: self.step_4_data_cleaning,
            5: self.step_5_eda_analysis,
            6: self.step_6_visualization,
            7: self.step_7_predictive_analytics,
            8: self.step_8_trend_analysis,
            9: self.step_9_sentiment_analysis,
            10: self.step_10_ab_testing,
            11: self.step_11_data_chat,
            12: self.step_12_ppt_generation
        }
        
        if self.current_step in step_methods:
            step_methods[self.current_step]()
        else:
            print(f"Invalid step: {self.current_step}")
    
    def step_1_variable_extraction(self):
        """Step 1: Extract variables from business problem"""
        print("\n🔍 Step 1: Variable Extraction")
        print("-" * 30)
        
        business_problem = self.get_user_choice("Enter your business problem: ")
        if not business_problem:
            return
        
        variables = self.variable_extractor.extract_variables(business_problem)
        
        print("\n📋 Extracted Variables:")
        for i, var in enumerate(variables, 1):
            print(f"{i}. {var}")
        
        approval = self.get_user_choice("\nApprove variables to proceed to questionnaire? (y/n): ")
        if approval.lower() == 'y':
            self.state_manager.save_data('variables', variables)
            self.state_manager.save_data('business_problem', business_problem)
            print(" Variables approved! Moving to questionnaire generation.")
            self.current_step = 2
        else:
            print(" Variables not approved. Please modify or try again.")
    
    def step_2_questionnaire_generation(self):
        """Step 2: Generate and approve questionnaire"""
        print("\n📝 Step 2: Questionnaire Generation")
        print("-" * 35)
        
        variables = self.state_manager.load_data('variables')
        if not variables:
            print(" No variables found. Please complete Step 1 first.")
            return
        
        questionnaire = self.questionnaire_generator.generate_questionnaire(variables)
        
        print("\n📋 Generated Questionnaire:")
        for i, question in enumerate(questionnaire, 1):
            print(f"\nQ{i}. {question['question']}")
            if question['type'] == 'MCQ':
                for j, option in enumerate(question['options'], 1):
                    print(f"   {j}. {option}")
        
        modify = self.get_user_choice("\nDo you want to modify the questionnaire? (y/n): ")
        if modify.lower() == 'y':
            # Allow modifications
            questionnaire = self.questionnaire_generator.modify_questionnaire(questionnaire)
        
        approval = self.get_user_choice("\nApprove questionnaire? (y/n): ")
        if approval.lower() == 'y':
            self.state_manager.save_data('questionnaire', questionnaire)
            print("✅ Questionnaire approved! Moving to data generation.")
            self.current_step = 3
        else:
            print("❌ Questionnaire not approved. Please modify or try again.")
    
    def step_3_data_generation(self):
        """Step 3: Generate sample data"""
        print("\n🎲 Step 3: Sample Data Generation")
        print("-" * 32)
        
        questionnaire = self.state_manager.load_data('questionnaire')
        if not questionnaire:
            print("❌ No questionnaire found. Please complete Step 2 first.")
            return
        
        num_responses = int(self.get_user_choice("Enter number of sample responses (default 1000): ") or "1000")
        
        sample_data = self.data_generator.generate_sample_data(questionnaire, num_responses)
        
        print(f"\n✅ Generated {len(sample_data)} sample responses")
        print("Sample data preview:")
        print(str(sample_data[:3])[:200] + "..." if len(str(sample_data[:3])) > 200 else str(sample_data[:3]))
        
        approval = self.get_user_choice("\nProceed to data cleaning? (y/n): ")
        if approval.lower() == 'y':
            self.state_manager.save_data('raw_data', sample_data)
            print("✅ Data saved! Moving to data cleaning.")
            self.current_step = 4
    
    def step_4_data_cleaning(self):
        """Step 4: Clean and balance data"""
        print("\n🧹 Step 4: Data Cleaning & Balancing")
        print("-" * 34)
        
        raw_data = self.state_manager.load_data('raw_data')
        if not raw_data:
            print(" No raw data found. Please complete Step 3 first.")
            return
        
        print(" Cleaning and balancing data...")
        cleaned_data = self.data_cleaner.clean_and_balance(raw_data)
        
        print(f" Data cleaned successfully!")
        print(f"Original records: {len(raw_data)}")
        print(f"Cleaned records: {len(cleaned_data)}")
        
        approval = self.get_user_choice("\nProceed to EDA? (y/n): ")
        if approval.lower() == 'y':
            self.state_manager.save_data('cleaned_data', cleaned_data)
            print(" Cleaned data saved! Moving to EDA.")
            self.current_step = 5
    
    def step_5_eda_analysis(self):
        """Step 5: Exploratory Data Analysis"""
        print("\n Step 5: Exploratory Data Analysis")
        print("-" * 36)
        
        cleaned_data = self.state_manager.load_data('cleaned_data')
        if not cleaned_data:
            print(" No cleaned data found. Please complete Step 4 first.")
            return
        
        print(" Performing EDA analysis...")
        eda_results = self.eda_analyzer.perform_eda(cleaned_data)
        
        print(" EDA completed!")
        print("Key insights:")
        for insight in eda_results.get('insights', []):
            print(f"  • {insight}")
        
        export_choice = self.get_user_choice("\nExport EDA to PPT Dashboard? (y/n): ")
        if export_choice.lower() == 'y':
            self.state_manager.add_to_ppt_exports('eda', eda_results)
            print(" EDA results exported to PPT Dashboard")
        
        approval = self.get_user_choice("\nProceed to visualization? (y/n): ")
        if approval.lower() == 'y':
            self.state_manager.save_data('eda_results', eda_results)
            print(" Moving to visualization creation.")
            self.current_step = 6
    
    def step_6_visualization(self):
        """Step 6: Create visualizations"""
        print("\n Step 6: Visualization Creation")
        print("-" * 32)
        
        cleaned_data = self.state_manager.load_data('cleaned_data')
        variables = self.state_manager.load_data('variables')
        
        if not cleaned_data or not variables:
            print(" Missing required data. Please complete previous steps.")
            return
        
        print("Available features for visualization:")
        for i, var in enumerate(variables, 1):
            print(f"{i}. {var}")
        
        selected_features = self.get_user_choice("Enter feature numbers (comma-separated): ").split(',')
        selected_features = [variables[int(i.strip())-1] for i in selected_features if i.strip().isdigit()]
        
        print(" Creating visualizations...")
        visualizations = self.visualization_creator.create_visualizations(cleaned_data, selected_features)
        
        print(f" Created {len(visualizations)} visualizations!")
        
        export_choice = self.get_user_choice("\nExport visualizations to PPT Dashboard? (y/n): ")
        if export_choice.lower() == 'y':
            self.state_manager.add_to_ppt_exports('visualizations', visualizations)
            print(" Visualizations exported to PPT Dashboard")
        
        approval = self.get_user_choice("\nProceed to predictive analytics? (y/n): ")
        if approval.lower() == 'y':
            self.state_manager.save_data('visualizations', visualizations)
            print(" Moving to predictive analytics.")
            self.current_step = 7
    
    def step_7_predictive_analytics(self):
        """Step 7: Predictive analytics"""
        print("\n Step 7: Predictive Analytics")
        print("-" * 31)
        
        cleaned_data = self.state_manager.load_data('cleaned_data')
        if not cleaned_data:
            print(" No cleaned data found. Please complete previous steps.")
            return
        
        print(" Running predictive analytics...")
        predictions = self.predictive_analyzer.analyze(cleaned_data)
        
        print(" Predictive analysis completed!")
        print("Classification metrics:")
        for metric, value in predictions.get('metrics', {}).items():
            print(f"  {metric}: {value}")
        
        export_choice = self.get_user_choice("\nExport predictions to PPT Dashboard? (y/n): ")
        if export_choice.lower() == 'y':
            self.state_manager.add_to_ppt_exports('predictions', predictions)
            print(" Predictions exported to PPT Dashboard")
        
        approval = self.get_user_choice("\nProceed to trend analysis? (y/n): ")
        if approval.lower() == 'y':
            self.state_manager.save_data('predictions', predictions)
            print(" Moving to trend analysis.")
            self.current_step = 8
    
    def step_8_trend_analysis(self):
        """Step 8: Trend analysis"""
        print("\n Step 8: Trend Analysis")
        print("-" * 25)
        
        cleaned_data = self.state_manager.load_data('cleaned_data')
        if not cleaned_data:
            print(" No cleaned data found. Please complete previous steps.")
            return
        
        print(" Analyzing trends...")
        trends = self.trend_analyzer.analyze_trends(cleaned_data)
        
        print(" Trend analysis completed!")
        print("Key trends identified:")
        for trend in trends.get('trends', []):
            print(f"  • {trend}")
        
        export_choice = self.get_user_choice("\nExport trends to PPT Dashboard? (y/n): ")
        if export_choice.lower() == 'y':
            self.state_manager.add_to_ppt_exports('trends', trends)
            print(" Trends exported to PPT Dashboard")
        
        approval = self.get_user_choice("\nProceed to sentiment analysis? (y/n): ")
        if approval.lower() == 'y':
            print(" Moving to sentiment analysis.")
            self.current_step = 9
    
    def step_9_sentiment_analysis(self):
        """Step 9: Sentiment analysis"""
        print("\n Step 9: Sentiment Analysis")
        print("-" * 29)
        
        cleaned_data = self.state_manager.load_data('cleaned_data')
        if not cleaned_data:
            print(" No cleaned data found. Please complete previous steps.")
            return
        
        print(" Analyzing sentiment...")
        sentiment = self.sentiment_analyzer.analyze_sentiment(cleaned_data)
        
        print(" Sentiment analysis completed!")
        print("Sentiment distribution:")
        for sentiment_type, percentage in sentiment.get('distribution', {}).items():
            print(f"  {sentiment_type}: {percentage}%")
        
        export_choice = self.get_user_choice("\nExport sentiment to PPT Dashboard? (y/n): ")
        if export_choice.lower() == 'y':
            self.state_manager.add_to_ppt_exports('sentiment', sentiment)
            print(" Sentiment analysis exported to PPT Dashboard")
        
        approval = self.get_user_choice("\nProceed to A/B testing? (y/n): ")
        if approval.lower() == 'y':
            print(" Moving to A/B testing.")
            self.current_step = 10
    
    def step_10_ab_testing(self):
        """Step 10: A/B testing"""
        print("\n Step 10: A/B Testing")
        print("-" * 22)
        
        cleaned_data = self.state_manager.load_data('cleaned_data')
        if not cleaned_data:
            print(" No cleaned data found. Please complete previous steps.")
            return
        
        print(" Setting up A/B test...")
        ab_results = self.ab_tester.run_ab_test(cleaned_data)
        
        print(" A/B test completed!")
        print("Test results:")
        for result in ab_results.get('results', []):
            print(f"  • {result}")
        
        export_choice = self.get_user_choice("\nExport A/B test to PPT Dashboard? (y/n): ")
        if export_choice.lower() == 'y':
            self.state_manager.add_to_ppt_exports('ab_test', ab_results)
            print(" A/B test results exported to PPT Dashboard")
        
        approval = self.get_user_choice("\nProceed to data chat? (y/n): ")
        if approval.lower() == 'y':
            print(" Moving to data chat interface.")
            self.current_step = 11
    
    def step_11_data_chat(self):
        """Step 11: Chat with data"""
        print("\n Step 11: Chat with Data")
        print("-" * 25)
        
        cleaned_data = self.state_manager.load_data('cleaned_data')
        if not cleaned_data:
            print(" No cleaned data found. Please complete previous steps.")
            return
        
        print(" Data Chat Interface Active")
        print("Type 'exit' to leave chat mode")
        
        while True:
            query = self.get_user_choice("\nAsk about your data: ")
            if query.lower() == 'exit':
                break
            
            response = self.data_chat.process_query(cleaned_data, query)
            print(f" Analysis: {response}")
        
        approval = self.get_user_choice("\nProceed to PPT generation? (y/n): ")
        if approval.lower() == 'y':
            print(" Moving to automated PPT generation.")
            self.current_step = 12
    
    def step_12_ppt_generation(self):
        """Step 12: Generate automated PPT"""
        print("\n Step 12: Automated PPT Generation")
        print("-" * 36)
        
        ppt_exports = self.state_manager.load_data('ppt_exports')
        if not ppt_exports:
            print(" No exported data found for PPT generation.")
            return
        
        print(" Available exports for PPT:")
        for section, data in ppt_exports.items():
            print(f"  • {section.upper()}")
        
        print("\n Generating PowerPoint presentation...")
        ppt_file = self.ppt_generator.generate_presentation(ppt_exports)
        
        print(f" PowerPoint presentation generated: {ppt_file}")
        print(" BI Storyteller analysis complete!")
        
        self.get_user_choice("\nPress Enter to return to main menu...")
    
    def jump_to_step(self):
        """Allow user to jump to a specific step"""
        print("\nAvailable steps:")
        steps = [
            "Variable Extraction",
            "Questionnaire Generation", 
            "Data Generation",
            "Data Cleaning",
            "EDA Analysis",
            "Visualization",
            "Predictive Analytics",
            "Trend Analysis",
            "Sentiment Analysis",
            "A/B Testing",
            "Data Chat",
            "PPT Generation"
        ]
        
        for i, step in enumerate(steps, 1):
            print(f"{i:2d}. {step}")
        
        choice = self.get_user_choice("\nEnter step number (1-12): ")
        try:
            step_num = int(choice)
            if 1 <= step_num <= 12:
                self.current_step = step_num
                print(f" Jumped to Step {step_num}: {steps[step_num-1]}")
            else:
                print(" Invalid step number")
        except ValueError:
            print(" Please enter a valid number")
    
    def view_current_state(self):
        """Display current application state"""
        print("\n Current Application State")
        print("-" * 30)
        
        state_data = self.state_manager.get_all_data()
        for key, value in state_data.items():
            if isinstance(value, (list, dict)):
                print(f"{key.upper()}: {len(value)} items")
            else:
                print(f"{key.upper()}: Available")
        
        print(f"\nCurrent Step: {self.current_step}/12")
        self.get_user_choice("\nPress Enter to continue...")
    
    def export_to_ppt_dashboard(self):
        """Export current data to PPT dashboard"""
        print("\n Export to PPT Dashboard")
        print("-" * 26)
        
        # Show available data for export
        available_data = self.state_manager.get_all_data()
        exportable_items = [key for key in available_data.keys() 
                          if key not in ['ppt_exports', 'business_problem']]
        
        if not exportable_items:
            print(" No data available for export")
            return
        
        print("Available data for export:")
        for i, item in enumerate(exportable_items, 1):
            print(f"{i}. {item.upper()}")
        
        choice = self.get_user_choice("Enter item number to export (or 'all'): ")
        
        if choice.lower() == 'all':
            for item in exportable_items:
                data = self.state_manager.load_data(item)
                self.state_manager.add_to_ppt_exports(item, data)
            print(" All available data exported to PPT Dashboard")
        else:
            try:
                item_index = int(choice) - 1
                if 0 <= item_index < len(exportable_items):
                    item = exportable_items[item_index]
                    data = self.state_manager.load_data(item)
                    self.state_manager.add_to_ppt_exports(item, data)
                    print(f" {item.upper()} exported to PPT Dashboard")
                else:
                    print(" Invalid selection")
            except ValueError:
                print(" Please enter a valid number or 'all'")
    
    def run(self):
        """Main application loop"""
        self.display_welcome()
        
        while True:
            try:
                self.display_menu()
                choice = self.get_user_choice()
                
                if choice == '1':
                    self.execute_current_step()
                elif choice == '2':
                    self.jump_to_step()
                elif choice == '3':
                    self.view_current_state()
                elif choice == '4':
                    self.export_to_ppt_dashboard()
                elif choice == '5':
                    print("\n Thank you for using BI Storyteller!")
                    print("Your analysis data has been saved.")
                    break
                else:
                    print(" Invalid choice. Please select 1-5.")
                    
            except Exception as e:
                self.logger.log(f"Application error: {e}", "ERROR")
                print(f" An error occurred: {e}")
                continue


if __name__ == "__main__":
    app = BIStorytellerApp()
    app.run()