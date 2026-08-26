from http import HTTPStatus
from pathlib import Path

from sqlalchemy import select

from app.auth.models import Users
from app.document.models import Documents, DocumentsChunks

ASSETS_DIR = Path(__file__).parent / "assets"


def test_upload_file_creates_document_and_chunks(
    client_override, access_token, refresh_token, session, monkeypatch
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)
    monkeypatch.setattr(
        "app.document.service.model.encode", lambda _: [0.0] * 384
    )

    with open(ASSETS_DIR / "sample.pdf", "rb") as f:
        response = client_override.post(
            "document/",
            files={"file": ("sample.pdf", f, "application/pdf")},
        )

    assert response.status_code == HTTPStatus.OK

    document_in_db = session.scalar(select(Documents))
    assert document_in_db is not None
    document_chunks = session.scalars(
        select(DocumentsChunks).where(DocumentsChunks.document_id == document_in_db.id)
    ).all()

    assert document_in_db.name == "sample"
    assert document_in_db.extension == "pdf"
    assert document_chunks


def test_delete_file_success(
    client_override, access_token, refresh_token, session, add_document_in_db
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)
    session.add(
        DocumentsChunks(
            document_id=add_document_in_db.id,
            chunk_index=0,
            chunk_text="Test document chunk",
            embedding=[0.0] * 384,
        )
    )
    session.commit()

    response = client_override.delete(
        "document/", params={"document_id": int(add_document_in_db.id)}
    )

    assert response.status_code == HTTPStatus.OK

    document_in_db = session.scalar(select(Documents))
    document_chunks = session.scalars(select(DocumentsChunks)).all()

    assert document_in_db is None
    assert document_chunks == []


def test_delete_file_not_found(
    client_override, access_token, refresh_token, session, add_document_in_db
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    response = client_override.delete(
        "document/", params={"document_id": 0}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Document not found"}

    document_in_db = session.scalars(select(Documents)).all()

    assert len(document_in_db) == 1


def test_delete_file_rejects_document_owned_by_another_user(
    client_override, access_token, refresh_token, session
):
    session.add(
        Users(
            username="another-user",
            email="another@example.com",
            password_hash="unused",
        )
    )
    session.commit()
    another_user = session.scalar(
        select(Users).where(Users.email == "another@example.com")
    )
    session.add(
        Documents(
            user_id=another_user.id,
            name="private document",
            extension="pdf",
        )
    )
    session.commit()
    private_document = session.scalar(
        select(Documents).where(Documents.name == "private document")
    )

    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)
    response = client_override.delete(
        "document/", params={"document_id": private_document.id}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Document not found"}
    assert session.get(Documents, private_document.id) is not None


def test_delete_file_requires_authentication(client_override, add_document_in_db):
    response = client_override.delete(
        "document/", params={"document_id": add_document_in_db.id}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}
