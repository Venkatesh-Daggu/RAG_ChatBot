# 📚 College Notes RAG Chatbot

College Notes RAG Chatbot is an AI-powered Streamlit application that helps students ask questions from their uploaded notes.

Students can upload notes at runtime in **PDF**, **DOCX**, or **TXT** format. The app extracts text from the uploaded files, splits the text into smaller chunks, creates embeddings using **HuggingFaceEmbeddings**, stores them in **FAISS**, retrieves relevant chunks, and generates answers using the **Google Gemini API**.

---

## 🚀 Project Overview

Students often have long PDFs, notes, and study materials. Searching through those files manually takes time.

This project makes that process easier by allowing students to upload their notes and ask questions directly from them.

Example:

```text
Upload DBMS notes
Ask: Explain normalization
Get: A clear answer based on the uploaded notes
```

---

## ✨ Features

- Upload notes at runtime
- Supports PDF, DOCX, and TXT files
- Ask questions from uploaded notes
- Uses HuggingFaceEmbeddings for creating embeddings
- Uses FAISS for vector storage and similarity search
- Uses Gemini API for answer generation
- Multiple answer styles:
  - Simple explanation
  - Detailed explanation
  - Exam point of view
  - Short notes
  - Important points
- Chat history support
- Cache support for repeated questions
- Simple and clean Streamlit interface
- Suitable for Streamlit Community Cloud deployment

---

## 🧠 How the Project Works

```text
Student uploads notes
        ↓
Text is extracted from PDF/DOCX/TXT
        ↓
Text is divided into chunks
        ↓
HuggingFaceEmbeddings convert chunks into vectors
        ↓
FAISS stores the vectors
        ↓
Student asks a question
        ↓
FAISS retrieves the most relevant chunks
        ↓
Gemini generates the final answer
        ↓
Answer is displayed to the student
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Embeddings | HuggingFaceEmbeddings |
| Vector Database | FAISS |
| LLM | Google Gemini API |
| PDF Reader | pypdf |
| DOCX Reader | python-docx |
| Text Splitting | LangChain Text Splitters |
| Environment Variables | python-dotenv |

---

## 📁 Project Structure

```text
College_Bot/
│
├── app.py
├── requirements.txt
├── README.md
├── .env
└── .gitignore
```

---

## 🔑 Gemini API Key Setup

This project uses the Gemini API for generating answers.

Create a `.env` file in the project folder:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Do not upload the `.env` file to GitHub.

Add this to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
.streamlit/secrets.toml
```

---

## 📦 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Venkatesh-Daggu/RAG_ChatBot.git
cd RAG_ChatBot
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

For Windows:

```bash
venv\Scripts\activate
```

For Mac/Linux:

```bash
source venv/bin/activate
```

### 4. Install required packages

```bash
pip install -r requirements.txt
```

### 5. Run the app

```bash
streamlit run app.py
```

---

## 📌 Requirements

Create a `requirements.txt` file

---

## 🌐 Deployment on Streamlit Community Cloud

This project can be deployed on Streamlit Community Cloud.

### Deployment Steps

1. Push the project to GitHub
2. Open Streamlit Community Cloud
3. Connect your GitHub repository
4. Select `app.py` as the main file
5. Add Gemini API key in Streamlit Secrets
6. Deploy the app

In Streamlit Secrets, add:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

---

## 💬 Example Questions

After uploading notes, students can ask questions like:

```text
Explain normalization in DBMS
```

```text
Give important points from this unit
```

```text
Summarize the uploaded notes
```

```text
Explain this topic in exam point of view
```

```text
Generate short notes from this chapter
```

---

## ⚡ Cache Feature

This project includes a simple cache mechanism.

If the same question is asked again with the same answer style, the app retrieves the answer from cache instead of calling Gemini API again.

This helps to:

- Reduce repeated API calls
- Improve response speed
- Save quota usage

---

## ⚠️ Limitations

- Very large PDFs may take more time to process
- Scanned image PDFs may not work because OCR is not added
- HuggingFace embedding model may take time to load for the first time
- Gemini API quota limits may affect answer generation
- The app works best with clear text-based notes

---

## 🔮 Future Improvements

- Add OCR support for scanned PDFs
- Add PPT file support
- Add source page citations
- Add MCQ generation from notes
- Add chapter-wise summary
- Add user login system
- Save chat history permanently
- Store uploaded files in cloud storage


It combines document processing, embeddings, vector search, and LLM answer generation into one simple Streamlit app.

The main goal is to help students interact with their own study material in a faster and smarter way.
