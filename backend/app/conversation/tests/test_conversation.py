from http import HTTPStatus

from sqlalchemy import select

from app.conversation.models import Conversations


def test_create_conversation_success(
    client_override, access_token, refresh_token, session, add_document_in_db
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    response = client_override.post(
        "conversation/create_conversation/",
        params={"document_id": add_document_in_db.id},
    )

    assert response.status_code == HTTPStatus.CREATED

    conversation_in_db = session.scalars(select(Conversations)).all()

    assert len(conversation_in_db) == 1


def test_read_conversation_success(
    client_override, access_token, refresh_token, session, add_conversation_in_db
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    response = client_override.get("conversation/read_conversation/")

    assert response.status_code == HTTPStatus.OK

    conversation_in_db = session.scalars(select(Conversations)).all()

    assert len(conversation_in_db) == 1


def test_read_conversation_not_found(
    client_override, access_token, refresh_token, session
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    response = client_override.get("conversation/read_conversation/")

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_conversation_success(
    client_override, access_token, refresh_token, session, add_conversation_in_db
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    response = client_override.delete(
        "conversation/delete_conversation/",
        params={"conversation_id": add_conversation_in_db.id},
    )

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

    response = client_override.delete(
        "conversation/delete_conversation/", params={"conversation_id": 0}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    conversation_in_db = session.scalar(select(Conversations))

    assert not conversation_in_db
