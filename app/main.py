from fastapi import FastAPI
from app.api import documents, chat

app = FastAPI(title="Healthcare Document Chat API", version="1.0.0")

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}

#Routers
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])