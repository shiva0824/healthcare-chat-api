import os
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.document_processor import extract_text
from app.utils.logger import log_info, log_error
from app.models.schemas import DocumentResponse, DocumentUpload

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory DB substitute
documents_db = {}

@router.post(
    "/upload",
    response_model=DocumentResponse,
    summary="Upload and process a document",
    description="Accepts PDF, DOCX, and TXT files, validates and extracts text content."
)
async def upload_document(file: UploadFile = File(...)):
    """Handles document upload, validation, extraction, and metadata storage."""
    allowed_types = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "text/plain": "txt",
    }

    if file.content_type not in allowed_types:
        log_error(f"Unsupported file type: {file.filename}")
        raise HTTPException(status_code=415, detail="Unsupported file type")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > 10:
        log_error(f"File too large: {file.filename}")
        raise HTTPException(status_code=413, detail="File size exceeds 10 MB limit")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(contents)

    try:
        extracted_text = extract_text(file_path, allowed_types[file.content_type])
        extracted_len = len(extracted_text)
    except Exception as e:
        log_error(f"Extraction failed for {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="Text extraction failed")

    # stores metadata of the uploaded file
    document_data = DocumentResponse(
        id=file_id,
        filename=file.filename,
        file_type=allowed_types[file.content_type],
        file_size=len(contents),
        upload_timestamp=datetime.utcnow(),
        processing_status="completed",
        extracted_text_length=extracted_len,
    )
    
    # .model_dump() converts the Pydantic model into a plain Python dict before storing.
    documents_db[file_id] = document_data.model_dump()
    log_info(f"Uploaded {file.filename} ({document_data.file_type})")

    return document_data


@router.get(
    "/",
    summary="List all uploaded documents",
    description="Returns metadata for all uploaded documents currently stored in memory."
)
def list_documents():
    return {"documents": list(documents_db.values())}


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Retrieve a specific document",
    description="Fetches metadata for a specific uploaded document using its unique ID."
)
def get_document(document_id: str):
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    return documents_db[document_id]


@router.delete(
    "/{document_id}",
    summary="Delete a document",
    description="Removes the uploaded file and its metadata from in-memory storage."
)
def delete_document(document_id: str):
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    file_prefix = document_id + "_"
    for f in os.listdir(UPLOAD_DIR):
        if f.startswith(file_prefix):
            try:
                os.remove(os.path.join(UPLOAD_DIR, f))
            except Exception as e:
                log_error(f"Error deleting file {f}: {e}")

    del documents_db[document_id]
    log_info(f"Deleted document {document_id}")
    return {"message": "Document deleted successfully"}