import streamlit as st
import re
import src.utils.TermSelector as TermSelector
from src.db.DbHelper import getExistingTerms, getExistingStudents, getStudentInfoById, updateStudentPaymentStatus, getCurrentPayment
import pandas as pd
from src.db.DbHelper import createNewTerm, updateTermDates, getExistingTerms, addClass, updateClassRate, getExistingClasses, getExistingStudents, getClassRate, getNumberOfLessonsInTermForClassByStudent
from src.utils.MiscFunctions import ConvertStringToDateTimeOne

wantedColumns = ["Statement Date","Ref For Account Owner", "Statement Details Info", "Our Ref", "Credit Amount"]
key_data_columns = ["Ref For Account Owner", "Statement Details Info"]

terms = getExistingTerms()
terms = [term[0] for term in terms]
terms = ["Select Term"] + terms

# Check if the term is already in session state
if "selected_term" in st.session_state:
    initial_term = st.session_state["selected_term"]
else:
    initial_term = "Select Term"

termSelector = st.selectbox("Select Term", terms, index=terms.index(initial_term))

# Store the selected term in session state
st.session_state["selected_term"] = termSelector

def expected_payment_for_student(termSelector, student_data):
    return (getClassRate(student_data['class_id']) - student_data['discount']) * getNumberOfLessonsInTermForClassByStudent(student_data['class_id'], termSelector, student_data['id'])

if termSelector != "Select Term":
    bankStatementCsv = st.file_uploader(f'Upload your bank statement in .csv format for {termSelector}', type=['csv'])

    if bankStatementCsv:
        # Store the uploaded file in session state
        df = pd.read_csv(bankStatementCsv)

        # keep rows where credit amount is not 0
        df = df[df["Credit Amount"] != 0]

        st.session_state[f"bank_statement_{termSelector}"] = df

    # Check if the file is already in session state
    if f"bank_statement_{termSelector}" in st.session_state:
        bankStatementCsv_df = st.session_state[f"bank_statement_{termSelector}"]
        
        # display all data
        st.subheader("Raw Data", divider="rainbow")
        st.write(bankStatementCsv_df)

        # Fetch existing students
        existing_students = getExistingStudents()
        student_options = ["Not a student"] + [f"{student['name']} (ID: {student['id']})" for student in existing_students]

        # Used for comparison later, with the semester infromation
        student_parent_invoice_hash = [(student['parent1_name'], student['name'], student['parent2_name']) for student in existing_students] #student['invoice_number'] , student['term_id']

        st.subheader("Possible Student Payments Rows", divider="rainbow")
        # Display the DataFrame with dropdowns next to each row
        for index, row in bankStatementCsv_df.iterrows():

            # content from the wanted columns
            all_content_per_row = row[key_data_columns].values
            
            # remove any $, commas, "Payment" and "Transfer" from the content
            all_content_per_row = [str(content).replace("  ", " ").replace("$", "").replace(",", "").replace("/", "").replace("\\", "").replace("PAYMENT", "").replace("TRANSFER", "").replace("OTHR S", "").replace("via PayNow", "") for content in all_content_per_row]
            all_content_per_row = ", ".join(all_content_per_row)

            # Regex pattern to extract the student name and optional invoice number
            pattern = r":\s*([\w\s]+?)(?:\s+([A-Za-z0-9]+))?$"

            match = re.search(pattern, all_content_per_row)
            if match:
                student_name = match.group(1).strip()  # Extract the student name
                invoice_number = match.group(2) if match.group(2) else "No Invoice Number"  # Optional invoice number

            
            col1, col2, col3 = st.columns([2, 2, 2])
            expected_payment_amount_by_student_for_term = 0
            with col1:
                st.text('Extracted Row Info', help=f"Full Statement Text: {all_content_per_row}")
                if match:
                    st.write(f'Student: **{student_name}**')
                    st.write(f"Invoice Number: **{invoice_number}**")
                else:
                    st.error("Unknown student.")
                st.write(f'Credit Amt: **${row["Credit Amount"]}**')
                st.write(f'Date: **{ConvertStringToDateTimeOne(str(row["Statement Value Date"]))}**')
                
            with col2:
                # Try to see if there is an exact match by studnet_name and the database's student name, get the index if there is
                student_index = None
                print(f"Checking for student name {student_name}")
                for i, student in enumerate(existing_students):
                    print(f"Now printing, seeing if match in student name {student['name']} and {student_name}")
                    if student_name.lower() in student['name'].lower():
                        student_index = i + 1
                        print(f"Match found at index {student_index}!!")
                        break

                print(f'filling with student index {student_index}')
                st.selectbox("Select Student", student_options, key=f"dropdown_{index}", index=student_index)

                student_index = 0
                # display the students ranked by similarity score
                # df_of_student_and_scores = getSimilarityScores(all_content_per_row, )

            with col3:
                #selected student information
                st.write('Selected Student Information:')
                possible_student = st.session_state.get(f'dropdown_{index}')
                if possible_student and possible_student != "Not a student":
                    possible_student_id = int(re.search(r'\(ID: (\d+)\)', possible_student).group(1))
                    student_data = getStudentInfoById(possible_student_id)
                    
                    expected_payment_amount_by_student_for_term = expected_payment_for_student(termSelector, student_data)

                    st.write(f"Name: **{student_data['name']}**")
                    st.write(f"School: **{student_data['school']}**")
                    st.write(f"Graduation Year: **{student_data['grad_year']}**")
                    st.write(f"Handphone: **{student_data['number']}**")
                    st.write(f"Email: **{student_data['email']}**")
                    st.write(f"Parent 1 Name: **{student_data['parent1_name']}**")
                    st.write(f"Parent 2 Name: **{student_data['parent2_name']}**")
                    st.write(f"Expected Payment for current term: **${expected_payment_amount_by_student_for_term:.2f}**")
                    
                else:
                    st.write("N.A.")

            # If credit amount and expected payment differs, then warn the user.
            if round(float(row["Credit Amount"]),2)!= round(expected_payment_amount_by_student_for_term,2) and possible_student and possible_student != "Not a student":
                st.warning("Credit Amount and Expected Amount Paid is different!")
            st.divider()

        # Collect selected students
        selected_students_ids = []
        selected_student_names = []
        selected_amounts = []
        for index, row in bankStatementCsv_df.iterrows():
            selected_student = st.session_state.get(f"dropdown_{index}")
            if selected_student and selected_student != "Not a student":
                student_id = re.search(r'\(ID: (\d+)\)', selected_student).group(1)
                student_name = re.search(r'(.+) \(ID: \d+\)', selected_student).group(1)
                amount_credited = float(row["Credit Amount"])
                selected_student_names.append(student_name)
                selected_students_ids.append(student_id)
                selected_amounts.append(amount_credited)

        st.write(f"Update that the following students have now paid for {termSelector}:")

        # display a table for selected students, with columns: student name + id, paid amount, expected payment for current term
        # Create a DataFrame for display
        summary_data = []
        for i, student_id in enumerate(selected_students_ids):
            student_data = getStudentInfoById(student_id)
            expected_payment = expected_payment_for_student(termSelector, student_data)
            summary_data.append({
                'Student': f"{selected_student_names[i]} (ID: {student_id})",
                'Paid Amount': f"${selected_amounts[i]:.2f}",
                'Expected Payment': f"${expected_payment:.2f}"
            })
        summary_df = pd.DataFrame(summary_data)
        st.table(summary_df)

        # Update the database with the selected students' payment status
        if st.button("Update Payment Status"):
            for i, student_id in enumerate(selected_students_ids):
                # Assuming you have a function to update the payment status
                try:
                    updateStudentPaymentStatus(student_id, termSelector, selected_amounts[i])
                except Exception as e:
                    print("Error updating payment status:", e)
                    st.error(f"Error updating payment status for {selected_student_names[i]}!")

                print("Payment status updated for student ID:", student_id)
            st.success("Payment status updated successfully!")

    st.header("Manual Payment Entry", divider='rainbow')
    
    # Get all active students
    students_df = pd.DataFrame(getExistingStudents())  # You'll need to create this function
    
    # Create student selector
    manual_student_options = [f"{row[1]} (ID: {row[0]})" for _, row in students_df.iterrows()]
    manual_student_options.insert(0, "Select a student")
    manual_selected_student = st.selectbox("Select Student", manual_student_options)
    
    if manual_selected_student and manual_selected_student != "Select a student":
        # Extract student ID and name
        manual_student_id = re.search(r'\(ID: (\d+)\)', manual_selected_student).group(1)
        manual_student_name = re.search(r'(.+) \(ID: \d+\)', manual_selected_student).group(1)
        
        # Get student info and payment details
        manual_student_data = getStudentInfoById(manual_student_id)
        manual_expected_payment = expected_payment_for_student(st.session_state.selectedTerm, manual_student_data)
        manual_current_payment = getCurrentPayment(manual_student_id, st.session_state.selectedTerm)
        
        # Display payment information
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"Current Payment: ${manual_current_payment:.2f}")
        with col2:
            st.info(f"Expected Payment: ${manual_expected_payment:.2f}")
        
        # Manual payment input
        new_payment = st.number_input(
            "Update Payment Amount",
            min_value=0.0,
            max_value=float(manual_expected_payment),
            value=float(manual_current_payment),
            step=0.01,
            format="%.2f"
        )
        
        if st.button("Update Payment"):
            try:
                updateStudentPaymentStatus(
                    student_id=manual_student_id,
                    term_name=st.session_state.selectedTerm,
                    amount_paid=new_payment
                )
                st.success(f"Payment of ${new_payment:.2f} updated for {manual_student_name}!")
            except Exception as e:
                st.error(f"Error recording payment: {e}")
    