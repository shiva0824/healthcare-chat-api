from PyPDF2 import PdfReader
from docx import Document

def extract_text(file_path: str, file_type: str) -> str:
    """Extract text from PDF, DOCX, or TXT."""
    text = ""

    if file_type == "pdf":
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""

    elif file_type == "docx":
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    elif file_type == "txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    return text.strip()