import os
import streamlit as st
from vanna.remote import VannaDefault
from dotenv import load_dotenv
from utils.crc_train import CustomTraining
from utils.VN_Singleton import VannaSingleton

@st.cache_resource(ttl=3600)
def setup_connexion():
        load_dotenv()
        vn = VannaSingleton.getVN()
        # vn = VannaDefault(model=os.environ.get("VANNA_MODEL"), api_key=os.environ.get("VANNA_API_KEY"))
        
        # # vn.connect_to_bigquery(
        # #     project_id=os.environ.get("GCP_PROJECT_ID"),
        # # )
        # db_name = os.getenv("DB_NAME")
        # db_username = os.getenv("DB_USERNAME")
        # db_password = os.getenv("DB_PASSWORD")
        # db_server = os.getenv("DB_SERVER")

        # connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={db_server};DATABASE={db_name};UID={db_username};PWD={db_password}'
        # vn.connect_to_mssql(odbc_conn_str=connection_string) # You can use the ODBC connection string here
        # CustomTraining(vn)


def setup_session_state():
    st.session_state["my_question"] = None
