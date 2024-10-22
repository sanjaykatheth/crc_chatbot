import streamlit as st
import json
from streamlit_cookies_manager import EncryptedCookieManager

# Create a cookie manager
cookies = EncryptedCookieManager(
    prefix="myapp",  
    password="a_very_secure_password_for_cookies_encryption"  
)

# Ensure cookies are initialized
if not cookies.ready():
    st.stop()  # Wait until the cookie manager is ready

# Set the login state in cookies
def set_login_state(is_logged_in, user_data=None):
    cookies["logged_in"] = "true" if is_logged_in else "false"
    if user_data:
        cookies["user_data"] = json.dumps(user_data)
    else:
        cookies["user_data"] = ""
    cookies.save()

def logout():
    cookies.pop("user_data", None)  # Remove user_data cookie
    cookies.pop("logged_in", None)  # Remove logged_in cookie
    cookies.save()

# Check the login state from cookies
def check_login_state():
    if cookies.get("logged_in") == "true":
        return True, json.loads(cookies.get("user_data", "{}"))
    return False, {}

# Navigate to a specified page
def navigate(page):
    st.query_params = {"page": page}
    # st.experimental_set_query_params(page=page)  # This is a necessary step for now.
