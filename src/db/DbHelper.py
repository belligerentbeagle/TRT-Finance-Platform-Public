import pandas as pd
import sqlite3
import streamlit as st

database_location = "src/db/DB.db"

def connect(database_loc=database_location):
    try:
        conn = sqlite3.connect(database_loc)
        return conn
    except Exception as e:
        print(f'Error connecting to database: {e}')
        st.write(e)
        return None

def getAvailableGradYears():
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT DISTINCT grad_year FROM students
            """
        )

        grad_years = cur.fetchall()
        conn.close()

        grad_years = [grad_year[0] for grad_year in grad_years]
        print(f'Query success: \n{grad_years}')
        return grad_years if grad_years is not None else []
        
    except Exception as e:
        print(f"Error getting available grad years: {e}")
        st.write(e)
        return None

def getTermData(term_name):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute("""
                SELECT s.name as name, st.paid as paid, s.id as id, st.amount_paid as amount_paid, 
                       s.school as school, st.invoice_id as invoice_id, 
                       (cr.rate - s.discount) * ct.num_lessons as invoice_amount
                FROM students s
                JOIN student_class_term st ON st.student_id = s.id
                JOIN class_term ct ON ct.ct_id = st.ct_id
                JOIN term t ON t.term_id = ct.term_id
                JOIN class_rate cr ON ct.class_id = cr.cid
                WHERE t.term_name = ?
                """, (term_name,)
        )

        data = cur.fetchall()
        conn.close()

        if len(data) == 0: #return empty dataframe
            return pd.DataFrame(columns=['Name', 'Paid', 'ID', 'Amount Paid', 'School', 'Invoice ID', 'Invoice Amount'])
 
        df = pd.DataFrame(data)
        cols = {0: 'Name', 1: 'Paid', 2: 'ID', 3: 'Amount Paid', 
               4: 'School', 5: 'Invoice ID', 6: 'Invoice Amount'}
        df = df.rename(columns=cols)
        print(df)
        df['Paid'] = df['Paid'].astype(bool)
        df['Amount Paid'] = df['Amount Paid'].apply(lambda x: round(x, 2))
        df['Invoice Amount'] = df['Invoice Amount'].apply(lambda x: round(x, 2))

        return df
    
    except Exception as e:
        print(f"Error retrieving information: {e}")
        st.write(e)
        return None


    
def updateTermDates(term_name, start_date, end_date):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE term
            SET start_date = ?, end_date = ?
            WHERE term_name = ?
            """, (start_date, end_date, term_name)
        )

        conn.commit()
        conn.close()

        print(f"Term {term_name} updated successfully!")
        return True
    except Exception as e:
        print(f"Error updating term dates: {e}")
        st.write(e)
        return False


def getExistingTerms():
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
        """
            SELECT t.term_name, t.start_date, t.end_date FROM term t
        """
        )
       
        data = cur.fetchall()
        conn.close()

        return data if data is not None else []
    
    except Exception as e:
        print(f"Error getting available terms: {e}")
        st.write(e)
        return None
    
def createNewTerm(term_name, start_date, end_date):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO term (term_name, start_date, end_date)
            VALUES (?, ?, ?)
            """, (term_name, start_date, end_date)
        )

        conn.commit()
        conn.close()

        print(f"Term {term_name} created successfully!")
        return True
    except Exception as e:
        print(f"Error creating term: {e}")
        st.write(e)
        return False

def getExistingClasses(): # Returns a list
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
        """
            SELECT c.cid, c.name, c.rate FROM class_rate c
        """
        )
       
        rows = cur.fetchall()        
        conn.close()

        # Convert rows to list of dictionaries
        classes = [
            {"cid": row[0], "name": row[1], "rate": row[2]}
            for row in rows
        ]

        return classes if classes is not None else []

    except Exception as e:
        print(f"Error getting available classes: {e}")
        st.write(e)
        return None

def addClass(class_name, rate):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        # Check if class name already exists
        cur.execute("SELECT COUNT(*) FROM class_rate WHERE name = ?", (class_name,))
        if cur.fetchone()[0] > 0:
            print(f"Class {class_name} already exists!")
            st.error(f"Class {class_name} already exists! Please select it from the dropdown and edit the rate instead.")
            return False

        # Insert new class
        cur.execute(
            """
            INSERT INTO class_rate (name, rate)
            VALUES (?, ?)
            """, (class_name, rate)
        )

        conn.commit()
        conn.close()

        print(f"Class {class_name} added successfully!")
        return True
    
    except Exception as e:
        print(f"Error adding class: {e}")
        st.write(e)
        return False

def updateClassRate(class_name, new_rate):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        # Check if class name exists
        cur.execute("SELECT COUNT(*) FROM class_rate WHERE name = ?", (class_name,))
        if cur.fetchone()[0] == 0:
            print(f"Class {class_name} does not exist!")
            st.error(f"Class {class_name} does not exist! Please create it first.")
            return False

        # Update class rate
        cur.execute(
            """
            UPDATE class_rate
            SET rate = ?
            WHERE name = ?
            """, (new_rate, class_name)
        )

        conn.commit()
        conn.close()

        print(f"Class {class_name} updated successfully!")
        return True
    except Exception as e:
        print(f"Error updating class rate: {e}")
        st.write(e)
        return False


def createTerm(term_name, start_date, end_date):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO term (start_date, end_date, term_name)
            VALUES (?, ?, ?)
            """, (start_date, end_date, term_name)
        )

        conn.commit()
        conn.close()

        print(f"Term {term_name} created successfully!")
        return True
    
    except Exception as e:
        print(f"Error creating term: {e}")
        st.write(e)
        return False


def createNewStudent(name, school, grad_year, email, number, class_id, discount, parent1_id, parent1_name, parent1_number, parent1_email, parent2_id, parent2_name, parent2_number, parent2_email, active):
    try:
        conn = connect(database_location)
        if conn is None:
            return False 
        cur = conn.cursor()


        print(f'Original Parent 1 ID: {parent1_id}, Parent 2 ID: {parent2_id}')
        # Insert mandatory first parent if needed
        if parent1_name != "":
            success_p1, parent1_info = createNewParent(parent1_name, parent1_number, parent1_email)
            parent1_id = parent1_info['id'] if success_p1 else parent1_id 

        # Insert optional second parent if present
        if parent2_name != "":
            print(parent2_name)
            success_p2, parent2_info = createNewParent(parent2_name, parent2_number, parent2_email)
            parent2_id = parent2_info['id'] if success_p2 else parent2_id


        # Insert new student
        print(f'New Parent 1 ID: {parent1_id}, Parent 2 ID: {parent2_id}')
        cur.execute(
            """
            INSERT INTO students (name, school, grad_year, email, number, class_id, discount, parent1, parent2, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, school, grad_year, email, number, class_id, discount, parent1_id, parent2_id, active)
        )
        print(f'class_id: {class_id}')

        conn.commit()
        conn.close()

        print(f"Student {name} created successfully!")
        st.success(f"Student {name} created successfully!")
        return True

    except Exception as e:  
        print(f"Error creating student: {e}")
        if "UNIQUE constraint failed: students.number" in str(e):
            st.error(f"Student with number {number} already exists!")
            return False
        st.write(e)
        return False

def createNewParent(name, hp_number, email):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            INSERT OR IGNORE INTO parents (name, hp_number, email)
            VALUES (?, ?, ?)
            """,
            (name, hp_number, email)
        )

        conn.commit()
        conn.close()

        if name is None:
            return False, None
            
        print(f"Parent {name} created successfully!")
        st.success(f"Parent {name} created successfully!")

        return True, {"id": cur.lastrowid, "name": name, "hp_number": hp_number, "email": email}
    except Exception as e:
        print(f"Error creating parent: {e}")
        st.write(e)
        return False, None

def updateStudent(student_id, name, school, grad_year, email, number, class_id, discount, parent1_id, parent1_name, parent1_number, parent1_email, parent2_id, parent2_name, parent2_number, parent2_email, active):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        print(f'Original Parent 1 ID: {parent1_id}, Parent 2 ID: {parent2_id}')
        # Insert mandatory first parent if needed
        if parent1_name != "":
            success_p1, parent1_info = createNewParent(parent1_name, parent1_number, parent1_email)
            parent1_id = parent1_info['id'] if success_p1 else parent1_id 

        # Insert optional second parent if present
        if parent2_name != "":
            print(parent2_name)
            success_p2, parent2_info = createNewParent(parent2_name, parent2_number, parent2_email)
            parent2_id = parent2_info['id'] if success_p2 else parent2_id

        # Update student
        print(f'New Parent 1 ID: {parent1_id}, Parent 2 ID: {parent2_id}')
        cur.execute(
            """
            UPDATE students
            SET name = ?, school = ?, grad_year = ?, email = ?, number = ?, class_id = ?, discount = ?, parent1 = ?, parent2 = ?, active = ?
            WHERE id = ?
            """,
            (name, school, grad_year, email, number, class_id, discount, parent1_id, parent2_id, active, student_id)
        )

        conn.commit()
        conn.close()

        print(f"Student {name} updated successfully!")
        st.success(f"Student {name} updated successfully!")
        return True
    except Exception as e:
        print(f"Error updating student: {e}")
        if "UNIQUE constraint failed: students.number" in str(e):
            st.error(f"Student with number {number} already exists!")
            return False
        st.write(e)
        return False

# def deleteStudent():
#     pass

def getExistingStudents():
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT s.id, s.name, s.school, s.grad_year, s.email, s.number, s.discount, s.active,
            p1.id as parent1_id, p1.name as parent1_name, p1.email as parent1_email, p1.hp_number as parent1_hp_number, 
            p2.id as parent2_id, p2.name as parent2_name, p2.email as parent2_email, p2.hp_number as parent2_hp_number, 
            c.name as class_name, c.cid as class_id
            FROM students s
            LEFT JOIN parents p1 ON s.parent1 = p1.id
            LEFT JOIN parents p2 ON s.parent2 = p2.id
            LEFT JOIN class_rate c ON s.class_id = c.cid
            """
        )

        rows = cur.fetchall()
        conn.close()

        # Convert rows to list of dictionaries
        students = [
            {
                "id": row[0],
                "name": row[1],
                "school": row[2],
                "grad_year": row[3],
                "email": row[4],
                "number": row[5],
                "discount": row[6],
                "active": row[7],
                "parent1_id": row[8],
                "parent1_name": row[9],
                "parent1_email": row[10],
                "parent1_hp_number": row[11],
                "parent2_id": row[12],
                "parent2_name": row[13],
                "parent2_email": row[14],
                "parent2_hp_number": row[15],
                "class_name": row[16],
                "class_id": row[17]
            }
            for row in rows
        ]

        return students if students is not None else []
        
    except Exception as e:
        print(f"Error getting existing students: {e}")
        st.write(e)
        return None
    

def getExistingParents():
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, name, email, hp_number FROM parents
            """
        )

        rows = cur.fetchall()
        conn.close()

        # Convert rows to list of dictionaries
        parents = [
            {"id": row[0], "name": row[1], "email": row[2], "hp_number": row[3]}
            for row in rows
        ]

        return parents if parents is not None else []
        
    except Exception as e:
        print(f"Error getting existing parents: {e}")
        st.write(e)
        return None

def updateParent(id, name, email, hp_number):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE parents
            SET name = ?, email = ?, hp_number = ?
            WHERE id = ?
            """, (name, email, hp_number, id)
        )

        conn.commit()
        conn.close()

        print(f"Parent {name} updated successfully!")
        st.success(f"Parent {name} updated successfully!")
        return True
    except Exception as e:
        print(f"Error updating parent: {e}")
        st.write(e)
        return False


def deleteParent(id):
    pass


# def construct_comparison_text(termid):
#     try:
#         conn = connect(database_location)
#         if conn is None:
#             return False

#         cur = conn.cursor()

#         cur.execute(
#             """
#             SELECT p2.name, p1.name, s.name, st.invoice_id
#             FROM students s
#             JOIN student_class_term st ON st.student_id = s.id
#             JOIN parents p2 ON p2.id = s.parent2
#             JOIN parents p1 ON p1.id = s.parent1
#             WHERE st.term_id = ?
#             """, (termid,)
#         )

#         data = cur.fetchall()

#         conn.close()

#         return data if data is not None else []

#     except Exception as e:
#         print(f"Error getting comparison text: {e}")
#         st.write(e)
#         return None


def getStudentByInvoice(invoice_number):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT s.id, s.name, p1.id as parent1_id, p1.name as parent1_name, p1.hp_number as parent1_hp_number, 
            p2.id as parent2_id, p2.name as parent2_name, p2.hp_number as parent2_hp_number, 
            FROM students s
            LEFT JOIN parents p1 ON s.parent1 = p1.id
            LEFT JOIN parents p2 ON s.parent2 = p2.id
            LEFT JOIN student_class_term st ON s.id = st.student_id
            WHERE s.invoice_number = ?
            """, (invoice_number,)
        )

        row = cur.fetchone()
        conn.close()

        if row is None:
            return None

        student = {
            "id": row[0],
            "name": row[1],
            "parent1_id": row[2],
            "parent1_name": row[3],
            "parent1_hp_number": row[4],
            "parent2_id": row[5],
            "parent2_name": row[6],
            "parent2_hp_number": row[7]
        }

        return student
    except Exception as e:
        print(f"Error getting student by invoice number: {e}")
        st.write(e)
        return None

def getStudentInfoById(id):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT s.id, s.name, s.school, s.grad_year, s.email, s.number, s.discount, s.active,
            p1.id as parent1_id, p1.name as parent1_name, p1.email as parent1_email, p1.hp_number as parent1_hp_number, 
            p2.id as parent2_id, p2.name as parent2_name, p2.email as parent2_email, p2.hp_number as parent2_hp_number, 
            c.name as class_name, c.cid as class_id
            FROM students s
            LEFT JOIN parents p1 ON s.parent1 = p1.id
            LEFT JOIN parents p2 ON s.parent2 = p2.id
            LEFT JOIN class_rate c ON s.class_id = c.cid
            WHERE s.id = ?
            """, (id,)
        )

        row = cur.fetchone()
        conn.close()

        if row is None:
            return None

        student = {
            "id": row[0],
            "name": row[1],
            "school": row[2],
            "grad_year": row[3],
            "email": row[4],
            "number": row[5],
            "discount": row[6],
            "active": row[7],
            "parent1_id": row[8],
            "parent1_name": row[9],
            "parent1_email": row[10],
            "parent1_hp_number": row[11],
            "parent2_id": row[12],
            "parent2_name": row[13],
            "parent2_email": row[14],
            "parent2_hp_number": row[15],
            "class_name": row[16],
            "class_id": 0 if (row[17] == '' or row[17] is None) else int(row[17])
        }

        return student
    except Exception as e:
        print(f"Error getting student by ID: {e}")
        st.write(e)
        return None

def getStoredEmailMessage():
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, email_subject, email_body, date_created FROM email_messages
            """
        )

        rows = cur.fetchall()
        conn.close()

        # Convert rows to list of dictionaries
        messages = [
            {"id": row[0], "subject": row[1], "body": row[2], "date_created": row[3]}
            for row in rows
        ]

        return messages if messages is not None else []


    except Exception as e:
        print(f"Error getting stored email message: {e}")
        st.write(e)
        return None, None

def updateEmailMessage(subject, body, date_created):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO email_messages (email_subject, email_body, date_created)
            VALUES (?, ?, ?)
            """, (subject, body, date_created)
        )

        conn.commit()
        conn.close()

        print(f"Email message updated successfully!")
        return True
    except Exception as e:
        print(f"Error updating email message: {e}")
        st.write(e)
        return False


def updateStudentPaymentStatus(student_id, term_name, amount_paid):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        # Retrieve the class_id for the student
        cur.execute(
            """
            SELECT class_id FROM students
            WHERE id = ?
            """, (student_id,)
        )
        class_id = cur.fetchone()[0]

        print(f"Class ID found: {class_id}")

        # Update the student_class_term table using ct_id
        cur.execute(
            """
            UPDATE student_class_term
            SET paid = ?, amount_paid = ?
            WHERE student_id = ? AND ct_id = (
                SELECT ct_id FROM class_term
                WHERE term_id = (SELECT term_id FROM term WHERE term_name = ?) AND class_id = ?
            )
            """, (True, amount_paid, student_id, term_name, class_id)
        )

        conn.commit()
        conn.close()

        print(f"Student {student_id} paid status updated successfully!")
        return True
    except Exception as e:
        print(f"Error updating student paid status: {e}")
        st.write(e)
        return False

def getClassesInTerm(term_name):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT c.cid, c.name, c.rate
            FROM class_rate c
            JOIN class_term ct ON c.cid = ct.class_id
            JOIN term t ON ct.term_id = t.term_id
            WHERE t.term_name = ?
            """, (term_name,)
        )   

        data = cur.fetchall()
        conn.close()
        
        # return a dataframe with columns: cid, name, rate
        df = pd.DataFrame(data, columns=['cid', 'name', 'rate'])

        return df if df is not None else []

    except Exception as e:
        print(f"Error getting classes in term: {e}")
        st.write(e)
        return None

def addClassToTerm(term_name, class_id):
    try:
        print(f'From DbHelper.py: term_name: {term_name}, class_id: {class_id}')
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        # Check if term_name exists in the term table
        cur.execute("SELECT term_id FROM term WHERE term_name = ?", (term_name,))
        term_id = cur.fetchone()
        if term_id is None:
            print(f"Term '{term_name}' does not exist.")
            return False

        # Check if class_id exists in the class_rate table
        cur.execute("SELECT cid FROM class_rate WHERE cid = ?", (class_id,))
        class_exists = cur.fetchone()
        if class_exists is None:
            print(f"Class ID '{class_id}' does not exist.")
            return False
        
        # Add the class to the term
        cur.execute(
            """
            INSERT INTO class_term (term_id, class_id)
            VALUES (?, ?)
            """, (term_id[0], class_id)
        )

        # Get the class_term id (ct_id)
        cur.execute(
            """
            SELECT ct_id FROM class_term
            WHERE term_id = (SELECT term_id FROM term WHERE term_name = ?) AND class_id = ?
            """, (term_name, class_id)
        )
        ct_id = cur.fetchone()[0]

        # Insert records into student_class_term for all active students taking that class
        cur.execute(
            """
            INSERT INTO student_class_term (student_id, ct_id)
            SELECT id, ? FROM students s WHERE s.class_id = ? AND s.active = 1
            """, (ct_id, class_id)
        )

        conn.commit()
        conn.close()

        print(f"Class {class_id} added to term {term_name} successfully!")
        return True
    
    except Exception as e:
        print(f"Error adding class to term: {e}")
        st.write(e)
        return False

def removeClassFromTerm(term_name, class_id):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        # Get the class_term id (ct_id)
        cur.execute(
            """
            SELECT ct_id FROM class_term
            WHERE term_id = (SELECT term_id FROM term WHERE term_name = ?) AND class_id = ?
            """, (term_name, class_id)
        )

        ct_id = cur.fetchone()[0]

        print(f"Term name: {term_name}, Class ID: {class_id}")
        print(f"CT_ID: {cur.fetchone()}")
        if ct_id is None:
            print(f"Class {class_id} does not exist in term {term_name}.")
            return False


        # Delete records from student_class_term for that term with ct_id = ct_id
        cur.execute(
            """
            DELETE FROM student_class_term WHERE ct_id = ?
            """, (ct_id,)
        )

        # Remove the class from the term
        cur.execute(
            """
            DELETE FROM class_term
            WHERE term_id = (SELECT term_id FROM term WHERE term_name = ?) AND class_id = ?
            """, (term_name, class_id)
        )

        conn.commit()
        conn.close()

        print(f"Class {class_id} removed from term {term_name} successfully!")
        return True
    except Exception as e:
        print(f"Error removing class from term: {e}")
        st.write(e)
        return False

def getStudentsInTerm(term_name):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT s.id, s.name, s.school, s.grad_year, s.email, s.number, s.discount, s.active,
            p1.id as parent1_id, p1.name as parent1_name, p1.email as parent1_email, p1.hp_number as parent1_hp_number, 
            p2.id as parent2_id, p2.name as parent2_name, p2.email as parent2_email, p2.hp_number as parent2_hp_number, 
            c.name as class_name, c.cid as class_id
            FROM students s
            LEFT JOIN parents p1 ON s.parent1 = p1.id
            LEFT JOIN parents p2 ON s.parent2 = p2.id
            LEFT JOIN class_rate c ON s.class_id = c.cid
            LEFT JOIN student_class_term st ON s.id = st.student_id
            WHERE st.ct_id IN (SELECT ct_id FROM class_term WHERE term_id = (SELECT term_id FROM term WHERE term_name = ?))
            """, (term_name,)
        )

        rows = cur.fetchall()

        # Convert rows to dataframe with columns: id, name, school, grad_year, email, number, discount, active, parent1_id, parent1_name, parent1_email, parent1_hp_number, parent2_id, parent2_name, parent2_email, parent2_hp_number, class_name, class_id
        df = pd.DataFrame(rows, columns=['id', 'name', 'school', 'grad_year', 'email', 'number', 'discount', 'active', 'parent1_id', 'parent1_name', 'parent1_email', 'parent1_hp_number', 'parent2_id', 'parent2_name', 'parent2_email', 'parent2_hp_number', 'class_name', 'class_id'])

        return df if df is not None else []
    except Exception as e:
        print(f"Error getting students in term: {e}")
        st.write(e)
        return None

def getStudentInClassTerm(class_id, term_name):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT s.id, s.name, s.school, s.grad_year, s.email, s.number, s.discount, s.active, st.num_less_attdng as num_of_lessons_attending,
            p1.id as parent1_id, p1.name as parent1_name, p1.email as parent1_email, p1.hp_number as parent1_hp_number, 
            p2.id as parent2_id, p2.name as parent2_name, p2.email as parent2_email, p2.hp_number as parent2_hp_number, 
            c.name as class_name, c.cid as class_id
            FROM students s
            LEFT JOIN parents p1 ON s.parent1 = p1.id
            LEFT JOIN parents p2 ON s.parent2 = p2.id
            LEFT JOIN class_rate c ON s.class_id = c.cid
            LEFT JOIN student_class_term st ON s.id = st.student_id
            WHERE s.class_id = ? AND st.ct_id = (SELECT ct_id FROM class_term WHERE term_id = (SELECT term_id FROM term WHERE term_name = ?) AND class_id = ?)
            """, (class_id, term_name, class_id)
        )

        rows = cur.fetchall()

        # Convert rows to dataframe with columns: id, name, school, grad_year, email, number, discount, active, parent1_id, parent1_name, parent1_email, parent1_hp_number, parent2_id, parent2_name, parent2_email, parent2_hp_number, class_name, class_id
        df = pd.DataFrame(rows, columns=['id', 'name', 'school', 'grad_year', 'email', 'number', 'discount', 'active', 'num_of_lessons_attending', 'parent1_id', 'parent1_name', 'parent1_email', 'parent1_hp_number', 'parent2_id', 'parent2_name', 'parent2_email', 'parent2_hp_number', 'class_name', 'class_id'])

        return df if df is not None else []
    
    except Exception as e:

        print(f"Error getting students in class term: {e}")
        st.write(e)
        return None

def addStudentToClass(student_id, class_id, term_name):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        # Update student's class_id
        cur.execute(
            """
            UPDATE students
            SET class_id = ?
            WHERE id = ?
            """, (class_id, student_id)
        )

        # Add the record to student_class_term as well
        cur.execute(
            """
            INSERT INTO student_class_term (student_id, ct_id)
            VALUES (?, (SELECT ct_id FROM class_term WHERE term_id = (SELECT term_id FROM term WHERE term_name = ?) AND class_id = ?))
            """, (student_id, term_name, class_id)
        )

        conn.commit()
        conn.close()

        print(f"Student {student_id} added to class {class_id} successfully!")
        return True

    except Exception as e:
        print(f"Error adding student to class: {e}")
        st.write(e)
        return False

def removeStudentFromClass(student_id, class_id, term_name):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        # Update student's class_id to None
        cur.execute(
            """
            UPDATE students
            SET class_id = NULL
            WHERE id = ?
            """, (student_id,)
        )

        # Delete the record from student_class_term
        cur.execute(
            """
            DELETE FROM student_class_term
            WHERE student_id = ? AND ct_id = (SELECT ct_id FROM class_term WHERE term_id = (SELECT term_id FROM term WHERE term_name = ?) AND class_id = ?)
            """, (student_id, term_name, class_id)
        )

        conn.commit()
        conn.close()

        print(f"Student {student_id} deleted from class {class_id} successfully!")

        return True
    
    except Exception as e:
        print(f"Error deleting student from class: {e}")
        st.write(e)
        return False
    

def getClassRate(class_id):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT rate FROM class_rate WHERE cid = ?
            """, (class_id,)
        )

        result = cur.fetchone()
        conn.close()
        if result is None:
            return 0 
        rate = result[0]

        return rate if rate is not None else 0 
    except Exception as e:
        print(f"Error getting class rate: {e}")
        st.write(e)
        return 0 

def getNumberOfLessonsInTermForClass(class_id, term_name):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT num_lessons FROM class_term WHERE class_id = ? AND term_id = (SELECT term_id FROM term WHERE term_name = ?)
            """, (class_id, term_name)
        )

        answer = cur.fetchone()
        conn.close()

        if answer is None: # there is no class that the student is taking in this semester
            return 0

        number_of_lessons = answer[0]

        return number_of_lessons
    
    except Exception as e:
        print(f"error getting number of lessons: {e}")
        st.write(e)
        return 0

def getNumberOfLessonsInTermForClassByStudent(class_id, term_name, student_id):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT num_less_attdng FROM student_class_term WHERE student_id = ? AND ct_id = (SELECT ct_id FROM class_term WHERE class_id = ? AND term_id = (SELECT term_id FROM term WHERE term_name = ?))
            """, (student_id, class_id, term_name)
        )

        answer = cur.fetchone()
        conn.close()

        if answer is None: # there is no class that the student is taking in this semester
            return 0

        number_of_lessons = answer[0]

        return number_of_lessons
    
    except Exception as e:
        print(f"error getting number of lessons: {e}")
        st.write(e)
        return 0
    
def setNumberOfLessons(class_id, term_name, num_lessons):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE class_term 
            SET num_lessons = ?
            WHERE class_id = ? AND term_id = (SELECT term_id FROM term WHERE term_name = ?)
            """, (num_lessons, class_id, term_name)
        )

        ## update student_class_term too
        cur.execute(
            """
            UPDATE student_class_term
            SET num_less_attdng = ?
            WHERE ct_id = (SELECT ct_id FROM class_term WHERE class_id = ? AND term_id = (SELECT term_id FROM term WHERE term_name = ?))
            """, (num_lessons, class_id, term_name)
        ) # student_id in (SELECT id FROM students WHERE class_id = ?) AND <- use this if wna specify all students for some reason, though ct_id is enough already. 

        conn.commit()
        conn.close()

        st.success("Setting number of lessons success!")
        return True
    except Exception as e:
        print(f"Error setting number of lessons: {e}")
        st.write(e)
        if conn:
            conn.close()  # Ensure the connection is closed in case of an error
        return False

def setNumberOfLessonsForStudent(class_id, term_name, student_id, num_lessons_set_for_student):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        ## update student_class_term too
        cur.execute(
            """
            UPDATE student_class_term
            SET num_less_attdng = ?
            WHERE student_id = ? AND ct_id = (SELECT ct_id FROM class_term WHERE class_id = ? AND term_id = (SELECT term_id FROM term WHERE term_name = ?))
            """, (num_lessons_set_for_student, student_id, class_id, term_name)
        )

        conn.commit()
        conn.close()

        # st.success("Setting {} number of lesson for student ID: {} success!".format(num_lessons_set_for_student, student_id))
        return True
    except Exception as e:
        print(f"Error setting {num_lessons_set_for_student} for student ID: {student_id}: {e}")
        st.write(e)
        if conn:
            conn.close()  # Ensure the connection is closed in case of an error
        return False


def getNumberOfLessons(class_id, term_name):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT num_lessons FROM class_term 
            WHERE class_id = ? AND term_id = (SELECT term_id FROM term WHERE term_name = ?)
            """, (class_id, term_name)
        )

        num_lessons = cur.fetchone()
        conn.close()

        return num_lessons[0] if num_lessons is not None else 0
    except Exception as e:
        print(f"Error getting number of lessons: {e}")
        st.write(e)
        return 0
    
def getExpectedRevenueForGivenTerm(term_name): #TODO verfiy and check for correctness
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        # Get the total revenue for the term by the following calculation in sql:
        # Get the ct_ids with the term_id, then for every student in student_class_term with the ct_id, get the rate from class_rate and multiply by the number of lessons in class_term, and multiply it with the student's discount rate, lastly give the sum as a single value

        cur.execute(
            """
            SELECT SUM((cr.rate - s.discount) * ct.num_lessons)
            FROM class_rate cr
            JOIN class_term ct ON cr.cid = ct.class_id
            JOIN student_class_term sct ON ct.ct_id = sct.ct_id
            JOIN students s ON sct.student_id = s.id
            WHERE ct.term_id = (SELECT term_id FROM term WHERE term_name = ?)
            """, (term_name,)
        )

        expected_revenue = cur.fetchone()[0]
        conn.close()

        return expected_revenue if expected_revenue is not None else 0
    except Exception as e:
        print(f"Error getting expected revenue: {e}")
        st.write(e)
        return 0
    

def getExistingSchools():
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT DISTINCT school FROM students
            """
        )

        schools = cur.fetchall()
        conn.close()

        schools = [school[0] for school in schools]
        print(f'Query success: \n{schools}')
        return schools if schools is not None else []
        
    except Exception as e:
        print(f"Error getting available schools: {e}")
        st.write(e)
        return None

def getCurrentPayment(student_id, term_name):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT amount_paid FROM student_class_term
            WHERE student_id = ? AND ct_id = (
                SELECT ct_id FROM class_term
                WHERE term_id = (SELECT term_id FROM term WHERE term_name = ?)
            )
            """, (student_id, term_name)
        )

        amount_paid = cur.fetchone()
        conn.close()

        return amount_paid[0] if amount_paid is not None else 0
    except Exception as e:
        print(f"Error getting current payment: {e}")
        st.write(e)
        return 0

def getTermDates(term_name):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT start_date, end_date FROM term
            WHERE term_name = ?
            """, (term_name,)
        )

        dates = cur.fetchone()
        conn.close()

        # rename columns to start_date and end_date
        if dates is None:
            return None

        return {"start_date": dates[0], "end_date": dates[1]}

    except Exception as e:
        print(f"Error getting term dates: {e}")
        st.write(e)
        return None

def getTermId(term_name):
    try:
        conn = connect(database_location)
        if conn is None:
            return False
        cur = conn.cursor()

        cur.execute(
            """
            SELECT term_id FROM term
            WHERE term_name = ?
            """, (term_name,)
        )

        term_id = cur.fetchone()
        conn.close()

        # rename columns to start_date and end_date
        if term_id is None:
            return None
            
        return int(term_id[0])

    except Exception as e:
        print(f"Error getting term id: {e}")
        st.write(e)
        return None