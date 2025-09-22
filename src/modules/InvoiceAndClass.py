import streamlit as st
import pandas as pd
from src.db.DbHelper import createNewTerm, updateTermDates, getExistingTerms, addClass, updateClassRate, getExistingClasses, getExistingStudents, getTermId, getNumberOfLessonsInTermForClassByStudent
import os
import csv
from datetime import datetime
from src.db.DbHelper import getStudentsInTerm, getClassRate, getTermDates
from src.invoice.ClassInvoiceGen import InvoiceGenerator

def generate_invoices_for_students(selected_term, students):
    # Get students in term
    term_dates = getTermDates(selected_term)
    term_number = getTermId(selected_term)
    year = selected_term.split(" ")[0]
    
    # Prepare CSV data
    csv_data = []
    invoice_date = datetime.now().strftime("%d/%m/%Y")
    
    # Header rows
    headers = ["Name","Invoice Number","Invoice Date","Grad Year","Tuition Class","Term",
               "Start Date","End Date","No. of lessons","Lesson Rate","Total Lesson Fees",
               "Discount Rate","Total discounted","Payment Refund","Payment Refund Rate",
               "Refund Quantity","Total refunded","Trial Lesson","Trial Lesson Total","Grand Total","Year"]
    
    format_row = ["Name Here","YYYYTTNNN","DD/MM/YYYY","","","0","DD/MM/YYYY","DD/MM/YYYY",
                 "Sample","","Sample","","Sample","Reason","0.00","1","0.00","Date","0.00","Sample","2024"]
    
    csv_data.append(headers)
    csv_data.append(format_row)
    
    # Generate data for each student
    for student in students:
        lesson_rate = getClassRate(student['class_id'])
        num_lessons = getNumberOfLessonsInTermForClassByStudent(student['class_id'], selected_term, student['id'])
        total_lessons = float(lesson_rate) * float(num_lessons)
        discount = student.get('discount', 0)
        total_discounted = float(discount) * float(num_lessons)
        grand_total = total_lessons - total_discounted
        
        invoice_number = get_invoice_number(term_number, year, student)
        
        student_row = [
            student['name'],
            invoice_number,
            invoice_date,
            student['grad_year'],
            student['class_name'],
            term_number,
            term_dates['start_date'],
            term_dates['end_date'],
            str(num_lessons),
            f"{lesson_rate:.2f}",
            f"{total_lessons:.2f}",
            f"{discount:.2f}",
            f"{total_discounted:.2f}",
            "",  # refund reason
            "0.00",  # refund rate
            "",  # refund quantity
            "0.00",  # total refunded
            "",  # trial lesson
            "0.00",  # trial fee
            f"{grand_total:.2f}",
            year,
            student['id']
        ]
        csv_data.append(student_row)
    
    # Write to CSV
    csv_path = f"private/term_{term_number}_invoices_data.csv"
    os.makedirs("private", exist_ok=True)
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
    
    # Generate PDFs
    generator = InvoiceGenerator()
    pdfs = generator.generate_from_csv(csv_path)
    
    return pdfs

def get_invoice_number(term_number, year, student):
    return f"{year}{term_number:02d}{student['id']:03d}"


def get_generated_invoices(term_name):
    """Get list of student IDs with generated invoices"""
    term_id = getTermId(term_name)
    invoice_dir = f"invoices/term_{term_id}"
    generated_ids = set()
    
    if os.path.exists(invoice_dir):
        for filename in os.listdir(invoice_dir):
            if filename.endswith('.pdf'):
                try:
                    student_id = filename.split('_')[0]
                    generated_ids.add(student_id)
                except:
                    continue
    return generated_ids

def display_invoice_status(selected_term):
    """Display invoice generation status for all students"""
    students = getStudentsInTerm(selected_term)

    print("Students", students)
    generated_ids = get_generated_invoices(selected_term)
    
   # Create DataFrame for display
    status_data = []
    for i, student in students.iterrows():
        status_data.append({
            'Student Name': student['name'],
            'Class': student['class_name'],
            'Status': "✓" if str(student['id']) in generated_ids else "×",
            'Generated': str(student['id']) in generated_ids
        })
    
    df = pd.DataFrame(status_data)

    # Style the DataFrame
    def color_status(val):
        color = '#98FB98' if val == "✓" else '#FFB6C1'
        return f'background-color: {color}'
    
    if len(df) != 0:
        styled_df = df.drop('Generated', axis=1).style.applymap(
            color_status,
            subset=['Status']
        )
        
        # Display with Streamlit
        st.write("### Invoice Generation Status")
        st.dataframe(
            styled_df,
            column_config={
                "Student Name": st.column_config.TextColumn("Student Name", width="large"),
                "Class": st.column_config.TextColumn("Class", width="medium"),
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="✓ = Generated, × = Not Generated",
                    width="small"
                )
            },
            hide_index=True,
            use_container_width=True
        )
    
    # Add generate/regenerate buttons
    if st.button("Generate Missing Invoices"):
        missing_students = [
            {
                'id': student['id'],
                'name': student['name'],
                'class_id': student['class_id'],
                'grad_year': student['grad_year'],
                'class_name': student['class_name'],
                'discount': student['discount']
            }
            for _, student in students.iterrows() 
            if str(student['id']) not in generated_ids
        ]
        if missing_students:
            with st.spinner("Generating missing invoices..."):
                pdfs = generate_invoices_for_students(selected_term, missing_students)
                if pdfs:
                    st.success("Generated missing invoices! Saved to invoices folder, no need to download.")
                    for pdf in pdfs:
                        with open(pdf, "rb") as f:
                            st.download_button(
                                label=f"Download {os.path.basename(pdf)}",
                                data=f,
                                file_name=os.path.basename(pdf),
                                mime="application/pdf"
                            )
        else:
            st.info("No missing invoices to generate.")

    # if st.button("Regenerate All Invoices"):
    #     pdfs = generate_invoices_for_students(selected_term, students)
    #     if pdfs:
    #         st.success("Regenerated all invoices!")
    #         for pdf in pdfs:
    #             with open(pdf, "rb") as f:
    #                 st.download_button(
    #                     label=f"Download {os.path.basename(pdf)}",
    #                     data=f,
    #                     file_name=os.path.basename(pdf),
    #                     mime="application/pdf"
    #                 )
    #     else:
    #         st.info("No invoices to regenerate.")


## Generate Invoices for a term for students
st.header("Invoice Generation for term", divider="rainbow")

# Fetch existing terms
existing_terms = getExistingTerms()

# Dropdown to select an existing term to edit
term_options = [f"{name} | Start: {start_date} | End: {end_date}" for name, start_date, end_date in existing_terms]
selected_term = st.selectbox("Select a term to edit:", term_options, index=len(term_options) - 1).split(" | Start:")[0]

# Update existing code
if selected_term:
    display_invoice_status(selected_term)

