# utils/db_utils.py

import pyodbc
import os

def connect_to_mssql():
    
    db_name = os.getenv("DB_NAME")
    db_username = os.getenv("DB_USERNAME")
    db_password = os.getenv("DB_PASSWORD")
    db_server = os.getenv("DB_SERVER")
    
    connection = pyodbc.connect(
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server={db_server};"
        f"Database={db_name};"
        f"UID={db_username};"
        f"PWD={db_password};"
    )
    
    return connection
