import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
import streamlit as st
import json
from datetime import datetime

class DatabaseClient:
    def __init__(self):
        """Initialize database connection"""
        self.engine = None
        self.connect()
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            database_url = os.getenv('DATABASE_URL')
            if database_url:
                self.engine = create_engine(database_url)
                # Test connection
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                st.success("Database connected successfully!")
            else:
                st.error("Database URL not found in environment variables")
        except Exception as e:
            st.error(f"Database connection failed: {str(e)}")
            self.engine = None
    
    def create_survey_table(self, questionnaire_data):
        """Create a table for survey responses based on questionnaire structure"""
        if not self.engine:
            return False
            
        try:
            table_name = f"survey_{questionnaire_data.get('id', 'default')}"
            
            # Build CREATE TABLE SQL
            columns = ["id SERIAL PRIMARY KEY", "submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"]
            
            for i, question in enumerate(questionnaire_data.get('questions', [])):
                question_id = question.get('id', f"question_{i+1}")
                question_type = question.get('type', question.get('question_type', 'text'))
                
                if question_type in ['text', 'email']:
                    columns.append(f"{question_id} TEXT")
                elif question_type in ['number', 'rating']:
                    columns.append(f"{question_id} NUMERIC")
                elif question_type == 'select':
                    columns.append(f"{question_id} TEXT")
                elif question_type == 'multiselect':
                    columns.append(f"{question_id} TEXT[]")
                elif question_type == 'boolean':
                    columns.append(f"{question_id} BOOLEAN")
                elif question_type == 'date':
                    columns.append(f"{question_id} DATE")
                else:
                    columns.append(f"{question_id} TEXT")
            
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            
            with self.engine.connect() as conn:
                conn.execute(text(create_sql))
                conn.commit()
            
            return table_name
            
        except Exception as e:
            st.error(f"Failed to create survey table: {str(e)}")
            return False
    
    def submit_survey_response(self, table_name, response_data):
        """Submit a survey response to the database"""
        if not self.engine:
            return False
            
        try:
            # Prepare data for insertion
            columns = list(response_data.keys())
            values = []
            
            for value in response_data.values():
                if isinstance(value, list):
                    # Handle multiselect as array
                    values.append(value)
                elif isinstance(value, bool):
                    values.append(value)
                elif isinstance(value, (int, float)):
                    values.append(value)
                else:
                    values.append(str(value))
            
            # Build INSERT SQL
            placeholders = ', '.join([f':{col}' for col in columns])
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            with self.engine.connect() as conn:
                conn.execute(text(insert_sql), response_data)
                conn.commit()
            
            return True
            
        except Exception as e:
            st.error(f"Failed to submit response: {str(e)}")
            return False
    
    def get_survey_responses(self, table_name):
        """Retrieve all survey responses from database"""
        if not self.engine:
            return None
            
        try:
            query = f"SELECT * FROM {table_name} ORDER BY submitted_at DESC"
            df = pd.read_sql(query, self.engine)
            return df
            
        except Exception as e:
            st.error(f"Failed to retrieve responses: {str(e)}")
            return None
    
    def get_response_count(self, table_name):
        """Get total count of responses"""
        if not self.engine:
            return 0
            
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                return result.scalar()
                
        except Exception as e:
            return 0
    
    def table_exists(self, table_name):
        """Check if table exists"""
        if not self.engine:
            return False
            
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = :table_name
                    )
                """), {"table_name": table_name})
                return result.scalar()
                
        except Exception as e:
            return False
    
    def delete_table(self, table_name):
        """Delete a survey table"""
        if not self.engine:
            return False
            
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                conn.commit()
            return True
            
        except Exception as e:
            st.error(f"Failed to delete table: {str(e)}")
            return False
    
    def clear_survey_responses(self, table_name):
        """Clear all responses from survey table"""
        if not self.engine:
            return False
            
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"DELETE FROM {table_name} WHERE id > 0"))
                conn.commit()
            return True
            
        except Exception as e:
            st.error(f"Failed to clear survey responses: {str(e)}")
            return False