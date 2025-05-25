import streamlit as st
from app import student_ui
from admin_interface import admin_ui
from login import login_page


def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.user_type == "Student":
            student_ui()
        elif st.session_state.user_type == "Admin":
            admin_ui()

if __name__ == "__main__":
    main()