
# 🧠 RAG Chatbot – Your Notes Buddy

This project is a **Retrieval-Augmented Generation (RAG)** based chatbot that allows users to upload a PDF or submit a website URL, and then ask questions based on that content. It leverages **LangChain**, **FAISS**, **HuggingFace embeddings**, and **Google's Gemini LLM** to deliver smart contextual answers from user-supplied data.

---

## 🚀 Features

- 📄 Upload **PDF** documents or 🌐 enter a **website URL**
- 🧠 Embeds text using `all-mpnet-base-v2` HuggingFace model
- 💬 Chat in real-time with a Google Gemini-powered bot
- 🗂️ FAISS vector store for efficient semantic search
- 🧰 Built with **FastAPI**, **LangChain**, and **Vanilla JS + HTML/CSS**

---

## 📁 Project Structure

```
├── main.py            # FastAPI backend with RAG logic
├── index.html         # Frontend UI for upload and chat
├── main.js            # JavaScript to handle form/chat logic
├── styles.css         # Stylesheet for responsive UI
├── faiss_index/       # Local vector store (auto-generated)
```

---

## ⚙️ Setup & Run

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/rag-chatbot.git
cd rag-chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

<details>
<summary><strong>requirements.txt sample</strong></summary>

```
fastapi
uvicorn
langchain
langchain-community
langchain-google-genai
huggingface-hub
sentence-transformers
faiss-cpu
pydantic
PyMuPDF
beautifulsoup4
requests
```

</details>

### 4. Set Up Google Gemini API Key

Export your Gemini API key (update `main.py` or use environment variable):

```bash
export GOOGLE_API_KEY=your-google-api-key
```

### 5. Run the App

```bash
uvicorn main:app --reload
```

### 6. Open the Frontend

Just open `index.html` in your browser (you may use Live Server in VSCode or host with Python HTTP server).

---

## 🌐 How It Works

1. **Upload a PDF or provide a URL** via the UI.
2. The server:
   - Extracts text from the file or webpage.
   - Splits content into chunks.
   - Embeds and stores in FAISS vector DB.
3. User asks a question.
4. RAG pipeline:
   - Retrieves top relevant chunks.
   - Gemini model generates a response using `langchain` QA chain.

---

## 📸 UI Overview

- Clean, responsive layout with **chatbox interface**
- File/URL input form
- Real-time Q&A interaction

---

## 🧪 Example Use Cases

- Preparing responses to RFPs or legal documents
- Conversational search on research papers or documentation
- Customer support for your product’s website content

---

## 📌 Notes

- Only one file or URL can be submitted at a time.
- Currently supports **PDFs** and **publicly accessible URLs**.
- Vector DB (`faiss_index/`) persists between sessions.

---

## 📄 License

MIT License
