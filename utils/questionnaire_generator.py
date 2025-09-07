"""
Questionnaire Generator Module
Creates comprehensive questionnaires based on extracted variables
"""

import random
from typing import List, Dict, Any


class QuestionnaireGenerator:
    """Generate questionnaires from business variables"""
    
    def __init__(self):
        self.question_templates = {
            'demographic': [
                "What is your age group?",
                "What is your gender?",
                "What is your income level?",
                "What is your education level?",
                "Where are you located?"
            ],
            'behavioral': [
                "How frequently do you {action}?",
                "When do you typically {action}?",
                "What influences your decision to {action}?",
                "How do you prefer to {action}?"
            ],
            'satisfaction': [
                "How satisfied are you with {subject}?",
                "How would you rate {subject}?",
                "What do you like most about {subject}?",
                "What improvements would you suggest for {subject}?"
            ],
            'preference': [
                "Which {option} do you prefer?",
                "What factors are most important when choosing {subject}?",
                "How do you compare different {options}?",
                "What would make you switch to a different {option}?"
            ]
        }
        
        self.mcq_options = {
            'age': ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"],
            'gender': ["Male", "Female", "Non-binary", "Prefer not to say"],
            'income': ["<$25k", "$25k-$50k", "$50k-$75k", "$75k-$100k", ">$100k"],
            'education': ["High School", "Bachelor's", "Master's", "PhD", "Other"],
            'frequency': ["Daily", "Weekly", "Monthly", "Rarely", "Never"],
            'satisfaction': ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"],
            'rating': ["Excellent", "Good", "Average", "Poor", "Very Poor"],
            'importance': ["Very Important", "Important", "Neutral", "Not Important", "Not Important at All"]
        }
    
    def generate_questionnaire(self, variables: List[str]) -> List[Dict[str, Any]]:
        """Generate a complete questionnaire from variables"""
        questionnaire = []
        
        # Add demographic questions first
        demographic_questions = self._generate_demographic_questions()
        questionnaire.extend(demographic_questions)
        
        # Generate questions for each variable
        for variable in variables:
            var_questions = self._generate_variable_questions(variable)
            questionnaire.extend(var_questions)
        
        # Add open-ended questions
        open_ended = self._generate_open_ended_questions()
        questionnaire.extend(open_ended)
        
        return questionnaire
    
    def _generate_demographic_questions(self) -> List[Dict[str, Any]]:
        """Generate standard demographic questions"""
        questions = []
        
        demographics = [
            ("What is your age group?", "age"),
            ("What is your gender?", "gender"),
            ("What is your annual income level?", "income"),
            ("What is your highest education level?", "education")
        ]
        
        for question_text, category in demographics:
            question = {
                "question": question_text,
                "type": "MCQ",
                "category": "demographic",
                "options": self.mcq_options.get(category, ["Option 1", "Option 2", "Option 3", "Option 4"])
            }
            questions.append(question)
        
        return questions
    
    def _generate_variable_questions(self, variable: str) -> List[Dict[str, Any]]:
        """Generate questions specific to a variable"""
        questions = []
        var_lower = variable.lower()
        
        # Determine question type based on variable
        if any(word in var_lower for word in ['satisfaction', 'quality', 'rating']):
            questions.extend(self._create_satisfaction_questions(variable))
        elif any(word in var_lower for word in ['frequency', 'behavior', 'usage']):
            questions.extend(self._create_behavioral_questions(variable))
        elif any(word in var_lower for word in ['preference', 'choice', 'selection']):
            questions.extend(self._create_preference_questions(variable))
        else:
            questions.extend(self._create_general_questions(variable))
        
        return questions
    
    def _create_satisfaction_questions(self, variable: str) -> List[Dict[str, Any]]:
        """Create satisfaction-related questions"""
        subject = variable.replace('Analysis', '').replace('Satisfaction', '').strip()
        
        questions = [
            {
                "question": f"How satisfied are you with {subject.lower()}?",
                "type": "MCQ",
                "category": "satisfaction",
                "options": self.mcq_options["satisfaction"]
            },
            {
                "question": f"How would you rate the overall {subject.lower()}?",
                "type": "MCQ",
                "category": "rating",
                "options": self.mcq_options["rating"]
            },
            {
                "question": f"What aspects of {subject.lower()} are most important to you?",
                "type": "Descriptive",
                "category": "preference"
            }
        ]
        
        return questions
    
    def _create_behavioral_questions(self, variable: str) -> List[Dict[str, Any]]:
        """Create behavior-related questions"""
        behavior = variable.replace('Analysis', '').replace('Behavior', '').strip()
        
        questions = [
            {
                "question": f"How often do you engage with {behavior.lower()}?",
                "type": "MCQ",
                "category": "frequency",
                "options": self.mcq_options["frequency"]
            },
            {
                "question": f"What motivates your {behavior.lower()} behavior?",
                "type": "Descriptive",
                "category": "motivation"
            },
            {
                "question": f"When do you typically engage in {behavior.lower()}?",
                "type": "MCQ",
                "category": "timing",
                "options": ["Morning", "Afternoon", "Evening", "Night", "Varies"]
            }
        ]
        
        return questions
    
    def _create_preference_questions(self, variable: str) -> List[Dict[str, Any]]:
        """Create preference-related questions"""
        subject = variable.replace('Analysis', '').replace('Preference', '').strip()
        
        questions = [
            {
                "question": f"What factors influence your {subject.lower()} preferences?",
                "type": "Descriptive",
                "category": "factors"
            },
            {
                "question": f"How important is {subject.lower()} in your decision-making?",
                "type": "MCQ",
                "category": "importance",
                "options": self.mcq_options["importance"]
            }
        ]
        
        return questions
    
    def _create_general_questions(self, variable: str) -> List[Dict[str, Any]]:
        """Create general questions for any variable"""
        subject = variable.replace('Analysis', '').strip()
        
        questions = [
            {
                "question": f"How familiar are you with {subject.lower()}?",
                "type": "MCQ",
                "category": "familiarity",
                "options": ["Very Familiar", "Familiar", "Somewhat Familiar", "Not Familiar", "Never Heard Of"]
            },
            {
                "question": f"What is your experience with {subject.lower()}?",
                "type": "Descriptive",
                "category": "experience"
            }
        ]
        
        return questions
    
    def _generate_open_ended_questions(self) -> List[Dict[str, Any]]:
        """Generate open-ended questions for additional insights"""
        questions = [
            {
                "question": "What additional comments or suggestions do you have?",
                "type": "Descriptive",
                "category": "feedback"
            },
            {
                "question": "Is there anything else you'd like us to know?",
                "type": "Descriptive",
                "category": "additional"
            }
        ]
        
        return questions
    
    def modify_questionnaire(self, questionnaire: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Allow interactive modification of questionnaire"""
        print("\n🔧 Questionnaire Modification Mode")
        print("Commands: 'add', 'remove [number]', 'edit [number]', 'done'")
        
        while True:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'done':
                break
            elif command == 'add':
                new_question = self._add_question()
                if new_question:
                    questionnaire.append(new_question)
                    print("✅ Question added successfully!")
            elif command.startswith('remove'):
                try:
                    parts = command.split()
                    if len(parts) > 1:
                        index = int(parts[1]) - 1
                        if 0 <= index < len(questionnaire):
                            removed = questionnaire.pop(index)
                            print(f"✅ Removed: {removed['question']}")
                        else:
                            print("❌ Invalid question number")
                    else:
                        print("❌ Please specify question number to remove")
                except (ValueError, IndexError):
                    print("❌ Invalid remove command format")
            elif command.startswith('edit'):
                try:
                    parts = command.split()
                    if len(parts) > 1:
                        index = int(parts[1]) - 1
                        if 0 <= index < len(questionnaire):
                            questionnaire[index] = self._edit_question(questionnaire[index])
                            print("✅ Question edited successfully!")
                        else:
                            print("❌ Invalid question number")
                    else:
                        print("❌ Please specify question number to edit")
                except (ValueError, IndexError):
                    print("❌ Invalid edit command format")
            else:
                print("❌ Unknown command. Use 'add', 'remove [number]', 'edit [number]', or 'done'")
        
        return questionnaire
    
    def _add_question(self) -> Dict[str, Any]:
        """Add a new question interactively"""
        question_text = input("Enter question text: ").strip()
        if not question_text:
            print("❌ Question text cannot be empty")
            return None
        
        question_type = input("Question type (MCQ/Descriptive): ").strip()
        if question_type not in ['MCQ', 'Descriptive']:
            print("❌ Invalid question type")
            return None
        
        question = {
            "question": question_text,
            "type": question_type,
            "category": "custom"
        }
        
        if question_type == 'MCQ':
            options = []
            print("Enter options (press Enter twice to finish):")
            while True:
                option = input(f"Option {len(options) + 1}: ").strip()
                if not option:
                    break
                options.append(option)
            
            if len(options) < 2:
                print("❌ MCQ questions need at least 2 options")
                return None
            
            question["options"] = options
        
        return question
    
    def _edit_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Edit an existing question"""
        print(f"\nEditing: {question['question']}")
        
        new_text = input(f"New question text (current: {question['question']}): ").strip()
        if new_text:
            question['question'] = new_text
        
        if question['type'] == 'MCQ' and 'options' in question:
            edit_options = input("Edit options? (y/n): ").strip().lower()
            if edit_options == 'y':
                new_options = []
                print("Enter new options (press Enter twice to finish):")
                while True:
                    option = input(f"Option {len(new_options) + 1}: ").strip()
                    if not option:
                        break
                    new_options.append(option)
                
                if len(new_options) >= 2:
                    question['options'] = new_options
        
        return question