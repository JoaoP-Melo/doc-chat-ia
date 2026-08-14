from http import HTTPStatus
from io import BytesIO

from fastapi import HTTPException
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.document.models import Documents, DocumentsChunks

model = SentenceTransformer("all-MiniLM-L6-v2")


def create_chunks(texto: str, len_chunk: int = 500, overlap: int = 100):
    start = 0

    while start < len(texto):
        fim = start + len_chunk

        yield texto[start:fim]

        start += len_chunk - overlap


def process_docs(documento_id: int, file_text: str, session: Session):
    for index, chunk in enumerate(create_chunks(file_text)):
        embedding = model.encode(chunk)

        session.add(
            DocumentsChunks(
                document_id=documento_id,
                chunk_index=index,
                chunk_text=chunk,
                embedding=embedding.tolist(),
            )
        )
    session.commit()


def get_file_extension(file_name: str):
    names = file_name.split(".")

    return names


def add_documents_in_db(user_id, file_name, file_extension, session: Session):
    new_document = Documents(user_id=user_id, name=file_name, extension=file_extension)

    session.add(new_document)
    session.commit()
    session.refresh(new_document)

    return new_document


async def extract_file_text(file):
    content = await file.read()
    pdf = PdfReader(BytesIO(content))
    text = ""

    for page in pdf.pages:
        text += page.extract_text()

    return text


def delete_file_in_db(document_id, user_id, session: Session):
    document_in_db = session.scalar(
        select(Documents).where(
            Documents.id == document_id,
            Documents.user_id == user_id,
        )
    )

    if not document_in_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Document Not Found"
        )

    session.execute(
        delete(DocumentsChunks).where(
            DocumentsChunks.document_id == document_id,
        )
    )
    session.delete(document_in_db)
    session.commit()


def get_files_in_db(user_id, session: Session):
    documents_in_db = session.scalars(
        select(Documents).where(Documents.user_id == user_id)
    ).all()

    if not documents_in_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Documents Not Found"
        )

    return documents_in_db
