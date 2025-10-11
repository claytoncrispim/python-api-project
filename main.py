import os
import psycopg2
from fastapi import FastAPI, HTTPException
# We also import BaseModel from Pydantic to define our data structure
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

# --- Configuration ---
# Load the environment variables from our .env file
load_dotenv()

# --- FastAPI App Initialization ---
app = FastAPI()

# --- Pydantic Models (Our Data Structures) ---
class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/contact")
def submit_contact_form(form_data: ContactForm):
    conn = None  # Initialize connection to None
    try:
        # --- 1. Establish Database Connection ---
        # Read the credentials from the environment variables
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        # Create a "cursor" to execute SQL commands
        cur = conn.cursor()

        # --- 2. Write the SQL INSERT Command ---
        # This SQL statement will insert a new row into our 'submissions' table.
        # We use %s placeholders to prevent SQL injection attacks. This is a crucial security practice!
        sql_command = """
            INSERT INTO submissions (name, email, message) 
            VALUES (%s, %s, %s);
        """
        
        # --- 3. Execute the Command ---
        # Pass the SQL command and a tuple of the data to the cursor.
        cur.execute(sql_command, (form_data.name, form_data.email, form_data.message))
        
        # --- 4. Commit the Transaction ---
        # This saves the changes to the database.
        conn.commit()
        
        # --- 5. Close the cursor and connection ---
        cur.close()
        
        # Return a success message
        return {
            "status": "success",
            "message": "Contact form submitted and saved to database successfully!"
        }

    except psycopg2.Error as e:
        # If any database error occurs, print it for debugging
        print("Database error:", e)
        # Return a 500 Internal Server Error to the client
        raise HTTPException(status_code=500, detail="Database connection error.")
        
    finally:
        # --- 6. The "Finally" block always runs ---
        # This ensures our connection is closed, even if an error occurred.
        if conn is not None:
            conn.close()

