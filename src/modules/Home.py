import streamlit as st
import plotly.express as px
import src.gmail.EmailSender as EmailSender
import src.db.DbHelper as DbHelper
from src.modules.InvoiceAndClass import (
    generate_invoices_for_students, 
    get_invoice_number, 
    get_generated_invoices
)

studentdata = '/Users/ethanyuxin/Documents/World/TRT-Finance-Platform/private/sample_csd.csv'
import pandas as pd
import time
import glob
import os

st.title("TRT Finance Platform")
st.info("This is a tool to manage payments, invoices and track payments for The Rationale Thinking Learning Centre.")

terms = DbHelper.getExistingTerms()
terms = [term[0] for term in terms]
termSelection = st.sidebar.selectbox("Select Term", terms, index=len(terms) - 1)

## Store in Session State
st.session_state.selectedTerm = termSelection


def showNotPaidStudents(df):
    print(df)
    students = df[df['Paid'] == False][['ID', 'Name', 'School', 'Amount Paid']]

    # show amount paid in 2 decimal places
    students['Amount Paid'] = students['Amount Paid'].map('${:,.2f}'.format)

    if len(students) != 0:
        st.table(students)
    else:
        st.success("No unpaid students!")

st.header(f"{termSelection} Term Collection Progress", divider='rainbow')

def showPaidStudents(df):
    students = df[df['Paid'] == True][['ID', 'Name','School', 'Amount Paid', 'Invoice Amount']]

    students['Amount Paid'] = students['Amount Paid'].map('${:,.2f}'.format)
    students['Invoice Amount'] = students['Invoice Amount'].map('${:,.2f}'.format)


    # Add a column to check if the amount is fully paid. 
    students['Fully Paid'] = students['Amount Paid'] == students['Invoice Amount']
    

    if len(students) != 0:
        st.table(students)
    else:
        st.error("No paid students!")

## Display students and their paid/unpaid status for the selected term
def displayProgressBar(percent_paid):
    st.markdown("""
        <style>
            .stProgress > div > div > div > div {
            background-color: green;
        }
        div[data-testid="stProgress"] > div > div > div {
            height: 20px; 
        }
        </style>
        """, unsafe_allow_html=True)

    progress = st.progress(percent_paid)

def progressBarSection(paymentsForTerm):
    if len(paymentsForTerm) != 0:
        percent_paid = paymentsForTerm['Paid'].sum()/len(paymentsForTerm)
        col1, col2 = st.columns([1, 9])
        with col1:
            percent_paid_formatted = f"{percent_paid*100:.2f}"
            st.write(f"{percent_paid_formatted}%")  
        with col2:
            displayProgressBar(percent_paid)

def customizeEmailMessageSection():
    st.subheader("Select/Edit Email Message", divider='rainbow', help="All emails will have students' corresponding invoice attached.")
    # Pull the most recent email subject and body from the database
    messages_available = DbHelper.getStoredEmailMessage()
    email_options = ["Create new message"] + [f"{msg['date_created']} - {msg['subject']}" for msg in messages_available]
    selected_email = st.selectbox("Select Email Message", email_options, index=len(email_options) - 1)

    if selected_email == "Create new message":
        email_subject = st.text_input("Subject", help="You may use <student_name> and <invoice_number> as placeholders for student name and invoice number.")
        email_body = st.text_area("Body", help="You may use <student_name> and <invoice_number> as placeholders for student name and invoice number.")
        if st.button("Save Email Message"):
            DbHelper.updateEmailMessage(email_subject, email_body, date_created=time.strftime("%Y-%m-%d %H:%M:%S"))
            st.success("New email message created and saved! Please refresh to see the updated list.")
    else:
        selected_msg = next(msg for msg in messages_available if f"{msg['date_created']} - {msg['subject']}" == selected_email)
        email_subject = selected_msg['subject']
        email_body = selected_msg['body']
        st.markdown(f"**Subject:** {email_subject}")
        st.markdown(f"**Body:**\n\n{email_body}")
    
    st.session_state.email_subject = email_subject
    st.session_state.email_body = email_body

def get_invoice_path(term_selection, term_id, student_info):
    """Find invoice using student ID and name pattern"""
    invoice_dir = os.path.join("invoices", f"term_{term_id}")
    
    if not os.path.exists(invoice_dir):
        return False
    
    # Pattern: student_id_student_name_*.pdf
    pattern = os.path.join(invoice_dir, f"{student_info['id']}_{student_info['name']}_{term_selection}_Term_{term_id}_Invoice_*.pdf")
    matching_files = glob.glob(pattern)
    
    # Return first match or False if none found
    print("matching: ", matching_files)
    return matching_files[0] if matching_files else False


# Information Display
def showPaidUnpaidStudents(paymentsForTerm):
    col1, col2 = st.columns([1, 1])
    with col2:
        st.subheader("Paid students", divider='rainbow')
        showPaidStudents(paymentsForTerm)

    with col1:
        st.subheader("Unpaid students", divider='rainbow')
        showNotPaidStudents(paymentsForTerm)
        
        with st.expander("Send Reminder to unpaid students"):
            st.warning("Dangerous action! Please check carefully before proceeding.")

            if st.button("Send Reminder to unpaid students"):
                term_id = DbHelper.getTermId(termSelection)
                year = termSelection.split(" ")[0]

                print("Send Reminder to unpaid students button clicked!")

                # if email is not selected, warn user
                if st.session_state.email_subject == '' or st.session_state.email_body == '':
                    st.warning("Please select an email message to send reminders to unpaid students!")
                    return

                # Get the list of unpaid students
                unpaid_students = paymentsForTerm[paymentsForTerm['Paid'] == False] 
                if False: #TODO, remove False after testing is complete and replace with #unpaid_students.empty:
                    st.write("No unpaid students to send reminders to!")
                else:
                    # Send reminder to each student
                    with st.spinner("Sending reminders to unpaid students..."):
                        for index, student in unpaid_students.iterrows():
                            # Get student details
                            student_info = DbHelper.getStudentInfoById(student['ID'])
                            student_id = student['ID']
                            student_name = student_info['name']    
                            student_email = student_info['email']
                            parent1_email = student_info['parent1_email']
                            parent2_email = student_info['parent2_email']
                            
                            # don't send email twice if both parents share the same email
                            if parent1_email == parent2_email:
                                email_list = [student_email, parent1_email]
                            else:
                                email_list = [student_email, parent1_email, parent2_email]

                            # Generate invoice number and PDF file path
                            invoice_num = get_invoice_number(term_id, year, student_info)
                            
                            invoice_pdf_file_path = get_invoice_path(termSelection, term_id, student_info)
                            if invoice_pdf_file_path is False:
                                st.error(f"Please generate invoice for student: {student_name}, id: {student_id} first!")
                                continue
                                                        
                            email_subject_copy = st.session_state.email_subject
                            subject = email_subject_copy.replace("<student_name>", student_name).replace("<invoice_number>", str(invoice_num))

                            email_body_copy = st.session_state.email_body
                            content = email_body_copy.replace("<student_name>", student_name).replace("<invoice_number>", str(invoice_num))

                            for email in email_list:
                                if email is None or email == "":
                                    continue
                                try:
                                    EmailSender.send_message(
                                            recipientEmail=email,
                                            subject=subject,
                                            body=content,
                                            pdf_file_path=invoice_pdf_file_path,
                                        )
                                    st.info(f"Email sent to {email} for student {student_name}")
                                except Exception as e:
                                    st.write(f"Failed to send email to {email} for student {student_name}: {e}")

                    st.success("Reminders sent to students and respective parents successfully!")

    

def showExpectedTermRevenue(paymentsForTerm):
    # get all student ids of students who are in the selected term
    student_ids = paymentsForTerm['ID'].tolist()

    total_expected_revenue = DbHelper.getExpectedRevenueForGivenTerm(termSelection)
    total_paid_revenue = paymentsForTerm[paymentsForTerm['Paid'] == True]['Amount Paid'].sum()
    total_unpaid_revenue = total_expected_revenue - total_paid_revenue
    st.write(f"Total expected revenue: ${total_expected_revenue:.2f}")
    st.write(f"Total paid revenue: ${total_paid_revenue:.2f}")
    st.write(f"Total unpaid revenue: ${total_unpaid_revenue:.2f}")

    if total_unpaid_revenue > 0:
        st.warning("There are unpaid students. Please send reminders to them!")

    if total_unpaid_revenue == 0:
        st.success("All students have paid their fees for this term!")

    # Display a chart showing the revenue
    revenue_data = {
        'Category': ['Expected', 'Paid', 'Unpaid'],
        'Amount': [total_expected_revenue, total_paid_revenue, total_unpaid_revenue]
    }
    revenue_df = pd.DataFrame(revenue_data)

    fig = px.bar(revenue_df, x='Category', y='Amount',
                 title='Revenue Breakdown',
                 labels={'Amount': 'Amount ($)', 'Category': ''})
    
    # Configure the layout
    fig.update_layout(
        yaxis=dict(
            rangemode='nonnegative',  # Forces y-axis to start from 0
            fixedrange=True  # Prevents y-axis zooming
        ),
        xaxis=dict(
            fixedrange=True  # Prevents x-axis zooming
        )
    )
    
    # Format y-axis ticks to show dollar amounts
    fig.update_traces(
        texttemplate='$%{y:.2f}',
        textposition='outside'
    )
    
    st.plotly_chart(fig, use_container_width=True)

if termSelection:
    paymentsForTerm = DbHelper.getTermData(termSelection)
    if paymentsForTerm is not None:
        showExpectedTermRevenue(paymentsForTerm)
        progressBarSection(paymentsForTerm)
        showPaidUnpaidStudents(paymentsForTerm)
        customizeEmailMessageSection()






