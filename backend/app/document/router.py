from http import HTTPStatus
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import delete, select

from app.core.database import get_db
from app.core.security import get_current_user
from app.document.models import Documents, DocumentsChunks
from app.document.service import (
    process_docs, 
    get_file_extension, 
    add_documents_in_db,
    extract_file_text,
    delete_file_in_db,
    get_files_in_db
)

router = APIRouter(prefix="/document", tags=["Document"])


@router.post("/upload_file", status_code=HTTPStatus.OK)
async def upload_file(
    file: UploadFile, session=Depends(get_db), current_user=Depends(get_current_user)
):
    extension = get_file_extension(file.filename)

    new_document = add_documents_in_db(
        user_id=current_user.id,
        file_name=file.filename,
        file_extension=extension,
        session=session
    )

    text = await extract_file_text(file=file)

    process_docs(documento_id=new_document.id, file_text=text, session=session)

    return {"Message": "File Saved"}


@router.delete("/delete_file", status_code=HTTPStatus.OK)
def delete_file(
    document_id: int, session=Depends(get_db), current_user=Depends(get_current_user)
):
    delete_file_in_db(
        document_id=document_id,
        user_id=current_user.id,
        session=session
    )

    return {"Message": "File Deleted"}


@router.get("/delete_file", status_code=HTTPStatus.OK)
def read_files(session=Depends(get_db), current_user=Depends(get_current_user)):
    documents_in_db = get_files_in_db(
        user_id=current_user.id,
        session=session)

    return {"Documents": documents_in_db}
