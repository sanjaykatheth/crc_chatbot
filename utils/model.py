# utils/modal.py
import streamlit as st
from streamlit_modal import Modal

def reset_password():
    modal = Modal(key="Password Reset Modal", title="Password Reset")
    
    if modal.is_open():
        with modal.container():
            st.markdown('Please enter your new password and confirm it.')
            new_password = st.text_input('New Password', type='password')
            confirm_password = st.text_input('Confirm Password', type='password')

            # Create columns for layout
            col1, col2 = st.columns([3, 2])  # Adjust the ratios as needed
            
            with col1:
                # Empty space or additional content can go here
                pass
            
            with col2:
                if st.button('Submit'):
                    if new_password == confirm_password:
                        # Here you can add functionality to save the new password
                        st.success('Password updated successfully!')
                        modal.close()
                    else:
                        st.error('Passwords do not match!')

    return modal
