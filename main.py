import os
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# --- Configuration & Initialization ---
# Load environment variables from a .env file for secure configuration.
load_dotenv()

# Initialize the FastAPI application.
app = FastAPI()


# --- Pydantic Data Models ---
class ContactForm(BaseModel):
    """Defines the data structure and validation for a contact form submission."""
    name: str
    email: EmailStr
    message: str


# --- API Endpoints ---
@app.get("/")
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"status": "API is running"}


@app.get("/submissions")
def get_submissions():
    """
    Retrieves all submission records from the PostgreSQL database.

    Returns:
        A list of dictionaries, where each dictionary represents a submission.
        Returns a 404 error if no submissions are found.
    
    Raises:
        HTTPException: 500 status code for database connection or operational errors.
    """
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        # Use RealDictCursor to get results as a list of dictionaries.
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT id, name, email, message, submitted_at FROM submissions;")
        submissions = cur.fetchall()
        
        cur.close()

        if not submissions:
            raise HTTPException(status_code=404, detail="No submissions found.")

        return submissions

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error - Database operation failed.")
    finally:
        if conn is not None:
            conn.close()


@app.post("/contact")
def submit_contact_form(form_data: ContactForm):
    """
    Accepts a contact form submission and saves it to the PostgreSQL database.

    Args:
        form_data: A Pydantic model containing the validated name, email, and message.

    Returns:
        A success message upon successful insertion into the database.
    
    Raises:
        HTTPException: 500 status code for database connection or operational errors.
    """
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cur = conn.cursor()

        # Use parameterized queries (%s) to prevent SQL injection vulnerabilities.
        sql_command = """
            INSERT INTO submissions (name, email, message) 
            VALUES (%s, %s, %s);
        """
        
        cur.execute(sql_command, (form_data.name, form_data.email, form_data.message))
        
        conn.commit()
        cur.close()
        
        return {
            "status": "success",
            "message": "Contact form submitted successfully!"
        }

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error - Database operation failed.")
    finally:
        if conn is not None:
            conn.close()
