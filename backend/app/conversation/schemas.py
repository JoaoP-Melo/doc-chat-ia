from pydantic import BaseModel

class ConversationCreate(BaseModel):
    document_id: int