from fastapi import APIRouter, UploadFile, Depends, HTTPException
from http import HTTPStatus
from pypdf import PdfReader
from io import BytesIO
from sqlalchemy import select, delete
from app.document.service import process_docs
from app.core.database import get_db
from app.document.models import Documents, DocumentsChunks
from app.core.security import get_current_user


router = APIRouter(prefix="/document", tags=["Document"])


@router.post("/upload_file", status_code=HTTPStatus.OK)
async def upload_file(
    file: UploadFile, 
    session = Depends(get_db), 
    current_user = Depends(get_current_user)
    ):

    extensions = file.filename.split('.')

    new_document = Documents(
        user_id=current_user.id ,
        name=file.filename,
        extension=extensions[-1]
    )

    session.add(new_document)
    session.commit()
    session.refresh(new_document)

    content = await file.read()
    pdf = PdfReader(BytesIO(content))
    text = ''

    for page in pdf.pages:
        text += page.extract_text()

    process_docs(new_document.id, text, session)

    return {
        "Message": "File Saved"
    }


@router.delete("/delete_file", status_code=HTTPStatus.OK)
def delete_file(
    document_id: int,
    session = Depends(get_db), 
    current_user = Depends(get_current_user)
    ):

    document_in_db = session.scalar(select(Documents).where(
        Documents.id == document_id,
        Documents.user_id == current_user.id,
    ))

    if not document_in_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Document Not Found"
        )
    

    session.execute(delete(DocumentsChunks).where(
        DocumentsChunks.document_id == document_id,
        )
    )
    session.delete(document_in_db)
    session.commit()


    return {
        "Message": "File Deleted"
    }

@router.get("/delete_file", status_code=HTTPStatus.OK)
def delete_file(
    session = Depends(get_db), 
    current_user = Depends(get_current_user)
    ):

    documents_in_db = session.scalars(select(Documents).where(
        Documents.user_id == current_user.id
    )).all()

    return {
        "Documents": documents_in_db
    }