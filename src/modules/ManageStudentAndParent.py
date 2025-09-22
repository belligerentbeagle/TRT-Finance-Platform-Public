import streamlit as st
from src.utils.GradYearSelector import GradYearSelectionBox
from src.db.DbHelper import createNewStudent, updateStudent, getExistingStudents, getExistingParents, getExistingClasses, createNewParent, updateParent, deleteParent, getExistingSchools
import pandas as pd

# Get all attributes: name, school, grad_year, email, hp number, discount rate, parent1 name, parent1 email, parent1 hp number, parent2 name (optional), parent2 email parent2 name (optional), parent2 hpnumber parent2 name (optional), select class_name
#Edit Exisiting Student -> Change any of the above fields, as well as the term they have attended, the active status, class_name selected


# Function to create input fields for student details
def student_input_fields(student=None, key_prefix=""):
    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input("Enter Student Name", value=student['name'] if student else "", key=f"{key_prefix}_student_name")

        # School options
        school_options = ["Select School"] + getExistingSchools()
        if student and student.get('school'):
            school_index = school_options.index(student['school'])
        else:
            school_index = 0
        school = st.selectbox("Select School", school_options, index=school_index, key=f"{key_prefix}_school")

        grad_year = st.number_input("Select Graduation Year (from A levels)", value=int(student['grad_year']) if student else 2030, key=f"{key_prefix}_student_grad_year")
        email = st.text_input("Enter Email (compulsory)", value=student['email'] if student else "", key=f"{key_prefix}_email")
        hp_number = st.text_input("Enter HP Number (compulsory)", value=student['number'] if student else "", key=f"{key_prefix}_hp_number")

    with col2:
        discount_rate = st.number_input("Enter Discount Rate ($/lesson)", value=float(student['discount']) if student else 0.0, step=0.1, key=f"{key_prefix}_discount_rate")

        ## TODO: Fix parent thing. Show the parent name but select and edit by parent id
        # Parent 1
        existing_parents = getExistingParents()
        parent1_options = ["Add New Parent"] + [f"{parent['name']} (ID: {parent['id']})" for parent in existing_parents]
        parent1_default = f"{student['parent1_name']} (ID: {student['parent1_id']})" if student and student.get('parent1_name') else "Add New Parent"
        parent1_selection = st.selectbox("Select Parent 1", parent1_options, index=parent1_options.index(parent1_default), key=f"{key_prefix}_parent1_selection")
        if parent1_selection == "Add New Parent":
            parent1_name = st.text_input("Enter Parent 1 Name", key=f"{key_prefix}_parent1_name")
            parent1_number = st.text_input("Enter Parent 1 Number", key=f"{key_prefix}_parent1_number")
            parent1_email = st.text_input("Enter Parent 1 Email", key=f"{key_prefix}_parent1_email")
            parent1_id = None
        else:
            parent1_id = int(parent1_selection.split(" (ID: ")[1][:-1])
            parent1_name = None
            parent1_number = None
            parent1_email = None

        # Parent 2
        parent2_options = ["Add New Parent"] + [f"{parent['name']} (ID: {parent['id']})" for parent in existing_parents]
        parent2_default = f"{student['parent2_name']} (ID: {student['parent2_id']})" if student and student.get('parent2_name') else "Add New Parent"
        parent2_selection = st.selectbox("Select Parent 2 (Optional)", parent2_options, index=parent2_options.index(parent2_default), key=f"{key_prefix}_parent2_selection")
        if parent2_selection == "Add New Parent":
            parent2_name = st.text_input("Enter Parent 2 Name", key=f"{key_prefix}_parent2_name")
            parent2_number = st.text_input("Enter Parent 2 Number", key=f"{key_prefix}_parent2_number")
            parent2_email = st.text_input("Enter Parent 2 Email", key=f"{key_prefix}_parent2_email")
            parent2_id = None
        else:
            parent2_id = int(parent2_selection.split(" (ID: ")[1][:-1])
            parent2_name = None
            parent2_number = None
            parent2_email = None

    with col3:
        available_classes = getExistingClasses()
        class_options = ["No Class (ID: NA)"] + [f"{class_['name']} (ID: {class_['cid']})" for class_ in available_classes]   
        class_default = f"{student['class_name']} (ID: {student['class_id']})" if student and student.get('class_name') else class_options[0]
        class_id = st.selectbox("Select Class", class_options, index=class_options.index(class_default), key=f"{key_prefix}_class_id").split(" (ID: ")[1][:-1]
        active = st.checkbox("Active", value=student['active'] if student else True, key=f"{key_prefix}_active")
    if email == "":
        st.warning("Please enter an email address!")
        return None
    if hp_number == "":
        st.warning("Please enter a HP number!")
        return None
    return {
        "name": name,
        "school": school,
        "grad_year": grad_year,
        "email": email,
        "number": hp_number,
        "class_id": int(class_id) if class_id != "NA" else 0, # 0 is for a student not being assigned a class
        "discount": discount_rate,
        "parent1_id": parent1_id if parent1_selection != "Add New Parent" else None,
        "parent1_name": parent1_name,
        "parent1_number": parent1_number,
        "parent1_email": parent1_email,
        "parent2_id": parent2_id if parent2_selection != "Add New Parent" else None,
        "parent2_name": parent2_name,
        "parent2_number": parent2_number,
        "parent2_email": parent2_email,
        "active": active
    }

# Fetch existing students
existing_students = getExistingStudents()

# Header
st.header("Add/Edit Students", divider="rainbow")

# Display all existing students
st.caption("Existing Students")
df = pd.DataFrame(existing_students)
st.write(df)

st.divider()

# Dropdown to select an existing student to edit
student_options = ["Create New Student"] + [f"{student['name']} (ID: {student['id']})" for student in existing_students]
selected_student = st.selectbox("Select a student to edit:", student_options, key="select_student")

if selected_student == "Create New Student":
    # Inputs for creating a new student
    student_details = student_input_fields(key_prefix="new_student")
    
    if st.button("Create Student"):
        createNewStudent(**student_details)
else:
    # Extract the selected student details
    student_id = int(selected_student.split(" (ID: ")[1][:-1])
    student = next(student for student in existing_students if student['id'] == student_id)
    
    # Inputs for editing an existing student
    student_details = student_input_fields(student, key_prefix=f"edit_student_{student_id}")
    
    if st.button("Update Student"):
        if student_details is None:
            st.error("Please fill in the compulsory fields!")
        else:  
            updateStudent(student_id, **student_details)
    
    # if st.button("Delete Student"):
    #     deleteStudent(student_id)


# Manage Parent Details

# Function to create input fields for parent details

def parent_input_fields(parent=None, key_prefix=""):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Enter Parent Name", value=parent['name'] if parent else "", key=f"{key_prefix}_parent_name")
        email = st.text_input("Enter Email", value=parent['email'] if parent else "", key=f"{key_prefix}_email")
        hp_number = st.text_input("Enter HP Number", value=parent['hp_number'] if parent else "", key=f"{key_prefix}_hp_number")

    return {
        "name": name,
        "email": email,
        "hp_number": hp_number,
    }


# Header
st.header("Add/Edit Parents", divider="rainbow")

# Display all existing parents
st.caption("Existing Parents")
df = pd.DataFrame(getExistingParents())
st.write(df)

st.divider()

# Fetch existing parents
existing_parents = getExistingParents()

# Dropdown to select an existing parent to edit
parent_options = ["Create New Parent"] + [f"{parent['name']} (ID: {parent['id']})" for parent in existing_parents]

selected_parent = st.selectbox("Select a parent to edit:", parent_options, key="select_parent")

if selected_parent == "Create New Parent":
    # Inputs for creating a new parent
    parent_details = parent_input_fields(key_prefix="new_parent")
    
    if st.button("Create Parent"):
        createNewParent(**parent_details)

else:
    # Extract the selected parent details
    parent_id = int(selected_parent.split(" (ID: ")[1][:-1])
    parent = next(parent for parent in existing_parents if parent['id'] == parent_id)
    
    # Inputs for editing an existing parent
    parent_details = parent_input_fields(parent, key_prefix=f"edit_parent_{parent_id}")
    
    if st.button("Update Parent"):
        updateParent(parent_id, **parent_details)
    
    if st.button("Delete Parent"):
        deleteParent(parent_id)