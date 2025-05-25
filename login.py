import streamlit as st
import pandas as pd
import os

class LoginPage:
    def __init__(self):
        """Initialize session state if not already set."""
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.user_data = None

    def load_student_data(self, student_id):
        """Load student data from students.csv based on ID."""
        try:
            path = os.path.join(os.path.dirname(__file__), "students.csv")
            students_df = pd.read_csv(path)
            student_data = students_df[students_df["id"] == int(student_id)]
            if student_data.empty:
                return None
            student = student_data.iloc[0]
            return {
                "name": student["name"],
                "id": student["id"]
            }
        except FileNotFoundError:
            st.error("students.csv not found. Please ensure the file exists.")
            return None
        except Exception as e:
            st.error(f"Error loading student data: {str(e)}")
            return None

    def login_page(self):
        """Display login page with role selection for students or admins."""
        st.title("AIU Course Registration System - Login")

        user_type = st.radio("Select User Type", ["Student", "Admin"])

        if user_type == "Student":
            student_id = st.text_input("Student ID")
            if st.button("Login"):
                if student_id:
                    student_data = self.load_student_data(student_id)
                    if student_data:
                        st.session_state.logged_in = True
                        st.session_state.user_type = "Student"
                        st.session_state.user_data = student_data
                        st.success(f"Logged in as {student_data['name']} (ID: {student_id})")
                        st.rerun()
                    else:
                        st.error("Invalid Student ID or student data not found.")
                else:
                    st.error("Please enter a Student ID.")
        else:  # Admin
            username = st.text_input("Username")
            if st.button("Login"):
                if username == "admin":
                    st.session_state.logged_in = True
                    st.session_state.user_type = "Admin"
                    st.session_state.user_data = {"username": "admin"}
                    st.success("Logged in as Admin")
                    st.rerun()
                else:
                    st.error("Invalid username. Only 'admin' is allowed.")

    def logout(self):
        """Clear session state and redirect to login page."""
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.user_data = None
        st.success("Logged out successfully")
        st.rerun()

# Create instance and expose login_page and logout as functions for import
login_page_instance = LoginPage()
login_page = login_page_instance.login_page
logout = login_page_instance.logout