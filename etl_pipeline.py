import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional

# Load environment variables (.env file)
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------------------------------------------------
# Schema: Exact column structure from your CSV
# ---------------------------------------------------------------------------
class CleanStudent(BaseModel):
    Student_ID: int = Field(description="Unique student identifier as an integer")
    Name: str = Field(description="Full name, trimmed and converted to proper Title Case")
    Email: str = Field(description="Standardized valid email in lowercase")
    Phone: str = Field(description="Standardized phone number format, e.g., +91XXX-XXX-XXXX or standard 10-digit")
    Course: str = Field(description="Cleaned, standardized course name with typos corrected")
    Fee_Paid: float = Field(description="Clean numeric fee amount paid without currency symbols")
    City: str = Field(description="City name in proper Title Case")
    Enrolled_Date: str = Field(description="Normalized enrollment date strictly in YYYY-MM-DD format")

class StudentCleaningBatch(BaseModel):
    cleaned_students: List[CleanStudent]

# ---------------------------------------------------------------------------
# ETL Functions
# ---------------------------------------------------------------------------

def extract_data(file_path: str) -> pd.DataFrame:
    """Step 1 & 2: Load and read the raw CSV file."""
    print(f"[EXTRACT] Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    print(f"[EXTRACT] Loaded {len(df)} rows.")
    return df


def transform_with_openai(df: pd.DataFrame) -> pd.DataFrame:
    """Step 3: Clean and standardize student data using OpenAI Structured Outputs."""
    print("[TRANSFORM] Sending uncleaned records to OpenAI...")

    # Convert the raw rows into JSON format
    raw_data_json = df.to_json(orient="records")

    prompt = f"""
    You are a professional data cleaning specialist. Clean, correct, and standardize the following student records:

    Rules:
    1. Student_ID: Ensure it is a valid integer.
    2. Name: Fix casing (Title Case), extra spaces, and obvious typos.
    3. Email: Standardize to lowercase and fix common domain typos (e.g., 'gamil.com' -> 'gmail.com').
    4. Phone: Remove unwanted characters and format uniformly.
    5. Course: Fix abbreviations or typos to standard course titles (e.g., 'Pythn' -> 'Python').
    6. Fee_Paid: Strip any currency symbols ($/₹/€) or commas and convert to a clean numeric float.
    7. City: Fix spelling mistakes and format in Title Case.
    8. Enrolled_Date: Parse and standardize any date format into standard ISO 'YYYY-MM-DD'.

    Raw Data:
    {raw_data_json}
    """

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You clean and standardize messy educational CSV datasets into strictly structured schemas."},
            {"role": "user", "content": prompt}
        ],
        response_format=StudentCleaningBatch,
        temperature=0.0
    )

    cleaned_records = response.choices[0].message.parsed.cleaned_students
    cleaned_df = pd.DataFrame([record.model_dump() for record in cleaned_records])
    print(f"[TRANSFORM] Successfully cleaned {len(cleaned_df)} rows.")
    return cleaned_df


def load_final_csv(df: pd.DataFrame, output_path: str) -> None:
    """Step 4: Save the final cleaned CSV file."""
    print(f"[LOAD] Writing clean dataset to {output_path}...")
    df.to_csv(output_path, index=False)
    print(f"[LOAD] Successfully saved output to {output_path}!")


# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Ensure your input filename matches your actual file name
    input_file = "student_enrollment_raw (2).csv"
    output_file = "cleaned_students.csv"

    # Step 1 & 2: Extract & Read
    raw_df = extract_data(input_file)

    # Step 3: Transform (OpenAI)
    cleaned_df = transform_with_openai(raw_df)

    # Step 4: Load
    load_final_csv(cleaned_df, output_file)