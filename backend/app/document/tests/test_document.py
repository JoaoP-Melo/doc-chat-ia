from http import HTTPStatus
from pathlib import Path
from sqlalchemy import select

from app.document.models import Documents, DocumentsChunks

ASSETS_DIR = Path(__file__).parent / "assets"

def test_upload_file_success(client_override, access_token, refresh_token, session):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    with open(ASSETS_DIR/ 'sample.pdf', "rb") as f:

        response = client_override.post(
            "document/upload_file/",
            files={"file": ("sample.pdf", f, "application/pdf")}
        )

    assert response.status_code == HTTPStatus.OK

    document_in_db = session.scalars(select(Documents)).all()

    assert len(document_in_db) == 1


def test_delete_file_success(
   client_override, 
   access_token, 
   refresh_token, 
   session,
   add_document_in_db
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    response = client_override.delete(
            "document/delete_file/",
            params={"document_id": int(add_document_in_db.id)}
        )
    
    assert response.status_code == HTTPStatus.OK
    
    document_in_db = session.scalars(select(Documents)).all()

    assert len(document_in_db) == 0


def test_delete_file_success(
   client_override, 
   access_token, 
   refresh_token, 
   session,
   add_document_in_db
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    response = client_override.delete(
            "document/delete_file/",
            params={"document_id": int(add_document_in_db.id) -1 }
        )
    
    assert response.status_code == HTTPStatus.NOT_FOUND
    
    document_in_db = session.scalars(select(Documents)).all()

    assert len(document_in_db) == 1


def test_read_file_success(
   client_override, 
   access_token, 
   refresh_token, 
   session,
   add_document_in_db
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    response = client_override.get(
            "document/read_file/"
        )
    
    assert response.status_code == HTTPStatus.OK
    
    document_in_db = session.scalars(select(Documents)).all()

    assert len(document_in_db) == 1


def test_read_file_success(
   client_override, 
   access_token, 
   refresh_token, 
   session,
):
    client_override.cookies.set("access_token", access_token)
    client_override.cookies.set("refresh_token", refresh_token)

    response = client_override.get(
            "document/read_file/"
        )
    
    assert response.status_code == HTTPStatus.NOT_FOUND
    
    document_in_db = session.scalars(select(Documents)).all()

    assert len(document_in_db) == 0