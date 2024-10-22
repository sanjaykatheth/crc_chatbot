import streamlit as st
from streamlit_modal import Modal
import bcrypt

def change_password():
    modal = Modal(key="Change Password Modal", title="Change Password")

    if modal.is_open():
        with modal.container():
            new_password = st.text_input("New Password", type="password", key="new_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

            if st.button('Submit'):
                if new_password and confirm_password:
                    if new_password == confirm_password:
                        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                        # update_user_password(hashed_password)  # Ensure this function updates the password
                        st.success('Your password has been successfully changed.')
                        modal.close()
                    else:
                        st.error('Passwords do not match. Please try again.')
                else:
                    st.error('Please fill in both password fields.')

    return modal
