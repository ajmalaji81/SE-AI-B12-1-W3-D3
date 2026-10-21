# Automated CSV Data Cleaning Pipeline (ETL with n8n & OpenAI)

An automated, end-to-end ETL (Extract, Transform, Load) workflow built in **n8n** that ingests messy, unstructured raw CSV data, cleans and standardizes it using an **OpenAI LLM Chain**, formats it via custom **JavaScript**, and exports a clean, analysis-ready CSV file.

---

## 📌 Architecture Overview

```
[ Raw CSV Upload ]
        │
        ▼
[ Extract from File ]  (Converts CSV binary to JSON objects)
        │
        ▼
[ Basic LLM Chain ]    (OpenAI Model: Cleans, standardizes, & normalizes data)
        │
        ▼
[ Code (JavaScript) ]  (Validates, parses JSON, and enforces schema)
        │
        ▼
[ Convert to File ]    (Re-packs cleaned JSON into a standardized CSV)
```

---

## 🚀 Workflow Nodes Breakdown

| Node Name | Node Type | Purpose |
| :--- | :--- | :--- |
| **CSV Upload** | Manual / Trigger | Accepts the raw, uncleaned CSV file as binary input. |
| **Extract from File** | Data Transformation | Parses raw binary data into individual structured JSON records for batch processing. |
| **Basic LLM Chain** | LangChain / AI | Sends records to OpenAI to fix inconsistencies, extract fields, standardize naming, and clean messy text. |
| **OpenAI Chat Model** | AI Credential Model | Provides LLM inference (e.g., `gpt-4o-mini` / `gpt-3.5-turbo`) powering the cleaning chain. |
| **Code in JavaScript** | Code Execution | Programmatically parses model responses, handles null fallbacks, and standardizes column structures. |
| **Convert to File** | Data Output | Converts the transformed JSON array back into a production-ready, clean CSV file. |

---

## 🛠️ Prerequisites

- **n8n** (Cloud or self-hosted via Docker/npm)
- **OpenAI API Key** with available credits

---

## ⚙️ Setup & Installation

1. **Import the Workflow:**
   - In your n8n workspace, create a new workflow.
   - Click the top-right menu `...` -> **Import from File** or paste the exported workflow JSON.

2. **Configure OpenAI Credentials:**
   - Open the **OpenAI Chat Model** node.
   - Select or add your OpenAI API Credentials.

3. **Configure Custom JavaScript:**
   - In the **Code in JavaScript** node, customize any specific schema validations, column renames, or type castings specific to your dataset.

4. **Run the Pipeline:**
   - Click **Execute Workflow**.
   - Upload your dirty/unprocessed CSV into the **CSV Upload** node.
   - Download the final cleaned CSV from the **Convert to File** node output.

---

## 💡 Example Transformation

- **Raw Input:** Inconsistent casing (`jOHn dOE`), mismatched phone numbers, misspelled categories, or missing country codes.
- **Cleaned Output:** Standardized casing (`John Doe`), normalized E.164 phone formats, unified category names, and consistent schema columns.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
