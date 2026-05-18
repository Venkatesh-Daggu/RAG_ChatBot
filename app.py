import os
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv

from pypdf import PdfReader
from docx import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from google import genai


# -----------------------------
# 1. PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="College Notes RAG Chatbot",
    page_icon="📚",
    layout="wide"
)


# -----------------------------
# 2. LOAD GEMINI API KEY
# -----------------------------
def get_gemini_api_key():
    """
    First tries to read API key from Streamlit secrets.
    If not found, reads from local .env file.
    """

    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        load_dotenv()
        return os.getenv("GEMINI_API_KEY")


GEMINI_API_KEY = get_gemini_api_key()


# -----------------------------
# 3. EXTRACT TEXT FROM PDF
# -----------------------------
def extract_text_from_pdf(uploaded_file):
    text = ""

    pdf_reader = PdfReader(uploaded_file)

    for page_number, page in enumerate(pdf_reader.pages, start=1):
        page_text = page.extract_text()

        if page_text:
            text += f"\n\n--- Source: {uploaded_file.name}, Page: {page_number} ---\n"
            text += page_text

    return text


# -----------------------------
# 4. EXTRACT TEXT FROM DOCX
# -----------------------------
def extract_text_from_docx(uploaded_file):
    text = ""

    doc = Document(uploaded_file)

    for para in doc.paragraphs:
        if para.text.strip():
            text += para.text + "\n"

    return f"\n\n--- Source: {uploaded_file.name} ---\n{text}"


# -----------------------------
# 5. EXTRACT TEXT FROM TXT
# -----------------------------
def extract_text_from_txt(uploaded_file):
    file_bytes = uploaded_file.read()
    text = file_bytes.decode("utf-8", errors="ignore")

    return f"\n\n--- Source: {uploaded_file.name} ---\n{text}"


# -----------------------------
# 6. EXTRACT TEXT FROM ALL FILES
# -----------------------------
def extract_text_from_uploaded_files(uploaded_files):
    full_text = ""

    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name.lower()

        if file_name.endswith(".pdf"):
            full_text += extract_text_from_pdf(uploaded_file)

        elif file_name.endswith(".docx"):
            full_text += extract_text_from_docx(uploaded_file)

        elif file_name.endswith(".txt"):
            full_text += extract_text_from_txt(uploaded_file)

        else:
            st.warning(f"Unsupported file type: {uploaded_file.name}")

    return full_text


# -----------------------------
# 7. SPLIT TEXT INTO CHUNKS
# -----------------------------
def create_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = text_splitter.split_text(text)
    return chunks


# -----------------------------
# 8. CREATE VECTOR STORE USING HUGGINGFACE EMBEDDINGS
# -----------------------------
@st.cache_resource
def load_embedding_model():
    """
    This downloads/loads the HuggingFace embedding model.
    First time it may take some time.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return embeddings


def create_vector_store(chunks):
    embeddings = load_embedding_model()

    vector_store = FAISS.from_texts(
        texts=chunks,
        embedding=embeddings
    )

    return vector_store


# -----------------------------
# 9. ASK GEMINI LLM
# -----------------------------
def ask_gemini(question, context, answer_style):
    if not GEMINI_API_KEY:
        return "Gemini API key not found. Please add GEMINI_API_KEY in .env or Streamlit Secrets."

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
You are an AI-powered College Notes Assistant.

Your task is to help students understand their uploaded notes clearly and accurately.

You will receive:
1. Context extracted from the student's uploaded notes
2. The student's question
3. The required answer style

Follow these rules strictly:

1. First, understand the student's question and compare it with the given context.

2. If the question is directly answered in the context:
   - Answer using the context.
   - Keep the explanation clear, simple, and student-friendly.

3. If the question is related to the uploaded notes, but the exact answer is not found in the context:
   - Give a helpful general explanation using your own knowledge.
   - Start the answer with this line:
     "This exact answer was not found in the uploaded notes, but here is a general explanation:"
   - Do not add unnecessary extra topics.

4. If the question is not related to the uploaded notes or the subject in the context:
   - Reply only with:
     "No info"

5. Do not hallucinate facts from the uploaded notes.
6. Do not mention that you are an AI model.
7. Use simple language suitable for students.
8. Format the answer according to this answer style: {answer_style}

Context:
{context}

Student Question:
{question}

Answer:
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


# -----------------------------
# 10. RETRIEVE RELEVANT CHUNKS
# -----------------------------
def retrieve_relevant_docs(vector_store, question, k=4):
    docs = vector_store.similarity_search(question, k=k)
    return docs


# -----------------------------
# 11. CACHE KEY FUNCTION
# -----------------------------
def make_cache_key(question, answer_style):
    clean_question = question.strip().lower()
    clean_style = answer_style.strip().lower()
    return f"{clean_question}__{clean_style}"


# -----------------------------
# 12. STREAMLIT UI
# -----------------------------
st.title("📚 College Notes RAG Chatbot")
st.write("Upload your college notes and ask questions from them.")

with st.sidebar:
    st.header("📤 Upload Notes")

    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, or TXT notes",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

    answer_style = st.selectbox(
        "Choose answer style",
        [
            "Simple explanation",
            "Detailed explanation",
            "Exam point of view",
            "Short notes",
            "Important points"
        ]
    )

    process_button = st.button("Process Notes")



# -----------------------------
# 13. INITIALIZE SESSION STATE
# -----------------------------
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "answer_cache" not in st.session_state:
    st.session_state.answer_cache = {}


# -----------------------------
# 14. PROCESS UPLOADED NOTES
# -----------------------------
if process_button:
    if not uploaded_files:
        st.warning("Please upload at least one notes file.")
    else:
        with st.spinner("Extracting text from uploaded notes..."):
            extracted_text = extract_text_from_uploaded_files(uploaded_files)

        if not extracted_text.strip():
            st.error("No text could be extracted from the uploaded files.")
        else:
            with st.spinner("Splitting text into chunks..."):
                chunks = create_chunks(extracted_text)

            with st.spinner("Creating HuggingFace embeddings and FAISS vector database..."):
                vector_store = create_vector_store(chunks)

            st.session_state.vector_store = vector_store
            st.session_state.chunks = chunks

            st.session_state.answer_cache = {}
            st.session_state.chat_history = []

            st.success(f"Notes processed successfully! Created {len(chunks)} chunks.")
            st.info("Old answer cache cleared because new notes were processed.")


# -----------------------------
# 15. QUESTION ANSWERING SECTION
# -----------------------------
st.markdown("## 💬 Ask Question from Your Notes")

question = st.text_input(
    "Enter your question",
    placeholder="Example: Explain normalization in DBMS"
)

ask_button = st.button("Ask")

if ask_button:
    if st.session_state.vector_store is None:
        st.warning("Please upload and process notes first.")

    elif not question.strip():
        st.warning("Please enter a question.")

    else:
        cache_key = make_cache_key(question, answer_style)

        # -----------------------------
        # CHECK CACHE FIRST
        # -----------------------------
        if cache_key in st.session_state.answer_cache:
            cached_data = st.session_state.answer_cache[cache_key]

            answer = cached_data["answer"]
            docs = cached_data["sources"]

        else:
            # -----------------------------
            # IF NOT IN CACHE, RUN RAG
            # -----------------------------
            with st.spinner("Retrieving relevant chunks from FAISS..."):
                docs = retrieve_relevant_docs(
                    st.session_state.vector_store,
                    question,
                    k=4
                )

                context = "\n\n".join([doc.page_content for doc in docs])

            with st.spinner("Generating answer using Gemini..."):
                answer = ask_gemini(
                    question=question,
                    context=context,
                    answer_style=answer_style
                )

            # -----------------------------
            # SAVE ANSWER TO CACHE
            # -----------------------------
            st.session_state.answer_cache[cache_key] = {
                "answer": answer,
                "sources": docs
            }


        # -----------------------------
        # SAVE TO CHAT HISTORY
        # -----------------------------
        st.session_state.chat_history.append(
            {
                "question": question,
                "answer": answer,
                "sources": docs
            }
        )

        st.markdown("### ✅ Answer")
        st.write(answer)


# -----------------------------
# 16. SHOW CHAT HISTORY
# -----------------------------
if st.session_state.chat_history:
    st.markdown("---")
    st.markdown("## 🕘 Chat History")

    for i, chat in enumerate(reversed(st.session_state.chat_history), start=1):
        with st.expander(f"Question {i}: {chat['question']}"):
            st.markdown("**Answer:**")
            st.write(chat["answer"])
