# Automated Student Enrollment ETL & AI Data Cleaning Pipeline

[![n8n Workflow](https://img.shields.io/badge/Orchestration-n8n-EA4B71?logo=n8n)](https://n8n.io/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/LLM-GPT--4o--mini-412991?logo=openai&logoColor=white)](https://openai.com/)
[![Pandas](https://img.shields.io/badge/Data%20Analysis-Pandas-150458?logo=pandas)](https://pandas.pydata.org/)
[![Pydantic](https://img.shields.io/badge/Schema%20Validation-Pydantic%20v2-E92063?logo=pydantic)](https://pydantic.dev/)

An automated **Extract, Transform, Load (ETL)** pipeline engineered to ingest raw, messy student enrollment data, standardize it using Generative AI (OpenAI GPT-4o-mini), perform deterministic deduplication and schema validation, filter records by location and email validity, and export production-ready datasets.

This repository provides two complete, interoperable implementations:
1. **n8n Workflow (`ETL AI AUTOMATION.json`)**: An event-driven, visual workflow with web-form triggers, LLM chains, batch loops, regex routing, and Excel export.
2. **Python Pipeline (`etl_pipeline.py`)**: A programmatic CLI pipeline utilizing Pandas and Pydantic Structured Outputs (`client.beta.chat.completions.parse`).

---

## 🏗️ System Architecture & Data Flow

```
                     RAW DATA SOURCE
       [ Web Form Upload ]  or  [ student_enrollment_raw.csv ]
               │                                │
               ▼ (n8n)                          ▼ (Python)
      [ Extract from File ]              [ pd.read_csv() ]
               │                                │
               ▼                                ▼
   [ Basic LLM Chain (n8n) ]           [ OpenAI Structured Outputs ]
   (Prompt: Title Case, dates,         (Pydantic Schema: CleanStudent,
    courses, fee normalization)         strict typing & conversions)
               │                                │
               ▼                                ▼
    [ Loop Over Items (Batch) ]          [ Clean DataFrame ]
               │                                │
               ▼                                ▼
    [ Code in JS (Regex/Sanitize) ]      [ Data Export: CSV ]
    • Strip non-digits from phone       `cleaned_students.csv`
    • Validate email syntax regex
    • Flag `is_email_valid`, `is_phone_valid`
               │
               ▼
    [ Remove Duplicates ] (By student_id)
               │
               ▼
    [ Code in JS1 ] (Safe trimming & lowercasing)
               │
               ▼
    [ If Node ] ──► (Matches `/[cC]hennai/` & `is_email_valid == true`)
               │
               ▼
    [ Convert to XLSX ]
    `chennai_emailed_user.xlsx`
```

---

## 📊 Data Transformation Rules & Schema

Both implementations enforce consistent standardization rules across raw fields:

| Field | Raw State (Messy) | Cleaned Output Rule |
| :--- | :--- | :--- |
| `Student_ID` | String / Numbers with spacing | Normalized integer / string identifier (`student_id`). |
| `Name` | Inconsistent casing, trailing spaces | Converted to proper **Title Case** (e.g., `Manoj K`). |
| `Email` | Missing, misformatted, domain typos | Trimmed, converted to **lowercase**; validated against regex (`is_email_valid: true/false`). Invalid set to `null` / `Invalid_Email`. |
| `Phone` | Extra spaces, dashes, parentheses | Stripped of non-numeric characters (`\D`). Must have 10–15 digits (`is_phone_valid`). |
| `Course` | Typos (`Pythn`, `ml`) | Standardized to approved catalog: `Python`, `Machine Learning`, or `Data Science`. |
| `Fee_Paid` | Strings (`yes`, `NO`), currency symbols | Normalized boolean (`true`/`false`) in n8n; numeric float in Python. |
| `City` | Inconsistent casing, empty | Proper **Title Case**; defaults to `UNKNOWN` if missing. |
| `Enrolled_Date`| Mixed formats (`DD/MM/YYYY`, text) | Normalized ISO standard `YYYY-MM-DD`. |

---

## ⚡ Implementation 1: n8n Workflow

The n8n workflow (`ETL AI AUTOMATION.json`) provides a full visual orchestration engine.

### Key Nodes Breakdown

1. **CSV Upload (`n8n-nodes-base.formTrigger`)**: Form-based file uploader accepting the input CSV document.
2. **Extract from File (`n8n-nodes-base.extractFromFile`)**: Parses incoming binary CSV data into JSON records.
3. **Basic LLM Chain + OpenAI Chat Model**: Calls `gpt-4.1-mini` / `gpt-4o-mini` with zero temperature to format casing, course names, and dates.
4. **Loop Over Items (`splitInBatches`) & Code in JavaScript**:
   * Parses JSON string outputs from the LLM.
   * Strips non-digit characters from phone numbers:
     ```javascript
     const digitsOnlyPhone = rawPhone.replace(/\D/g, '');
     const isPhoneValid = digitsOnlyPhone.length >= 10 && digitsOnlyPhone.length <= 15;
     ```
   * Evaluates RFC compliant email regex: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`.
   * Flags row-level diagnostics (`has_errors = !is_email_valid || !is_phone_valid`).
5. **Remove Duplicates (`n8n-nodes-base.removeDuplicates`)**: Deduplicates incoming entries by unique `student_id`.
6. **Code in JavaScript1**: Performs safe null-guarded whitespace trimming and casing operations:
   ```javascript
   item.json.name = item.json.name ? item.json.name.trim() : '';
   item.json.email = item.json.email ? item.json.email.trim().toLowerCase() : null;
   return item;
   ```
7. **If Node (Routing & Filtering)**: Isolates target candidates using two conditions:
   * `city` matches regex `/[cC]hennai/`
   * `is_email_valid == true`
8. **Convert to File (`convertToFile`)**: Outputs matched rows as an Excel document (`chennai_emailed_user.xlsx`).

---

## 🐍 Implementation 2: Python ETL Script

The Python script (`etl_pipeline.py`) performs standalone, batch-oriented data cleaning using Pydantic v2 schemas and OpenAI Structured Outputs.

### Key Modules

* **`CleanStudent` & `StudentCleaningBatch`**: Pydantic models ensuring strict schema adherence from LLM inference.
* **`extract_data()`**: Ingests raw CSV records via Pandas.
* **`transform_with_openai()`**: Sends records formatted as a JSON string to `gpt-4o-mini` using `client.beta.chat.completions.parse()`.
* **`load_final_csv()`**: Writes the resulting structured dataset to `cleaned_students.csv`.

---

## 🚀 Setup & Execution Guide

### Prerequisites
* Python 3.10+ (for Python script)
* n8n v1.0+ (self-hosted or n8n Cloud)
* OpenAI API Key

### Running the n8n Workflow
1. Open n8n and select **Add Workflow > Import from File**.
2. Upload `ETL AI AUTOMATION.json`.
3. Add your OpenAI credential under credentials settings.
4. Click **Test Step** or **Execute Workflow** and submit a raw CSV through the trigger form.
5. Retrieve the processed `chennai_emailed_user.xlsx` file.

### Running the Python Script
1. Clone this repository and navigate to the directory:
   ```bash
   git clone https://github.com/your-username/etl-ai-automation.git
   cd etl-ai-automation
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install pandas openai pydantic python-dotenv
   ```
4. Configure your `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```
5. Place your input CSV in the project folder as `student_enrollment_raw (2).csv` and run:
   ```bash
   python etl_pipeline.py
   ```
6. The cleaned file will be exported as `cleaned_students.csv`.

---

## 📁 Repository Structure

```
├── ETL AI AUTOMATION.json     # Complete export of the n8n workflow
├── etl_pipeline.py            # Standalone Python ETL script with Pydantic validation
├── README.md                  # Project overview and technical documentation
└── .env.example               # Template for environment configuration
```

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
