from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.conversation.service import (
    add_conversation_in_db,
    add_messages_in_db,
    ask_question,
    delete_conversation_in_db,
    get_chunks,
    get_user_messages,
    make_question,
    read_conversations_in_db,
)
from app.document.service import delete_file_in_db
from app.core.database import get_db
from app.core.security import get_current_user
from app.conversation.models import Messages
from app.conversation.schemas import (
    ConversationCreate, 
    QuestionRequest,
    PublicConversation
)
from app.core.limiter import limiter

router = APIRouter(prefix="/conversation", tags=["conversation"])


@router.post("", status_code=HTTPStatus.CREATED, response_model=PublicConversation)
@limiter.limit("60/minute")
def create_conversation(
    request: Request,
    data: ConversationCreate,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    new_conversation = add_conversation_in_db(
        user_id=current_user.id, document_id=data.document_id, session=session
    )

    return PublicConversation(
        id=new_conversation.id,
        title=new_conversation.title
    )


@router.get("", status_code=HTTPStatus.OK)
@limiter.limit("60/minute")
def read_conversation(
    request: Request,
    session: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):

    conversations_in_db = read_conversations_in_db(
        user_id=current_user.id, session=session
    )

    return {
    "Chats": [
        PublicConversation(
            id=chat.id,
            title=chat.title
        )
        for chat in conversations_in_db
    ]
}


@router.delete("/{conversation_id}/", status_code=HTTPStatus.OK)
@limiter.limit("60/minute")
def delete_conversation(
    request: Request,
    conversation_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    conversation_document_id = delete_conversation_in_db(
        conversation_id=conversation_id, user_id=current_user.id, session=session
    )

    delete_file_in_db(
        conversation_document_id,
        current_user.id,
        session
    )


@router.post("/question/", status_code=HTTPStatus.OK)
@limiter.limit("60/minute")
def user_question(
    request: Request,
    data: QuestionRequest,
    session: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):

    message_history = get_user_messages(data.conversation_id, session)
    document_context = get_chunks(data.question, data.conversation_id, session)
    messages = make_question(document_context, message_history, data.question)

    output = ask_question(messages)

    add_messages_in_db(data.question, output, session, data.conversation_id)

    return {"Message": output}


@router.get("/{chat_id}/messages")
@limiter.limit("60/minute")
def get_chat_messages(
    request: Request,
    chat_id: int,
    current_user = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    messages = session.scalars(
    select(Messages)
    .where(
        Messages.conversation_id == chat_id
    )
    .order_by(Messages.created_at.asc())
    ).all()

    return {
        "Messages": messages
    }