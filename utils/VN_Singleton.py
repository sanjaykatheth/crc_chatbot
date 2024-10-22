import os
from vanna.remote import VannaDefault
from dotenv import load_dotenv
from utils.crc_train import CustomTraining

class VannaSingleton:
    _instance = None
    _vn = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialize_vanna()
        return cls._instance

    def initialize_vanna():
        load_dotenv()
        vn = VannaDefault(model=os.environ.get("VANNA_MODEL"), api_key=os.environ.get("VANNA_API_KEY"))
        
        db_name = os.getenv("DB_NAME")
        db_username = os.getenv("DB_USERNAME")
        db_password = os.getenv("DB_PASSWORD")
        db_server = os.getenv("DB_SERVER")
        db_port = os.getenv("DB_PORT")
    
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={db_server},{db_port};DATABASE={db_name};UID={db_username};PWD={db_password}'
        # print(connection_string)
        vn.connect_to_mssql(odbc_conn_str=connection_string)
        VannaSingleton._vn = vn
        CustomTraining(vn)
    
    def getVN():
        if VannaSingleton._vn is None:
            VannaSingleton.initialize_vanna()
        return VannaSingleton._vn
