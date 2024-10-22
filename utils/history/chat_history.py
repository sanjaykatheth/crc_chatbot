import pandas as pd
from datetime import datetime
from utils.db_utils import connect_to_mssql
import streamlit as st
import requests
import json
import bcrypt
from flask_bcrypt import Bcrypt
from streamlit_modal import Modal



def get_existing_chat_data(user_question):
    connection = connect_to_mssql()
    query = """
        SELECT user_question, sql_query, sql_result, plot_code
        FROM chat_history_collection
        WHERE user_question = ?
    """
    chat_data_df = pd.read_sql(query, connection, params=[user_question])
    connection.close()
    
    if not chat_data_df.empty:
        chat_data = chat_data_df.iloc[0]
        chat_data['sql_result'] = pd.read_json(chat_data['sql_result']) if chat_data['sql_result'] is not None else None
        return chat_data
    return None

def store_chat_history_mssql(chat_session_object):
    try:
        connection = connect_to_mssql()
        cursor = connection.cursor()
        cursor.execute(""" 
            INSERT INTO chat_history_collection (user_question, sql_query, sql_result, plot_code, created_at, user_department, user_email, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chat_session_object.user_question,
            chat_session_object.sql,
            chat_session_object.sql_result.to_json() if isinstance(chat_session_object.sql_result, pd.DataFrame) else None,
            chat_session_object.plot_code,
            datetime.now(),  # Ensure datetime is first
            chat_session_object.user_department,
            chat_session_object.user_email,  # Add user_email here
            chat_session_object.user_id
        ))
        connection.commit()
    except Exception as e:
        print(f"Error while storing chat history: {e}")
    finally:
        cursor.close()
        connection.close()

def retrieve_chat_history_mssql():
    connection = connect_to_mssql()
    query = """
        SELECT user_question 
        FROM chat_history_collection 
        WHERE created_at >= DATEADD(hour, -5, GETDATE())
    """
    chat_history_df = pd.read_sql(query, connection)
    connection.close()
    return chat_history_df

def get_default_questions():
    user_department = st.session_state.get("user_department")
    if not user_department:
        return []

    connection = connect_to_mssql()
    query = """
        SELECT DISTINCT user_question 
        FROM chat_history_collection
        WHERE user_department = ?
    """
    
    default_questions_df = pd.read_sql(query, connection, params=[user_department])
    connection.close()
    
    return default_questions_df['user_question'].tolist() if not default_questions_df.empty else []

def get_default_questions_by_email(user_email):
    if not user_email:
        return []
    connection = connect_to_mssql()
    query = """SELECT DISTINCT user_question
               FROM chat_history_collection
               WHERE user_email = ?"""
    email_questions_df = pd.read_sql(query, connection, params=[user_email])
    connection.close()
    return email_questions_df['user_question'].tolist() if not email_questions_df.empty else []


def get_suggested_questions(keyword):
    user_department = st.session_state.get("user_department")
    if not user_department:
        return []

    connection = connect_to_mssql()
    query = """
        SELECT DISTINCT user_question 
        FROM chat_history_collection
        WHERE user_question LIKE ?
        
        AND user_department = ?
    """
    
    keyword = f"%{keyword}%"
    suggested_questions_df = pd.read_sql(query, connection, params=[keyword, user_department])
    connection.close()
    
    return suggested_questions_df['user_question'].tolist() if not suggested_questions_df.empty else []

def get_global_suggested_questions(keyword):
    connection = connect_to_mssql()
    query = """
        SELECT DISTINCT user_question 
        FROM chat_history_collection
        WHERE user_question LIKE ?
    """
    
    keyword = f"%{keyword}%"
    suggested_questions_df = pd.read_sql(query, connection, params=[keyword])
    connection.close()
    
    return suggested_questions_df['user_question'].tolist() if not suggested_questions_df.empty else []

def get_new_global_suggested_questions(keyword):
    # Fetch data from the database
    connection = connect_to_mssql()
    query = """
        SELECT DISTINCT user_question 
        FROM chat_history_collection
        WHERE user_question LIKE ?
    """
    
    keyword = f"%{keyword}%"
    suggested_questions_df = pd.read_sql(query, connection, params=[keyword])
    connection.close()

    if not suggested_questions_df.empty:
        return json.dumps({"suggested_questions": suggested_questions_df['user_question'].tolist()})
    
    return json.dumps({"suggested_questions": []})

def get_user_questions_count(user_email):
    if not user_email:
        return 0
    connection = connect_to_mssql()
    query = """SELECT COUNT(DISTINCT user_question) AS question_count
               FROM chat_history_collection
               WHERE user_email = ?"""
    count_df = pd.read_sql(query, connection, params=[user_email])
    connection.close()
    return count_df['question_count'].iloc[0] if not count_df.empty else 0


def get_user_info(email):
    connection = connect_to_mssql()
    cursor = connection.cursor()
    
    query = """
        SELECT user_id, department, password FROM user_login 
        WHERE email = ?
    """
    
    cursor.execute(query, (email,))
    user_info = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return user_info if user_info else None



bcrypt = Bcrypt()  # This should be initialized where your Flask app is created

def save_new_user(email, department):
    connection = connect_to_mssql()  # Ensure this function is defined
    cursor = connection.cursor()

    # Use a default password
    default_password = "admin@123"
    hashed_password = bcrypt.generate_password_hash(default_password).decode('utf-8')

    cursor.execute(""" 
        INSERT INTO user_login (email, department, password, created_at) 
        VALUES (?, ?, ?, ?) 
    """, (email, department, hashed_password, datetime.now()))

    connection.commit()
    cursor.close()
    connection.close()

def update_user_password(email, new_password):
    connection = connect_to_mssql()
    cursor = connection.cursor()
    
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cursor.execute("""
        UPDATE user_login SET password = ? WHERE email = ?
    """, (hashed_password, email))

    connection.commit()
    cursor.close()
    connection.close()

def check_email_registered(email):
    connection = connect_to_mssql()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM user_login WHERE email = ?", (email,))
    count = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return count > 0

def get_default_questions_by_department(user_department):
    if not user_department:
        return []
    connection = connect_to_mssql()
    query = """
    SELECT user_question
    FROM (
        SELECT DISTINCT user_question, created_at
        FROM chat_history_collection
        WHERE user_department = ?
    ) subquery
    ORDER BY created_at DESC
    """
    department_questions_df = pd.read_sql(query, connection, params=[user_department])
    connection.close()
    return department_questions_df['user_question'].tolist() if not department_questions_df.empty else []


def get_default_questions_by_department(user_department, logged_in_user_email):
    if not user_department:
        return []
    connection = connect_to_mssql()
    query = """
    SELECT user_question
    FROM (
        SELECT DISTINCT user_question, created_at
        FROM chat_history_collection
        WHERE user_department = ?
        AND user_email != ?
    ) subquery
    ORDER BY created_at DESC
    """
    department_questions_df = pd.read_sql(query, connection, params=[user_department, logged_in_user_email])
    connection.close()
    return department_questions_df['user_question'].tolist() if not department_questions_df.empty else []



def get_default_questions_by_email(user_email):
    if not user_email:
        return []
    connection = connect_to_mssql()
    query = """
    SELECT user_question
    FROM (
        SELECT DISTINCT user_question, created_at
        FROM chat_history_collection
        WHERE user_email = ?
    ) subquery
    ORDER BY created_at DESC
    """
    email_questions_df = pd.read_sql(query, connection, params=[user_email])
    connection.close()
    return email_questions_df['user_question'].tolist() if not email_questions_df.empty else []

