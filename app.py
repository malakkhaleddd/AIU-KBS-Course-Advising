import streamlit as st
import pandas as pd
from inference import recommend_courses
from login import logout

def student_ui():
    # Add logout button at the top
    if st.button("Back to Login Page"):
        logout()

    st.header("Enter Your Information")

    semester = st.number_input("Semester", min_value=1, max_value=12, step=1)
    cgpa = st.number_input("CGPA", min_value=0.0, max_value=4.0, step=0.1)
    total_credits = st.number_input("Total Credits Passed", min_value=0, step=1)
    current_semester = st.selectbox("Current Semester", ["Fall", "Spring"])

    # Load main courses
    try:
        courses = pd.read_csv("courses1.csv")
    except FileNotFoundError:
        st.error("courses1.csv not found. Please ensure the file exists.")
        return

    # Define elective course files
    elective_files = {
        "E1": "E1.csv",
        "E2": "Elective E2 Courses1.csv",
        "E3": "Elective E3 Courses1.csv",
        "E4": "E4.csv",
        "E5": "E5.csv",
        "E6": "Elective E6 Courses1.csv",
        "University Elective": "Elective University Courses1.csv"
    }

    # Load elective courses based on semester and season
    elective_selections = {}
    failed_elective_selections = {}
    passed_elective_selections = {}
    if semester == 4 and current_semester == "Fall":
        try:
            e1_df = pd.read_csv(elective_files["E1"])
            elective_selections["Elective Course E1"] = st.multiselect(
                "Elective Course E1", options=e1_df["CourseCode"].tolist(), key="e1_select"
            )
            failed_elective_selections["Failed Elective Course E1"] = st.multiselect(
                "Failed Elective Course E1", options=e1_df["CourseCode"].tolist(), key="e1_failed_select"
            )
            available_passed_e1 = list(set(e1_df["CourseCode"].tolist()) - set(failed_elective_selections["Failed Elective Course E1"]))
            passed_elective_selections["Passed Elective Course E1"] = st.multiselect(
                "Passed Elective Course E1", options=available_passed_e1, key="e1_passed_select"
            )
        except FileNotFoundError:
            st.error("E1.csv not found. Please ensure the file exists.")
    elif semester == 5 and current_semester == "Spring":
        try:
            e2_df = pd.read_csv(elective_files["E2"])
            elective_selections["Elective Course E2"] = st.multiselect(
                "Elective Course E2", options=e2_df["CourseCode"].tolist(), key="e2_select"
            )
            failed_elective_selections["Failed Elective Course E2"] = st.multiselect(
                "Failed Elective Course E2", options=e2_df["Code"].tolist(), key="e2_failed_select"
            )
            available_passed_e2 = list(set(e2_df["CourseCode"].tolist()) - set(failed_elective_selections["Failed Elective Course E2"]))
            passed_elective_selections["Passed Elective Course E2"] = st.multiselect(
                "Passed Elective Course E2", options=available_passed_e2, key="e2_passed_select"
            )
        except FileNotFoundError:
            st.error("Elective E2 Courses1.csv not found. Please ensure the file exists.")
    elif semester == 5 and current_semester == "Fall":
        try:
            uni_df = pd.read_csv(elective_files["University Elective"])
            elective_selections["Elective University"] = st.multiselect(
                "Elective University", options=uni_df["CourseCode"].tolist(), key="uni_select_5"
            )
            failed_elective_selections["Failed Elective University"] = st.multiselect(
                "Failed Elective University", options=uni_df["CourseCode"].tolist(), key="uni_failed_select_5"
            )
            available_passed_uni = list(set(uni_df["CourseCode"].tolist()) - set(failed_elective_selections["Failed Elective University"]))
            passed_elective_selections["Passed Elective University"] = st.multiselect(
                "Passed Elective University", options=available_passed_uni, key="uni_passed_select_5"
            )
        except FileNotFoundError:
            st.error("Elective University Courses1.csv not found. Please ensure the file exists.")
    elif semester == 7 and current_semester == "Fall":
        try:
            uni_df = pd.read_csv(elective_files["University Elective"])
            elective_selections["Elective University"] = st.multiselect(
                "Elective University", options=uni_df["CourseCode"].tolist(), key="uni_select_7"
            )
            failed_elective_selections["Failed Elective University"] = st.multiselect(
                "Failed Elective University", options=uni_df["CourseCode"].tolist(), key="uni_failed_select_7"
            )
            available_passed_uni = list(set(uni_df["CourseCode"].tolist()) - set(failed_elective_selections["Failed Elective University"]))
            passed_elective_selections["Passed Elective University"] = st.multiselect(
                "Passed Elective University", options=available_passed_uni, key="uni_passed_select_7"
            )
        except FileNotFoundError:
            st.error("Elective University Courses1.csv not found. Please ensure the file exists.")
    elif semester == 9 and current_semester == "Fall":
        try:
            e3_df = pd.read_csv(elective_files["E3"])
            e4_df = pd.read_csv(elective_files["E4"])
            elective_selections["Elective Course E3"] = st.multiselect(
                "Elective Course E3", options=e3_df["CourseCode"].tolist(), key="e3_select"
            )
            failed_elective_selections["Failed Elective Course E3"] = st.multiselect(
                "Failed Elective Course E3", options=e3_df["CourseCode"].tolist(), key="e3_failed_select"
            )
            available_passed_e3 = list(set(e3_df["CourseCode"].tolist()) - set(failed_elective_selections["Failed Elective Course E3"]))
            passed_elective_selections["Passed Elective Course E3"] = st.multiselect(
                "Passed Elective Course E3", options=available_passed_e3, key="e3_passed_select"
            )
            elective_selections["Elective Course E4"] = st.multiselect(
                "Elective Course E4", options=e4_df["CourseCode"].tolist(), key="e4_select"
            )
            failed_elective_selections["Failed Elective Course E4"] = st.multiselect(
                "Failed Elective Course E4", options=e4_df["CourseCode"].tolist(), key="e4_failed_select"
            )
            available_passed_e4 = list(set(e4_df["CourseCode"].tolist()) - set(failed_elective_selections["Failed Elective Course E4"]))
            passed_elective_selections["Passed Elective Course E4"] = st.multiselect(
                "Passed Elective Course E4", options=available_passed_e4, key="e4_passed_select"
            )
        except FileNotFoundError as e:
            st.error(f"{str(e).split(': ')[1]} not found. Please ensure the file exists.")
    elif semester == 10:
        try:
            e4_df = pd.read_csv(elective_files["E4"])
            e6_df = pd.read_csv(elective_files["E6"])
            elective_selections["Elective Course E4"] = st.multiselect(
                "Elective Course E4", options=e4_df["CourseCode"].tolist(), key="e4_select_10"
            )
            failed_elective_selections["Failed Elective Course E4"] = st.multiselect(
                "Failed Elective Course E4", options=e4_df["CourseCode"].tolist(), key="e4_failed_select_10"
            )
            available_passed_e4 = list(set(e4_df["CourseCode"].tolist()) - set(failed_elective_selections["Failed Elective Course E4"]))
            passed_elective_selections["Passed Elective Course E4"] = st.multiselect(
                "Passed Elective Course E4", options=available_passed_e4, key="e4_passed_select_10"
            )
            elective_selections["Elective Course E6"] = st.multiselect(
                "Elective Course E6", options=e6_df["CourseCode"].tolist(), key="e6_select"
            )
            failed_elective_selections["Failed Elective Course E6"] = st.multiselect(
                "Failed Elective Course E6", options=e6_df["CourseCode"].tolist(), key="e6_failed_select"
            )
            available_passed_e6 = list(set(e6_df["CourseCode"].tolist()) - set(failed_elective_selections["Failed Elective Course E6"]))
            passed_elective_selections["Passed Elective Course E6"] = st.multiselect(
                "Passed Elective Course E6", options=available_passed_e6, key="e6_passed_select"
            )
        except FileNotFoundError as e:
            st.error(f"{str(e).split(': ')[1]} not found. Please ensure the file exists.")

    # Load all courses for failed/passed selection
    all_courses = courses["CourseCode"].tolist()
    for cat, file_path in elective_files.items():
        try:
            df = pd.read_csv(file_path)
            all_courses.extend(df["CourseCode"].tolist())
        except FileNotFoundError:
            continue

    # Remove specific E3 courses as per original logic
    all_courses = [code for code in all_courses if code not in ["CSE363", "CSE344"]]

    # Failed and Passed courses selection for core courses
    failed_courses = st.multiselect("Failed Core Courses", options=all_courses, key="failed_core")
    available_passed = list(set(all_courses) - set(failed_courses))
    passed_courses = st.multiselect("Passed Core Courses", options=available_passed, key="passed_core")

    if st.button("Get Recommendations"):
        # Combine selected elective courses and failed elective courses with failed core courses
        selected_electives = []
        failed_electives = []
        passed_electives = []
        for elective_label, selected_codes in elective_selections.items():
            selected_electives.extend(selected_codes)
        for failed_label, failed_codes in failed_elective_selections.items():
            failed_electives.extend(failed_codes)
        for passed_label, passed_codes in passed_elective_selections.items():
            passed_electives.extend(passed_codes)

        # Pass all selected courses to the recommender
        try:
            recs, elective_opts, exps = recommend_courses(
                semester=semester,
                cgpa=cgpa,
                passed_courses=passed_courses + passed_electives,
                failed_courses=failed_courses + failed_electives + selected_electives,
                total_credits=total_credits,
                current_semester=current_semester
            )

            st.subheader("Recommended Courses")
            if recs:
                for i, course in enumerate(recs):
                    st.write(f"{i}: {course}")
            else:
                st.write("[]")

            st.subheader("Explanation")
            if exps:
                for exp in exps:
                    st.write(f"- {exp}")
            else:
                st.write("[]")

            st.subheader("Total Recommended Credit Hours")
            total_hours = sum(courses[courses["CourseCode"] == code]["CreditHours"].iloc[0]
                              for code in recs
                              if code in courses["CourseCode"].values)
            for cat, file_path in elective_files.items():
                try:
                    df = pd.read_csv(file_path)
                    total_hours += sum(df[df["CourseCode"] == code]["Credit Hours"].iloc[0]
                                       for code in recs
                                       if code in df["CourseCode"].values)
                except FileNotFoundError:
                    continue
            st.write(total_hours)

        except ValueError as e:
            st.error(f"Error: {str(e)}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")