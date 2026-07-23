from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.conversation.models import Conversations
from app.document.models import Documents


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
