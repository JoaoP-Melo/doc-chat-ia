from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.conversation.router import router as conversation_router
from app.document.router import router as document_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(document_router)
app.include_router(conversation_router)
