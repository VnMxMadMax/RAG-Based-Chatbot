from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import logging
import os
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize FastAPI app
app = FastAPI()

# Logger setup
logging.basicConfig(level=logging.INFO)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
os.environ['GOOGLE_API_KEY'] = "your-api-key"
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

# Global variables
vector_store = None
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# Models
class ChatInput(BaseModel):
    question: str

# PDF extraction
def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        text = ""
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text.strip()
    except Exception as e:
        logging.error(f"PDF extraction failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF.")

# URL extraction
def extract_text_from_url(url: str) -> str:
    try:
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")

        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        logging.error(f"URL extraction failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract text from URL.")

# Upload endpoint
@app.post("/upload")
async def upload_data(
    myfile: UploadFile = File(None),
    url: str = Form(None)
):
    if not myfile and not url:
        return JSONResponse({"error": "Provide a PDF or URL"}, status_code=400)

    if myfile and url:
        return JSONResponse({"error": "Only provide a PDF or a URL, not both"}, status_code=400)

    # Extract text
    if myfile:
        if not myfile.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        contents = await myfile.read()
        text = extract_text_from_pdf(contents)
    else:
        text = extract_text_from_url(url)

    if not text.strip():
        raise HTTPException(status_code=400, detail="Extracted content is empty.")

    # Create LangChain Document
    doc = Document(page_content=text)
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
    chunks = splitter.split_documents([doc])

    # Embed & store
    global vector_store
    vector_store = FAISS.from_documents(chunks, embedding_model)
    vector_store.save_local("faiss_index")

    return {"message": f"Uploaded and embedded successfully. {len(text)} characters processed."}

# Chat endpoint
@app.post("/chat")
async def chat_with_doc(input: ChatInput):
    global vector_store
    
    if not vector_store:
        # Try to load persisted vector store if available
        if os.path.exists("faiss_index"):
            vector_store = FAISS.load_local(
                "faiss_index", 
                embedding_model, 
                allow_dangerous_deserialization=True
            )
        else:
            return JSONResponse({"error": "No data uploaded yet"}, status_code=400)

    # Retrieve relevant chunks from the vector store
    docs = vector_store.similarity_search(input.question, k=3)

    # Use Gemini model from Google Generative AI
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", convert_system_message_to_human=True)

    # Load the QA chain
    chain = load_qa_chain(llm, chain_type="stuff")
    answer = chain.run(input_documents=docs, question=input.question)

    return {"question": input.question, "answer": answer}

# Load persisted vector store if available at startup
if os.path.exists("faiss_index"):
    vector_store = FAISS.load_local(
        "faiss_index", 
        embedding_model, 
        allow_dangerous_deserialization=True
    )
