from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from .services.transcribe import transcribe_audio
import uuid
from io import BytesIO
import PyPDF2
from .services.llm_client import ask_llm, summarize_text
import logging

logger = logging.getLogger(__name__)
import os

router = APIRouter()

# Simple in-memory store for uploaded documents: id -> {filename, text}
UPLOAD_STORE = {}

class UploadResponse(BaseModel):
    id: str
    filename: str
    text: str

@router.post('/upload', response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    content_type = file.content_type or "application/octet-stream"
    filename = file.filename
    data = await file.read()
    # For audio/video we transcribe; for PDFs we could extract text (placeholder)
    if content_type.startswith('audio') or content_type.startswith('video'):
        text = await transcribe_audio(data, filename)
    elif filename.lower().endswith('.pdf'):
        # Extract text from PDF bytes
        try:
            reader = PyPDF2.PdfReader(BytesIO(data))
            texts = []
            for p in reader.pages:
                try:
                    texts.append(p.extract_text() or "")
                except Exception:
                    texts.append("")
            text = "\n\n".join(texts).strip()
        except Exception:
            text = ""
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    # Persist to in-memory store and return generated id
    doc_id = str(uuid.uuid4())
    UPLOAD_STORE[doc_id] = {"filename": filename, "text": text}
    return UploadResponse(id=doc_id, filename=filename, text=text)

class ChatRequest(BaseModel):
    doc_id: Optional[str]
    question: str

class ChatResponse(BaseModel):
    answer: str
    timestamps: Optional[List[float]] = None

@router.post('/chat', response_model=ChatResponse)
async def chat(req: ChatRequest):
    # Retrieve doc text by id (from in-memory store)
    doc_text = ""
    doc_filename = None
    if req.doc_id:
        doc = UPLOAD_STORE.get(req.doc_id)
        if doc:
            doc_text = doc.get('text', '')
            doc_filename = doc.get('filename')

    if not doc_text:
        return JSONResponse({"error": "No document text available for the given doc_id. Please upload a document and retry."}, status_code=400)

    # Build a strict prompt that instructs the LLM to answer using only the document.
    # Keep the context size reasonable: include the full text for now (could be chunked later).
    instruction = (
        "You are an assistant that MUST answer using ONLY the content of the provided document. "
        "Do not fabricate or hallucinate. If the document does not contain the information, reply: 'The document does not provide that information.' "
        "Be concise and, when possible, include a short quoted excerpt and indicate a reference (filename)."
    )

    prompt = f"{instruction}\n\nDocument Filename: {doc_filename or 'unknown'}\n\nDocument:\n" + doc_text + f"\n\nQuestion: {req.question}\n\nAnswer:" 

    try:
        answer = await ask_llm(prompt)
        return ChatResponse(answer=answer)
    except Exception as e:
        logger.exception("Error in /api/chat")
        return JSONResponse({"error": str(e)}, status_code=500)

@router.post('/summarize')
async def summarize(text: str = Form(...)):
    s = await summarize_text(text)
    return JSONResponse({"summary": s})


@router.get('/health')
async def health():
    """Return basic health and whether LLM key is configured."""
    llm_ok = bool(os.getenv('OPENAI_API_KEY'))
    return JSONResponse({"ok": True, "llm_configured": llm_ok})
