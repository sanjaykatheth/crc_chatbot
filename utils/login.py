import streamlit as st
import bcrypt
import re  # Import regex module
from utils.history.chat_history import get_user_info, save_new_user
from utils.reset_password import reset_password
from streamlit_modal import Modal
from utils.change_password import change_password
from utils.utility import set_login_state,check_login_state,navigate
def is_valid_email(email):
    """Check if the provided email address is valid."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def login():
    modal = reset_password()  # Correctly calling the modal function

    st.markdown("""<style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }
       .error-message {
            color: red; /* Set error color */
            margin: 10px 0; /* Adjust margin as needed */
            text-align: left; /* Align text to the left */
            font-weight: bold; /* Optional: make it bold */
            padding-left: 210px; /* Adjust left padding to shift more left */
            margin-left:  0px; /* Negative margin to shift further left */
        }
        .left-section {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .right-section {
            flex: 1;
            background-color: #000;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-form {
            text-align: center;
            width: 100%;
            max-width: 400px;
        }
        .login-form h1 {
            font-size: 36px;
            margin-bottom: 10px;
            color: #fff;
        }
        .login-form input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            background-color: #333;
            border: none;
            border-radius: 5px;
            color: #fff;
        }
        .forgot-password {
            margin-top: 10px;
            color: #007BFF; /* Bootstrap primary color */
            cursor: pointer;
        }
        .logo {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 140px; /* Adjust size as needed */
            height: auto;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="left-section"><img src="https://img.lovepik.com/element/45009/2341.png_300.png" alt="Calendar and Clock" style="width: 38%; height: 60%;"></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<img src="https://cmta.net/wp-content/uploads/california-resources-corporation-logo.jpg" class="logo" alt="California Resources Corporation Logo">', unsafe_allow_html=True)
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        st.markdown('<h1>LOG IN</h1>', unsafe_allow_html=True)
        st.markdown('<p>Log In with your registered email address</p>', unsafe_allow_html=True)

        # Email input
        email = st.text_input("Email Address", placeholder="Email Address", key="email_input")
        # Password input
        password = st.text_input("Password", type="password", placeholder="Password", key="password_input")

        # Create columns for buttons and a dedicated area for the error message
        left_space, button_col, right_space = st.columns([2, 3.2, 1.1])  # Adjust the widths as needed

        with left_space:
            pass  # This column creates space

        with button_col:
            # Login button
            if st.button("Log In"):
                print(f"Login attempt for email: {email}")
                st.session_state["email"] = email
                
                if not is_valid_email(email):
                    st.session_state["error_message"] = "Invalid email format. Please enter a valid email address."
                else:
                    user_info = get_user_info(email)

                    if user_info:
                        user_id, department, stored_password = user_info
                        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                            user_data = {
                                "email": email,
                                "department": department
                            }
                            st.session_state.update(user_data)
                            set_login_state(True, user_data)
                            st.success(f"Logged in successfully! Your department is: {department}.")
                            st.session_state["message_type"] = "success"
                            st.session_state["logged_in"] = True
                            st.session_state["user_email"] = email
                            st.session_state["user_id"] = user_id
                            st.session_state["user_department"] = department
                            st.session_state["message_type"] = "success"
                            navigate("home")
                            st.rerun()
                        else:
                            st.session_state["error_message"] = "Invalid password. Please try again."
                    else:
                        st.session_state["new_user"] = True 
                        st.session_state["error_message"] = "Your email is not present. Please select your department to sign up."


        # Create a new row for the error message
        if "error_message" in st.session_state:
            error_col = st.empty()  # Create an empty placeholder
            with error_col:
                st.markdown('<div class="error-message">{}</div>'.format(st.session_state["error_message"]), unsafe_allow_html=True)
            del st.session_state["error_message"]  # Clear the error message after displaying

        with right_space:
            # Forgot password button
            if st.button("Forgot Password?", key="forgot_password"):
                modal.open()  # Open the modal directly

        st.markdown('</div>', unsafe_allow_html=True)

        if "new_user" in st.session_state and st.session_state["new_user"]:
            st.markdown('<h2>Select Your Department</h2>', unsafe_allow_html=True)
            department_options = ["Regulatory Compliance"]
            selected_department = st.selectbox("Select your department", department_options, key="department_select")

            if st.button("Sign-up"):
                if selected_department:
                    with st.spinner("Saving user information and logging in..."):
                        save_new_user(st.session_state["email"], selected_department)
                        st.session_state["logged_in"] = True
                        st.session_state["user_email"] = st.session_state["email"]
                        st.session_state["user_department"] = selected_department
                        st.session_state["message"] = "User information saved and logged in successfully!"
                        st.session_state["message_type"] = "success"
                        del st.session_state["email"]
                        del st.session_state["new_user"]
                        st.session_state["page"] = 'dashboard'
                        st.rerun()
                else:
                    st.error("Please select a department.")

        if "message" in st.session_state:
            if st.session_state["message_type"] == "success":
                st.success(st.session_state["message"])
            else:
                st.error(st.session_state["message"])
            del st.session_state["message"]
            del st.session_state["message_type"]

    # if st.session_state.get("logged_in"):
    #     st.title("Dashboard")
    #     st.write(f"Welcome, {st.session_state['user_email']} from {st.session_state['user_department']} department!")

if __name__ == "__main__":
    login()
