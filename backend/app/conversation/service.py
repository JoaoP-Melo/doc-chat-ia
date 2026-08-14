from http import HTTPStatus
import os

from dotenv import load_dotenv
from fastapi import HTTPException
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.conversation.models import Conversations, Messages
from app.document.models import Documents, DocumentsChunks

model = SentenceTransformer("all-MiniLM-L6-v2")
load_dotenv()
API_KEY = os.getenv("API_KEY")


def add_conversation_in_db(user_id, document_id, session: Session):
    document_in_db = session.scalar(
        select(Documents).where(
            Documents.id == document_id, Documents.user_id == user_id
        )
    )

    new_conversation = Conversations(
        user_id=user_id,
        document_id=document_id,
        title=document_in_db.name,
    )

    session.add(new_conversation)
    session.commit()


def read_conversations_in_db(user_id, session: Session):
    conversations_in_db = session.scalars(
        select(Conversations).where(Conversations.user_id == user_id)
    ).all()

    if len(conversations_in_db) == 0:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Conversation Not Found"
        )

    return conversations_in_db


def delete_conversation_in_db(conversation_id, user_id, session: Session):
    conversation_in_db = session.scalar(
        select(Conversations).where(
            Conversations.id == conversation_id, Conversations.user_id == user_id
        )
    )

    if not conversation_in_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Conversation Not Found"
        )

    session.delete(conversation_in_db)
    session.commit()


def get_user_messages(conversation_id, session: Session):
    messages = (
        session.execute(
            select(Messages)
            .where(Messages.conversation_id == conversation_id)
            .order_by(Messages.created_at.desc())
            .limit(10)
        )
        .scalars()
        .all()
    )

    history = []

    for message in messages:
        history.append({"role": message.role, "content": message.content})

    history.reverse()
    return history


def make_embedding(question: str):
    question_embedding = model.encode(question)

    return question_embedding.tolist()


def get_chunks(question: str, document_id: str, session: Session):
    question_embedding = make_embedding(question)

    chunks = (
        session.execute(
            select(DocumentsChunks)
            .where(DocumentsChunks.document_id == document_id)
            .order_by(DocumentsChunks.embedding.cosine_distance(question_embedding))
            .limit(5)
        )
        .scalars()
        .all()
    )

    document_context = ""

    for chunk in chunks:
        document_context += chunk.chunk_text + "\n\n"

    return document_context


def make_question(document_context, message_history, question):
    messages = [
        {
            "role": "system",
            "content": "Você é um assistente que responde perguntas com base "
            "exclusivamente no contexto dos documentos fornecidos.",
        },
        *message_history,
        {
            "role": "user",
            "content": f"Contexto do documento: {document_context} Pergunta: {question}",
        },
    ]

    return messages


def ask_question(messages):
    client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b", messages=messages
    )

    return response.choices[0].message.content


def add_messages_in_db(input, output, session, conversation_id):

    session.add(
        Messages(
            conversation_id=conversation_id,
            role="user",
            content=input,
        )
    )

    session.add(
        Messages(
            conversation_id=conversation_id,
            role="assistant",
            content=output,
        )
    )

    session.commit()
