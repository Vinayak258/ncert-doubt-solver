# 📚 NCERT Doubt Solver (AI)

> **Team:** iDeatorsX  
> **Status:** Final Submission Ready  

---

## 🚀 Project Overview

The **NCERT Doubt Solver** is an AI-powered educational assistant designed to help Indian students (Classes 6, 8, 10) by answering queries **strictly** from official NCERT textbooks. 

Unlike general AI tools (like ChatGPT), this system:
*   **Uses RAG (Retrieval-Augmented Generation)**: It reads the textbook first, then answers.
*   **Prevents Hallucinations**: If the answer isn't in the book, it says "Out of Syllabus".
*   **Is Multilingual**: Supports both **English** and **Hindi**.
*   **Provides Citations**: Every answer proves its source (Chapter & Page number).

---

## 🏗️ Architecture Overview

The system processes data in a clear pipeline:

1.  **PDF Ingestion**: Official NCERT PDFs are read and cleaned.
2.  **Chunking**: Text is split into meaningful small parts (chunks).
3.  **Embeddings**: Chunks are converted into vector numbers (using `all-MiniLM-L12-v2`).
4.  **FAISS Retrieval**: User questions search this vector database for the best matches.
5.  **LLM Generation**: The retrieved text + user question is sent to **Google Gemini**.
6.  **UI**: The final answer is shown on a Student-Friendly Web Interface.

---

## ✨ Key Features

*   **🛡️ Strict NCERT Grounding**: Answers are verified against the textbook context.
*   **🔄 Incremental Ingestion**: Recognizes already processed files to save time.
*   **📚 Transparency**: Citations are displayed for every single answer.
*   **🚫 Out-of-Syllabus Guard**: Blocks questions that are not covered in the curriculum.
*   **⚠️ Graceful Quota Handling**: If the AI model (Gemini) is busy/limited, the system still shows the relevant textbook pages.

---

## 💻 Installation & Setup

Follow these steps to run the project on your local machine.

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ncert-doubt-solver
```

### 2. Set Up Virtual Environment (Recommended)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
**Important**: You need a Google Gemini API Key.
1.  Create a file named `.env` in the root folder.
2.  Add your key inside it:
    ```
    GOOGLE_API_KEY=your_actual_api_key_here
    ```
    *(Note: This file is ignored by Git for security.)*

---

## 🏃 How to Run the Project

### Start the User Interface
Run the following command:
```bash
streamlit run ui/app.py
```

*   The web app will open automatically in your browser.
*   Local URL: `http://localhost:8501`

---

## 🧪 Testing the System

### ✅ Test In-Syllabus Questions
Select **Class 6 - Science** and ask:
*   *"What are the components of food?"*
*   *"Explain the process of photosynthesis."*

**Expected Result**: A clear answer with citations (Page numbers).

### 🛑 Test Out-of-Syllabus Guardrails
Ask a question not in the book:
*   *"How does a nuclear reactor work?"* (For Class 6)
*   *"Who is the President of USA?"*

**Expected Result**: *"This topic is not covered in the NCERT textbook for this class."*

---

## ⚠️ Known Limitations

1.  **Gemini Free Tier Quota**: The system runs on the free tier of the Google Gemini API.
    *   If you see *"The system is temporarily unable to generate an answer"*, it means the Rate Limit (RPM) was hit.
    *   **Good News**: The Retrieval (Sources) will still appear, so the tool remains useful.
2.  **Text Only**: Currently, the system does not process images or diagrams from the PDFs.

---

## 🔒 Why is this not deployed?
This project is submitted as a **local-run application** for academic/hackathon evaluation because:
1.  **API Security**: We cannot expose our personal API keys on a public server.
2.  **Resource Limits**: The free tier of the LLM has per-minute request limits suitable for local testing but not public traffic.

---

*Built by **Team iDeatorsX** | NCERT Doubt Solver Project*
