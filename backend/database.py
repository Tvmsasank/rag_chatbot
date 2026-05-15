import os
import pyodbc
from dotenv import load_dotenv

# LOAD .env VARIABLES
load_dotenv()

# MSSQL CONNECTION

conn = pyodbc.connect(
    f"""
    DRIVER={{ODBC Driver 17 for SQL Server}};
    SERVER={os.getenv('DB_SERVER')};
    DATABASE={os.getenv('DB_DATABASE')};
    UID={os.getenv('DB_USERNAME')};
    PWD={os.getenv('DB_PASSWORD')};
    TrustServerCertificate=yes;
    """
)

cursor = conn.cursor()

# =====================================================
# GET COMPLETE STUDENT DETAILS
# =====================================================

def get_student_full_details(hallticket):

    cursor.execute(
        """
        SELECT
            StudentId,
            HallTicket,
            Name,
            FeesDue,
            Attendance,
            Course,
            Batch,
            Email,
            Phone,
            Address,
            DOB,
            ParentName,
            ParentContact,
            ExamResult,
            AssignmentsPending,
            LibraryBooksIssued,
            TransportRoute,
            ScholarshipStatus
        FROM StudentsICFAI
        WHERE HallTicket = ?
        """,
        (hallticket,)
    )

    return cursor.fetchone()