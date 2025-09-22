import sqlite3 

def create_tables(cur):
    # Create the students table with email field
    cur.execute("""
        CREATE TABLE students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        school TEXT,
        grad_year TEXT,
        number TEXT NOT NULL,
        email TEXT,
        class_id INTEGER,
        discount REAL(5, 2),
        parent1 INTEGER,
        parent2 INTEGER,
        active BOOLEAN,
        FOREIGN KEY (class_id) REFERENCES class_rate(cid),
        FOREIGN KEY (parent1) REFERENCES parents(id),
        FOREIGN KEY (parent2) REFERENCES parents(id)
        )
    """)

    # Create the parents table
    cur.execute("""
        CREATE TABLE parents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        hp_number TEXT NOT NULL,
        email TEXT NOT NULL,
        UNIQUE(name, hp_number, email)
        )
    """)

    # Create the student_class_term table
    cur.execute("""
        CREATE TABLE student_class_term (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        ct_id INTEGER,
        invoice_id INTEGER,
        paid BOOLEAN DEFAULT FALSE,
        amount_paid REAL DEFAULT 0.00,
        refund REAL DEFAULT 0.00,
        refund_reason TEXT,
        num_less_attdng INTEGER DEFAULT 12,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (ct_id) REFERENCES class_term(ct_id),
        FOREIGN KEY (invoice_id) REFERENCES invoices(id),
        UNIQUE(student_id, ct_id)
        )
    """)

    # Create the term table
    cur.execute("""
        CREATE TABLE term (
        term_id INTEGER PRIMARY KEY AUTOINCREMENT,
        term_name TEXT NOT NULL UNIQUE CHECK(term_name <> ''),
        start_date DATE NOT NULL,
        end_date DATE NOT NULL
        )
    """)

    # Create the invoices table
    cur.execute("""
        CREATE TABLE invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_num TEXT NOT NULL,
        amount REAL(10, 2) NOT NULL,
        term_id INTEGER,
        FOREIGN KEY (term_id) REFERENCES term(term_id)
        )
    """)

    # Create the class_rate table
    cur.execute("""
        CREATE TABLE class_rate (
        cid INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE CHECK(name <> ''),
        rate REAL(5, 2) NOT NULL
        )
    """)

    # Create the email_messages table
    cur.execute("""
        CREATE TABLE email_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_subject TEXT NOT NULL,
        email_body TEXT NOT NULL,
        date_created DATE NOT NULL
        )
    """)

    # Create the class_term table
    cur.execute("""
        CREATE TABLE class_term (
        ct_id INTEGER PRIMARY KEY AUTOINCREMENT,
        term_id INTEGER,
        class_id INTEGER,
        num_lessons INTEGER DEFAULT 12,
        FOREIGN KEY (term_id) REFERENCES term(term_id),
        FOREIGN KEY (class_id) REFERENCES class_rate(cid),
        UNIQUE (term_id, class_id)
        )
    """)
        

    cur.execute(
        """
        INSERT INTO email_messages (email_subject, email_body, date_created)
        VALUES 
        ("TRT Tuition Fee Invoice for your child\'s learning.", 
        "Dear Student/Parent of <student_name>,\n\nReminder: Your child\'s tuition fee is due.\n\nPlease find attached the invoice for this term.\n\nPlease include your Invoice number <invoice_number> in the Reference or Comments when making payment.\n\nThis is an automated message.", 
        DATE('now'))
        """
    )



def setupDB():
    con = sqlite3.connect("src/db/DB.db")
    cur = con.cursor()

    # Drop the tables if they exist
    cur.execute("DROP TABLE IF EXISTS students")
    cur.execute("DROP TABLE IF EXISTS parents")
    cur.execute("DROP TABLE IF EXISTS student_class_term")
    cur.execute("DROP TABLE IF EXISTS term")
    cur.execute("DROP TABLE IF EXISTS invoices")
    cur.execute("DROP TABLE IF EXISTS class_rate")
    cur.execute("DROP TABLE IF EXISTS email_messages")
    cur.execute("DROP TABLE IF EXISTS class_term")
    
    # Create the tables
    create_tables(cur)

    # Insert dummy data
    insertDummyData(cur)

    con.commit()
    con.close()


if __name__ == "__main__":
    setupDB()



