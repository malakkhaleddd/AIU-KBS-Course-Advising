import streamlit as st
from editor import add_course, load_courses_list, load_course_details, edit_course, delete_course
from login import logout
import pandas as pd
import os

def admin_ui():
    # Add logout button at the top
    if st.button("Back to Login Page"):
        logout()

    st.header("Admin Interface - Course Management")

    # Radio buttons for selecting action
    action = st.radio("Select Action", ["Add Course", "Edit Course", "Delete Course", "View All Courses"])

    if action == "Add Course":
        st.subheader("Add a New Course")
        course_code = st.text_input("Course Code")
        course_name = st.text_input("Course Name")
        description = st.text_area("Description")
        prerequisites = st.text_input("Prerequisites (comma-separated)")
        co_requisites = st.text_input("Co-requisites (comma-separated)")
        credit_hours = st.number_input("Credit Hours", min_value=0, step=1)
        semester_offered = st.selectbox("Semester Offered", ["Fall", "Spring", "Both"])
        semester = st.number_input("Semester", min_value=1, max_value=12, step=1)
        category = st.selectbox("Category", [
            "Core", "E1", "E2", "E3", "E4", "E5", "E6", "University Requirement", "University Elective"
        ])

        if st.button("Add Course"):
            if course_code and course_name:
                result = add_course(
                    course_code, course_name, description, prerequisites, co_requisites,
                    credit_hours, semester_offered, semester, category
                )
                st.success(result)
            else:
                st.error("Course Code and Course Name are required.")

    elif action == "Edit Course":
        st.subheader("Edit an Existing Course")
        course_codes = load_courses_list()
        if not course_codes:
            st.error("No courses available to edit.")
            return

        selected_code = st.selectbox("Select Course to Edit", course_codes)
        course_details = load_course_details(selected_code)

        if course_details:
            course_name = st.text_input("Course Name", value=course_details["name"])
            description = st.text_area("Description", value=course_details["description"])
            prerequisites = st.text_input("Prerequisites (comma-separated)", value=",".join(course_details["prerequisites"]))
            co_requisites = st.text_input("Co-requisites (comma-separated)", value=",".join(course_details["co_requisites"]))
            credit_hours = st.number_input("Credit Hours", min_value=0, step=1, value=course_details["credit_hours"])
            semester_offered = st.selectbox("Semester Offered", ["Fall", "Spring", "Both"], index=["Fall", "Spring", "Both"].index(course_details["semester_offered"]))
            semester = st.number_input("Semester", min_value=1, max_value=12, step=1, value=course_details["semester"])
            category = st.selectbox("Category", [
                "Core", "E1", "E2", "E3", "E4", "E5", "E6", "University Requirement", "University Elective"
            ], index=["Core", "E1", "E2", "E3", "E4", "E5", "E6", "University Requirement", "University Elective"].index(course_details["category"]))

            if st.button("Update Course"):
                if selected_code and course_name:
                    result = edit_course(
                        selected_code, course_name, description, prerequisites, co_requisites,
                        credit_hours, semester_offered, semester, category
                    )
                    st.success(result)
                else:
                    st.error("Course Code and Course Name are required.")
        else:
            st.error("Course details not found.")

    elif action == "Delete Course":
        st.subheader("Delete a Course")
        course_codes = load_courses_list()
        if not course_codes:
            st.error("No courses available to delete.")
            return

        selected_code = st.selectbox("Select Course to Delete", course_codes)
        if st.button("Delete Course"):
            result = delete_course(selected_code)
            st.success(result)

    elif action == "View All Courses":
        st.subheader("All Courses")
        # Define CSV files for all course categories
        CSV_FILES = {
            "Core": "courses1.csv",
            "E1": "E1.csv",
            "E2": "Elective E2 Courses1.csv",
            "E3": "Elective E3 Courses1.csv",
            "E4": "E4.csv",
            "E5": "E5.csv",
            "E6": "Elective E6 Courses1.csv",
            "University Requirement": "University Requirement Courses1.csv",
            "University Elective": "Elective University Courses1.csv"
        }

        # Initialize an empty DataFrame to store all courses
        all_courses_df = pd.DataFrame(columns=[
            "CourseCode", "CourseName", "Description", "Prerequisites",
            "CoRequisites", "CreditHours", "SemesterOffered", "Semester", "Category"
        ])

        # Load and combine data from all CSV files
        for category, file_path in CSV_FILES.items():
            try:
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path)
                    # Ensure all expected columns are present
                    for col in all_courses_df.columns:
                        if col not in df.columns:
                            df[col] = ""  # Add missing columns with empty strings
                    # Assign category
                    df["Category"] = category
                    # Select and reorder columns to match expected structure
                    df = df[["CourseCode", "CourseName", "Description", "Prerequisites",
                             "CoRequisites", "CreditHours", "SemesterOffered", "Semester", "Category"]]
                    all_courses_df = pd.concat([all_courses_df, df], ignore_index=True)
                else:
                    st.warning(f"{file_path} not found for category {category}.")
            except Exception as e:
                st.error(f"Error loading {file_path}: {str(e)}")

        if not all_courses_df.empty:
            # Display the combined courses in a table
            st.dataframe(all_courses_df, use_container_width=True)
        else:
            st.error("No course data available to display.")

if __name__ == "__main__":
    admin_ui()