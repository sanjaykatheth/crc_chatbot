import streamlit as st
from streamlit_modal import Modal
import bcrypt
from utils.history.chat_history import update_user_password, check_email_registered  # Ensure you have the necessary functions

def reset_password():
    modal = Modal(key="Password Reset Modal", title="Password Reset")

    if modal.is_open():
        with modal.container():
            # Create three separate columns for better layout control
            email_col, spacer_col, button_col = st.columns([2, 1, 1])  # Adjust widths as needed

            with email_col:
                st.text("Enter your registered email:")  # Label above the input
                # Use a unique key and set autocomplete to "off"
                user_email = st.text_input("", key="reset_email_unique", autocomplete="off")  

            with button_col:
                if st.button('Continue'):
                    if user_email:
                        if check_email_registered(user_email):
                            st.success('A password reset link has been sent to your email. Please check your inbox.')
                            modal.close()
                        else:
                            st.error('This email is not registered. Please try again.')
                    else:
                        st.error('Please enter an email address.')

    return modal
