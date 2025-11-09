from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import UploadFile
from pydantic import BaseModel

class DocumentUpload(BaseModel):
    file: UploadFile
    description: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    upload_timestamp: datetime
    processing_status: str
    extracted_text_length: int

class ChatMessage(BaseModel):
    session_id: str
    message: str
    context_documents: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    confidence_score: float
    processing_time: float