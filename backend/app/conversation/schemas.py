from pydantic import BaseModel

class ConversationCreate(BaseModel):
    document_id: int


class QuestionRequest(BaseModel):
    conversation_id: int
    question: str


class PublicConversation(BaseModel):
    id: int
    title: str