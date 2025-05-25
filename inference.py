import pandas as pd
from experta import *

# Load course data
try:
    courses_df = pd.read_csv("courses1.csv")
except FileNotFoundError:
    raise FileNotFoundError("Could not find courses1.csv. Ensure the file exists in the project directory.")

# Validate required columns
required_columns = ["CourseCode", "CourseName", "Category", "Prerequisites", "CoRequisites", "CreditHours", "SemesterOffered", "Semester"]
if not all(col in courses_df.columns for col in required_columns):
    raise ValueError(f"courses1.csv is missing required columns. Expected: {required_columns}")

class Student(Fact):
    """Student information"""
    semester = Field(int, mandatory=True)
    cgpa = Field(float, mandatory=True)
    passed = Field(list, mandatory=True)
    failed = Field(list, mandatory=True)
    credits = Field(int, mandatory=True)
    current_semester = Field(str, mandatory=True)  # "Fall", "Spring", or "Summer"

class Course(Fact):
    """Course information"""
    code = Field(str, mandatory=True)
    name = Field(str, mandatory=True)
    category = Field(str, mandatory=True)
    prerequisites = Field(list, mandatory=True)
    co_requisites = Field(list, mandatory=True)
    credit_hours = Field(float, mandatory=True)
    semester_offered = Field(str, mandatory=True)
    semester = Field(int, mandatory=True)

class Recommendation(Fact):
    """Recommended courses"""
    course_code = Field(str, mandatory=True)
    course_name = Field(str, mandatory=True)
    reason = Field(str, mandatory=True)

class Explanation(Fact):
    """Explanations for recommendations or exclusions"""
    course_code = Field(str, mandatory=True)
    explanation = Field(str, mandatory=True)

class CourseRecommender(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.recommendations = []
        self.explanations = []
        self.credit_limit = 0
        self.total_credits = 0
        self.passed = []
        self.failed = []
        self.elective_options = {}

    @DefFacts()
    def load_courses(self):
        """Load courses as Facts"""
        for _, row in courses_df.iterrows():
            try:
                yield Course(
                    code=row["CourseCode"],
                    name=row["CourseName"],
                    category=row["Category"],
                    prerequisites=str(row["Prerequisites"]).split(",") if pd.notna(row["Prerequisites"]) else [],
                    co_requisites=str(row["CoRequisites"]).split(",") if pd.notna(row["CoRequisites"]) else [],
                    credit_hours=float(row["CreditHours"]) if pd.notna(row["CreditHours"]) else 0.0,
                    semester_offered=row["SemesterOffered"],
                    semester=int(row["Semester"]) if pd.notna(row["Semester"]) else 1
                )
            except (ValueError, TypeError) as e:
                self.explanations.append(f"Skipped course {row['CourseCode']}: Invalid data ({str(e)}).")

    @Rule(AS.student << Student(semester=MATCH.semester, cgpa=MATCH.cgpa, current_semester=MATCH.current_semester),
          salience=100)
    def set_credit_limit(self, student, semester, cgpa, current_semester):
        """Set credit limit based on CGPA and semester"""
        if current_semester == "Summer":
            self.credit_limit = 9
            self.explanations.append("Credit limit set to 9 for Summer semester.")
        elif cgpa < 1.67 and semester >= 2:
            self.credit_limit = 12
            self.explanations.append(f"Credit limit set to 12 due to CGPA {cgpa} < 1.67 after 2 semesters.")
        elif cgpa < 2.00 and semester >= 3:
            self.credit_limit = 12
            self.explanations.append(f"Credit limit set to 12 due to CGPA {cgpa} < 2.00 after 3 semesters.")
        elif cgpa < 2.00:
            self.credit_limit = 12
            self.explanations.append(f"Credit limit set to 12 due to CGPA {cgpa} < 2.00.")
        elif 2.00 <= cgpa < 3.00:
            self.credit_limit = 20
            self.explanations.append(f"Credit limit set to 20 due to CGPA {cgpa} between 2.00 and 2.99.")
        else:
            self.credit_limit = 22
            self.explanations.append(f"Credit limit set to 22 due to CGPA {cgpa} >= 3.00.")
        self.declare(Student(**dict(student)))

    @Rule(AS.student << Student(passed=MATCH.passed, failed=MATCH.failed, current_semester=MATCH.current_semester),
          AS.course << Course(code=MATCH.code, semester_offered=MATCH.sem_off, credit_hours=MATCH.credits),
          TEST(lambda code, failed: code in failed),
          TEST(lambda code, passed: code not in passed),
          salience=90)
    def recommend_failed(self, course, code, credits, current_semester):
        """Recommend failed courses for retaking"""
        if code not in courses_df["CourseCode"].values:
            self.explanations.append(f"Not recommended {code}: Course not found in course database.")
            self.declare(Explanation(course_code=code, explanation="Course not found in course database."))
            return
        if code not in self.recommendations:
            if course["semester_offered"] not in ["Both", current_semester]:
                self.explanations.append(f"Not recommended {code}: Course not offered in {current_semester}.")
                self.declare(Explanation(course_code=code, explanation=f"Course not offered in {current_semester}."))
                return
            if self.total_credits + credits <= self.credit_limit or credits == 0:
                self.recommendations.insert(0, code)
                self.total_credits += credits
                self.explanations.append(f"Prioritized {code}: Retake due to previous failure.")
                self.declare(Recommendation(course_code=code, course_name=course["name"], reason="Retake due to previous failure"))
            else:
                self.explanations.append(f"Not recommended {code}: Exceeds credit limit of {self.credit_limit} (current: {self.total_credits}).")
                self.declare(Explanation(course_code=code, explanation=f"Exceeds credit limit of {self.credit_limit} (current: {self.total_credits})."))
        else:
            self.explanations.append(f"Not recommended {code}: Already recommended.")
            self.declare(Explanation(course_code=code, explanation="Already recommended."))

    @Rule(AS.student << Student(semester=MATCH.semester, passed=MATCH.passed, current_semester=MATCH.current_semester),
          AS.course << Course(code=MATCH.code, credit_hours=0, semester_offered=MATCH.sem_off, category="University Requirement", semester=MATCH.course_sem),
          TEST(lambda semester, course_sem, code, passed: semester <= 2 and course_sem <= 2 and code not in passed and code in ["CSE011", "LAN022"]),
          TEST(lambda sem_off, current_semester: sem_off in ["Both", current_semester]))
    def recommend_non_credit(self, course, code):
        """Recommend non-credit mandatory courses (CSE011, LAN022) in Semesters 1-2"""
        if code not in self.recommendations:
            self.recommendations.append(code)
            self.explanations.append(f"Recommended {code}: Mandatory non-credit course for first level.")
            self.declare(Recommendation(course_code=code, course_name=course["name"], reason="Mandatory non-credit course"))

    @Rule(AS.student << Student(semester=MATCH.semester, cgpa=MATCH.cgpa, passed=MATCH.passed, credits=MATCH.total_credits, current_semester=MATCH.current_semester),
          AS.course << Course(code=MATCH.code, category=MATCH.cat, prerequisites=MATCH.prereqs, co_requisites=MATCH.co_reqs, credit_hours=MATCH.credits, semester_offered=MATCH.sem_off, semester=MATCH.course_sem),
          TEST(lambda cat, code: cat == "Core" or (cat == "University Requirement" and code not in ["CSE011", "LAN022"])),
          NOT(Recommendation(course_code=MATCH.code)),
          TEST(lambda code, passed: code not in passed),
          TEST(lambda sem_off, current_semester: sem_off in ["Both", current_semester]),
          TEST(lambda semester, course_sem: semester >= course_sem or abs(semester - course_sem) <= 1))
    def recommend_mandatory(self, student, course, code, prereqs, co_reqs, credits, cgpa, total_credits, cat):
        """Recommend core and university requirement courses"""
        is_senior = student["semester"] >= 9 or total_credits >= 125
        if course["prerequisites"] == ["SENIOR STANDING"] and not is_senior:
            self.explanations.append(f"Not recommended {code}: Requires senior standing (Semester >= 9 or 125+ credits).")
            self.declare(Explanation(course_code=code, explanation="Requires senior standing (Semester >= 9 or 125+ credits)."))
            return

        prereqs_list = list(prereqs)  # Convert frozenlist to list
        co_reqs_list = list(co_reqs)
        if all(prereq.strip() in student["passed"] for prereq in prereqs_list if prereq.strip()):
            if all(co_req.strip() in student["passed"] or co_req.strip() in self.recommendations for co_req in co_reqs_list if co_req.strip()):
                if prereqs_list and cgpa < 2.00 and cat != "University Requirement":
                    self.explanations.append(f"Not recommended {code}: CGPA {cgpa} below 2.00 for advanced course.")
                    self.declare(Explanation(course_code=code, explanation=f"CGPA {cgpa} below 2.00 for advanced course."))
                    return
                if self.total_credits + credits <= self.credit_limit or credits == 0:
                    self.recommendations.append(code)
                    self.total_credits += credits
                    self.explanations.append(f"Recommended {code}: {cat} course, prerequisites {prereqs_list} met, CGPA {cgpa} sufficient.")
                    self.declare(Recommendation(course_code=code, course_name=course["name"], reason=f"{cat} course, prerequisites met"))
                else:
                    self.explanations.append(f"Not recommended {code}: Exceeds credit limit of {self.credit_limit} (current: {self.total_credits}).")
                    self.declare(Explanation(course_code=code, explanation=f"Exceeds credit limit of {self.credit_limit} (current: {self.total_credits})."))
            else:
                self.explanations.append(f"Not recommended {code}: Missing co-requisites {co_reqs_list}.")
                self.declare(Explanation(course_code=code, explanation=f"Missing co-requisites {co_reqs_list}."))
        else:
            self.explanations.append(f"Not recommended {code}: Missing prerequisites {prereqs_list}.")
            self.declare(Explanation(course_code=code, explanation=f"Missing prerequisites {prereqs_list}."))

    @Rule(AS.student << Student(semester=MATCH.semester, passed=MATCH.passed, current_semester=MATCH.current_semester),
          AS.course << Course(code=MATCH.code, category=MATCH.cat, credit_hours=MATCH.credits, semester_offered=MATCH.sem_off, semester=MATCH.course_sem),
          TEST(lambda cat: cat.startswith("E") or cat == "University Elective"),
          NOT(Recommendation(course_code=MATCH.code)),
          TEST(lambda code, passed: code not in passed),
          TEST(lambda sem_off, current_semester: sem_off in ["Both", current_semester]),
          TEST(lambda semester, course_sem: semester >= course_sem or abs(semester - course_sem) <= 1))
    def recommend_elective_placeholder(self, course, code, cat, credits):
        """Recommend elective placeholders"""
        if self.total_credits + credits <= self.credit_limit:
            self.recommendations.append(code)
            self.total_credits += credits
            self.explanations.append(f"Recommended {code}: {cat} course required in Semester {course['semester']}.")
            self.declare(Recommendation(course_code=code, course_name=course["name"], reason=f"{cat} course required"))
            eligible = [row["CourseCode"] for _, row in courses_df.iterrows()
                        if row["Category"] == cat
                        and all(prereq.strip() in self.passed for prereq in str(row["Prerequisites"]).split(",") if prereq.strip())
                        and float(row["CreditHours"]) + self.total_credits - credits <= self.credit_limit]
            if eligible:
                self.explanations.append(f"Eligible courses for {code} ({cat}): {eligible}.")
                self.declare(Explanation(course_code=code, explanation=f"Eligible courses: {eligible}."))
            else:
                self.explanations.append(f"No eligible courses for {code} ({cat}) due to prerequisites or credit limit.")
                self.declare(Explanation(course_code=code, explanation="No eligible courses due to prerequisites or credit limit."))

    def get_recommendations(self):
        return self.recommendations, self.elective_options, self.explanations

def recommend_courses(semester, cgpa, passed_courses, failed_courses, total_credits, current_semester):
    if current_semester not in ["Fall", "Spring", "Summer"]:
        raise ValueError("Current semester must be 'Fall', 'Spring', or 'Summer'.")
    engine = CourseRecommender()
    engine.reset()
    engine.declare(Student(
        semester=semester,
        cgpa=cgpa,
        passed=passed_courses,
        failed=failed_courses,
        credits=total_credits,
        current_semester=current_semester
    ))
    engine.run()
    return engine.get_recommendations()

if __name__ == "__main__":
    recs, elective_opts, exps = recommend_courses(
        semester=2,
        cgpa=3.7,
        passed_courses=["MEC011", "PHY212", "CSE014", "UC11XX", "MAT123", "MAT112", "MAT131", "CSE315"],
        failed_courses=["CSE015"],
        total_credits=30,
        current_semester="Fall"
    )
    print("Recommendations:", recs)
    print("Elective Options:", elective_opts)
    print("Explanations:")
    for exp in exps:
        print(f"- {exp}")