# utils/images/display_logo.py
import streamlit as st

def display_logo():
    st.markdown(
        """
        <style>
        .custom-header {
            font-size: 28px; /* Increase header font size */
            font-weight: bold; /* Make header bold */
            margin-bottom: 10px; /* Add some space below the header */
        }
        
        .logo {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 120px; /* Adjust size as needed */
            height: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    
    st.markdown('<img src="https://cmta.net/wp-content/uploads/california-resources-corporation-logo.jpg" class="logo" alt="California Resources Corporation Logo">', unsafe_allow_html=True)
