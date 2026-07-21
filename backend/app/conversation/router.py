from fastapi import APIRouter, HTTPException, Depends
from http import HTTPStatus
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.document.models import Documents
from app.conversation.models import Conversations

router = APIRouter(prefix="/conversation", tags=["conversation"])

@router.post("/create_conversation/", status_code=HTTPStatus.CREATED)
def create_conversation(
    documnet_id: int,
    session: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
    ):

    document_in_db = session.scalar(
            select(Documents).where(
                Documents.id == documnet_id,
                Documents.user_id == current_user.id
                )
        )
    
    new_conversation = Conversations(
        user_id= current_user.id,
        document_id=documnet_id,
        title=document_in_db.name,
    )

    session.add(new_conversation)
    session.commit()

    return{"Message": "Chat created"}


@router.post("/read_conversation/", status_code=HTTPStatus.OK)
def read_conversation(
    session: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
    ):

    conversations_in_db = session.scalars(
            select(Conversations).where(
                Conversations.user_id == current_user.id
                )
        ).all()

    return{"Chats": conversations_in_db}


@router.delete("/delete_conversation/", status_code=HTTPStatus.OK)
def delete_conversation(
    conversation_id: int,
    session: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
    ):

    conversation_in_db = session.scalar(
                select(Conversations).where(
                    Conversations.id == conversation_id,
                    Conversations.user_id == current_user.id
                    )
            )

    if not conversation_in_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="Conversation Not Found"
            )

    session.delete(conversation_in_db)
    session.commit()

    return{"Message": "Chat deleted"}

