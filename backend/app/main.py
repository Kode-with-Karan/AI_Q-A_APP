from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from .api import router as api_router
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)
if not os.getenv("OPENAI_API_KEY"):
    logger.warning("OPENAI_API_KEY not set. Set it in a .env file or environment to enable LLM features.")

app = FastAPI(title="AI Q&A App - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"ok": True, "message": "AI Q&A Backend is running"}
