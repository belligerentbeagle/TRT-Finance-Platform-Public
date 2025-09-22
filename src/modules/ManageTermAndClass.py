import streamlit as st
import pandas as pd
from src.db.DbHelper import createNewTerm, updateTermDates, getExistingTerms, addClass, updateClassRate, getExistingClasses, getExistingStudents, getClassesInTerm, addClassToTerm, removeClassFromTerm, getStudentInClassTerm, addStudentToClass, removeStudentFromClass, setNumberOfLessons, getNumberOfLessons, setNumberOfLessonsForStudent


## Allow user to create or edit term:
st.header("Manage Terms:", divider="rainbow")

# Fetch existing terms
existing_terms = getExistingTerms()

# Dropdown to select an existing term to edit
term_options = ["Create New Term"] + [f"{name} | Start: {start_date} | End: {end_date}" for name, start_date, end_date in existing_terms]
selected_term = st.selectbox("Select a term to edit:", term_options).split(" | Start:")[0]

if selected_term == "Create New Term":
    # Inputs for creating a new term
    term_name = st.text_input("Term Name: ", placeholder="e.g. Y24T3 for Year 2024, Term 3.")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    if st.button("Create Term"):
        if term_name == "":
            st.error("Please enter a term name!")
        else:
            is_successful = createNewTerm(term_name, start_date, end_date)
            if is_successful:
                st.success(f"Term {term_name} created successfully with dates from {start_date} to {end_date}!")
            else:
                st.error(f"Failed to create term {term_name}. Please try again.")
else:
    # Extract the selected term details
    term_name = selected_term
    term_name, default_start_date, default_end_date = next((name, start_date, end_date) for name, start_date, end_date in existing_terms if name == term_name)
    start_date = st.date_input("Start Date", value=pd.to_datetime(default_start_date))
    end_date = st.date_input("End Date", value=pd.to_datetime(default_end_date))
    
    if st.button("Update Term Dates"):
        is_successful = updateTermDates(term_name, start_date, end_date)
        if is_successful:
            st.success(f"Term {term_name} updated successfully with new dates from {start_date} to {end_date}!")
        else:
            st.error(f"Failed to update term {term_name}. Please try again.")




## Allow user to create or edit class:
st.header("Manage Classes:", divider="rainbow")

# Fetch existing classes
available_classes = getExistingClasses()

# Dropdown to select an existing class to edit
class_options = ["Create New Class"] + [f"{avail_class['name']} | Rate: ${avail_class['rate']} | (ID: {avail_class['cid']})" for avail_class in available_classes]
selected_classes = st.selectbox("Select a class to edit:", class_options).split(" | Rate")[0]

if selected_classes == "Create New Class":
    # Inputs for creating a new class
    class_name = st.text_input("Class Name: ", placeholder="e.g. S2 Saturday 7:00pm (RI)")
    rate = st.number_input("Class Rate: ($)", step=0.01)
    
    if st.button("Create Class"):
        if class_name == "":
            st.error("Please enter a class name!")
        else:
            is_successful = addClass(class_name, rate)
            if is_successful:
                st.success(f"Class {class_name} created successfully with rate of ${rate}!")
            else:
                st.error(f"Failed to create class {class_name}. Please try again.")
else:
    # Inputs for editing an existing class
    class_name = selected_classes
    new_rate = st.number_input("New Class Rate: ($)", step=1)
    
    if st.button("Update Class Rate"):
        is_successful = updateClassRate(class_name, new_rate)
        if is_successful:
            st.success(f"Class {class_name} updated successfully with new rate of ${new_rate}!")
        else:
            st.error(f"Failed to update class {class_name}. Please try again.")



## Allow user to select classes in a selected term:
st.header("Assign Classes to Term:", divider="rainbow")

# Dropdown to select a term
term_options = [f"{name} | Start: {start_date} | End: {end_date}" for name, start_date, end_date in existing_terms]
selected_term = st.selectbox("Select a term:", term_options).split(" | Start:")[0]

col1, col2 = st.columns(2)

with col1:
    # Display Available classes
    st.caption("Available Classes")

    # Fetch availbe classes
    available_classes = getExistingClasses()
    df = pd.DataFrame(available_classes)

    # Display all Available classes
    st.write(df[['name', 'rate']])


with col2:
    # Show classes currently in term
    st.caption(f"Classes in Selected Term {selected_term}")
    classes_in_term = (getClassesInTerm(selected_term))
    st.write(classes_in_term[['name', 'rate']])

# Dropdown to select a class to assign to the selected term
class_options = [f"{avail_class['name']} (ID: {avail_class['cid']})" for avail_class in available_classes]

selected_classes = st.multiselect("Select the following class(es) to assign/remove to the term:", class_options)

col1, col2 = st.columns(2)

with col1:
    if st.button("**Assign** Class(es) to Term", use_container_width=True):
        for class_name in selected_classes:
            class_id = int(class_name.split(" (ID: ")[1][:-1])
            print("Adding class to term:", class_id)
            is_successful = addClassToTerm(selected_term, class_id)
            if is_successful:
                st.success(f"Class {class_name} assigned to term {selected_term} successfully!")
            else:
                st.error(f"Failed to assign class {class_name} to term {selected_term}. Please try again.")

with col2:
    if st.button("**Remove** Class(es) from Term", use_container_width=True):
        for class_name in selected_classes:
            class_id = int(class_name.split(" (ID: ")[1][:-1])
            is_successful = removeClassFromTerm(selected_term, class_id)
            if is_successful:
                st.success(f"Class {class_name} removed from term {selected_term} successfully!")
            else:
                st.error(f"Failed to remove class {class_name} from term {selected_term}.")



# Manage students in the class this term.
st.header(f"Students in classes this term {selected_term}:", divider="rainbow")

if len(classes_in_term) == 0:
    st.warning(f"No classes in term {selected_term}. Please assign classes to the term first.")
    st.stop()

class_options = [f"{class_[1]} (ID: {class_[0]})" for _, class_ in classes_in_term.iterrows()]
selected_class_to_edit_students = st.selectbox("Select a class to view students:", class_options)
class_id = int(selected_class_to_edit_students.split(" (ID: ")[1][:-1])

# Edit the number of lessons in the term
current_num_lessons = getNumberOfLessons(class_id, selected_term)
num_lessons_set = st.number_input("Number of Lessons in Term:", min_value=1, step=1, value=current_num_lessons)

col1, col2 = st.columns(2)

with col1:
    st.warning("Note that setting new number of lessons will change the custom number of lessons for students to this new updated number of lessons!")
with col2:
    if st.button("Set Number of Lessons"):
        is_successful = setNumberOfLessons(class_id, selected_term, num_lessons_set)
        if is_successful:
            st.success(f"Number of lessons for class {selected_class_to_edit_students} in term {selected_term} set to {num_lessons_set} successfully!")
        else:
            st.error(f"Failed to set number of lessons for class {selected_class_to_edit_students} in term {selected_term}. Please try again.")


# Fetch students in the selected class for this term
students_in_class = getStudentInClassTerm(class_id, selected_term)

# Display students in the selected class
st.write(students_in_class[['name', 'school', 'num_of_lessons_attending']])

# Fetch all existing students
all_students = getExistingStudents()

# Dropdown to select students to assign/remove to/from the selected class
student_options = [f"{student['name']} (ID: {student['id']})" for student in all_students]
selected_students = st.multiselect("Select the following student(s) to assign/remove to the class:", student_options)

col1, col2 = st.columns(2)

with col1:
    if st.button("**Assign** Student(s) to Class", use_container_width=True):
        for student in selected_students:
            student_id = int(student.split(" (ID: ")[1][:-1])
            is_successful = addStudentToClass(student_id, class_id, selected_term)
            if is_successful:
                st.success(f"Student {student} assigned to class {selected_class_to_edit_students} successfully!")
            else:
                st.error(f"Failed to assign student {student} to class {selected_class_to_edit_students}. Please try again.")

with col2:
    if st.button("**Remove** Student(s) from Class", use_container_width=True):
        for student in selected_students:
            student_id = int(student.split(" (ID: ")[1][:-1])
            is_successful = removeStudentFromClass(student_id, class_id, selected_term)
            if is_successful:
                st.success(f"Student {student} removed from class {selected_class_to_edit_students} successfully!")
            else:
                st.error(f"Failed to remove student {student} from class {selected_class_to_edit_students}. Please try again.")


st.divider()

# Allow to customize number of lessons attending for a student in a classterm.
selected_student_for_custom_lesson_number = st.selectbox(f"Select the following student(s) to modify number of lessons for term {selected_term}:", student_options)
num_lessons_set_for_student = int(st.number_input(f"Number of Lessons in Term for {selected_student_for_custom_lesson_number}:", step=1))
student_id = int(selected_student_for_custom_lesson_number.split(" (ID: ")[1][:-1])

if st.button("Confirm Set Number of Lessons"):
    is_successful = setNumberOfLessonsForStudent(class_id, selected_term, student_id, num_lessons_set_for_student)
    if is_successful:
        st.success(f"Number of lessons for {selected_student_for_custom_lesson_number} in term {selected_term} set to {num_lessons_set_for_student} successfully!")
    else:
        st.error(f"Failed to set number of lessons for {selected_student_for_custom_lesson_number} in term {selected_term}. Please try again.")


# Add a refund for a student this term in the selected class



# Add a free trial function so that a student's free trial class will be added if they do end up signing up for a class.
