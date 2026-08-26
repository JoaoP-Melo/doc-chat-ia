from http import HTTPStatus

from sqlalchemy import select

from app.conversation.models import Conversations


def test_create_conversation_success(
    client_override, access_token, refresh_token, session, add_document_in_db
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    response = client_override.post(
        "conversation/",
        json={"document_id": add_document_in_db.id},
    )

    assert response.status_code == HTTPStatus.CREATED

    conversation_in_db = session.scalar(select(Conversations))

    assert conversation_in_db is not None
    assert response.json() == {
        "id": conversation_in_db.id,
        "title": add_document_in_db.name,
    }


def test_read_conversation_success(
    client_override, access_token, refresh_token, session, add_conversation_in_db
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    response = client_override.get("conversation/")

    assert response.status_code == HTTPStatus.OK

    conversation_in_db = session.scalars(select(Conversations)).all()

    assert len(conversation_in_db) == 1


def test_read_conversation_returns_empty_list(
    client_override, access_token, refresh_token, session
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    response = client_override.get("conversation/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"Chats": []}


def test_delete_conversation_success(
    client_override, access_token, refresh_token, session, add_conversation_in_db
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    response = client_override.delete(f"conversation/{add_conversation_in_db.id}/")

    assert response.status_code == HTTPStatus.OK

    conversation_in_db = session.scalar(select(Conversations))

    assert not conversation_in_db


def test_delete_conversation_not_found(
    client_override,
    access_token,
    refresh_token,
    session,
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    response = client_override.delete("conversation/0/")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Conversation not found"}

    conversation_in_db = session.scalar(select(Conversations))

    assert not conversation_in_db


def test_get_chat_messages_success(
    client_override, access_token, refresh_token, add_messages_in_db
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    conversation_id = add_messages_in_db[0].conversation_id
    response = client_override.get(f"conversation/{conversation_id}/messages")

    assert response.status_code == HTTPStatus.OK
    assert [
        {
            "id": message["id"],
            "conversation_id": message["conversation_id"],
            "role": message["role"],
            "content": message["content"],
        }
        for message in response.json()["Messages"]
    ] == [
        {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "role": message.role,
            "content": message.content,
        }
        for message in add_messages_in_db
    ]
