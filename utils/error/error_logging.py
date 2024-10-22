from datetime import datetime
from utils.db_utils import connect_to_mssql

def store_error_log(user_question, error_message, user_email, user_department):
    relevant_info = error_message.split('] ')[-1]
    connection = connect_to_mssql()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO error_log (user_question, error_message, user_email, user_department, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_question,
        relevant_info,
        user_email,
        user_department,
        datetime.now()
    ))
    connection.commit()
    cursor.close()
    connection.close()
