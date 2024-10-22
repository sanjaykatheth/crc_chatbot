# session_manager.py


from .login import login  # Import the login function directly
import streamlit as st

def check_login():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        login()
    else:
        return True