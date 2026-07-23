from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.conversation.service import (
    add_conversation_in_db,
    delete_conversation_in_db,
    read_conversations_in_db,
)
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/conversation", tags=["conversation"])


@router.post("/create_conversation/", status_code=HTTPStatus.CREATED)
def create_conversation(
    document_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    add_conversation_in_db(
        user_id=current_user.id, document_id=document_id, session=session
    )

    return {"Message": "Chat created"}


@router.get("/read_conversation/", status_code=HTTPStatus.OK)
def read_conversation(
    session: Session = Depends(get_db), current_user=Depends(get_current_user)
):

    conversations_in_db = read_conversations_in_db(
        user_id=current_user.id, session=session
    )

    return {"Chats": conversations_in_db}


@router.delete("/delete_conversation/", status_code=HTTPStatus.OK)
def delete_conversation(
    conversation_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    delete_conversation_in_db(
        conversation_id=conversation_id, user_id=current_user.id, session=session
    )

    return {"Message": "Chat deleted"}
