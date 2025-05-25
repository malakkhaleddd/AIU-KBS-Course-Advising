import pandas as pd
import os
import csv

# ملفات لكل فئة
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

def add_course(course_code, course_name, description, prerequisites, co_requisites, credit_hours, semester_offered,
               semester, category):
    filename = CSV_FILES.get(category)
    if not filename:
        return "Undefined Category"

    if os.path.exists(filename):
        courses = pd.read_csv(filename)
    else:
        courses = pd.DataFrame()

    if category == "Core":
        new_course = {
            "CourseCode": course_code,
            "CourseName": course_name,
            "Description": description,
            "Prerequisites": prerequisites,
            "CoRequisites": co_requisites,
            "CreditHours": credit_hours,
            "SemesterOffered": semester_offered,
            "Category": category,
            "Semester": semester
        }
    else:
        new_course = {
            "Code": course_code,
            "Course Name": course_name,
            "Description": description,
            "Credit Hours": credit_hours
        }
        if category == "E5" and prerequisites:
            new_course["Prerequisites"] = prerequisites

    courses = pd.concat([courses, pd.DataFrame([new_course])], ignore_index=True)
    courses.to_csv(filename, index=False)

    return f"{course_code} successfully added."

def load_courses_list():
    filename = CSV_FILES.get("Core")
    if not filename or not os.path.exists(filename):
        return []
    df = pd.read_csv(filename)
    return df['CourseCode'].dropna().tolist()

def load_course_details(course_code):
    filename = CSV_FILES.get("Core")
    if not filename or not os.path.exists(filename):
        return None

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('CourseCode') == course_code:
                return {
                    "name": row.get("CourseName", ""),
                    "description": row.get("Description", ""),
                    "prerequisites": row.get("Prerequisites", "").split(',') if row.get("Prerequisites") else [],
                    "co_requisites": row.get("CoRequisites", "").split(',') if row.get("CoRequisites") else [],
                    "credit_hours": int(row.get("CreditHours", 0)),
                    "semester_offered": row.get("SemesterOffered", "Fall"),
                    "semester": int(row.get("Semester", 1)),
                    "category": row.get("Category", "Core")
                }
    return None

def edit_course(course_code, course_name, description, prerequisites, co_requisites, credit_hours, semester_offered,
                semester, category):
    filename = CSV_FILES.get("Core")
    if not filename or not os.path.exists(filename):
        return "No Data Available."

    courses = []
    updated = False

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('CourseCode') == course_code:
                row.update({
                    'CourseName': course_name,
                    'Description': description,
                    'Prerequisites': prerequisites,
                    'CoRequisites': co_requisites,
                    'CreditHours': str(credit_hours),
                    'SemesterOffered': semester_offered,
                    'Semester': str(semester),
                    'Category': category
                })
                updated = True
            courses.append(row)

    if not updated:
        return f"Course {course_code} does not exist."

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['CourseCode', 'CourseName', 'Description', 'Prerequisites', 'CoRequisites', 'CreditHours',
                      'SemesterOffered', 'Semester', 'Category']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(courses)

    return f"{course_code} successfully updated."

def delete_course(course_code):
    filename = CSV_FILES.get("Core")
    if not filename or not os.path.exists(filename):
        return "No Data Available."

    courses = []
    deleted = False

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('CourseCode') == course_code:
                deleted = True
                continue
            courses.append(row)

    if not deleted:
        return f"Course {course_code} does not exist."

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['CourseCode', 'CourseName', 'Description', 'Prerequisites', 'CoRequisites', 'CreditHours',
                      'SemesterOffered', 'Semester', 'Category']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(courses)

    return f"{course_code} successfully deleted."