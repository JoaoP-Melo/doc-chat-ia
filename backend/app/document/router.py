from http import HTTPStatus

from fastapi import APIRouter, Depends, UploadFile

from app.core.database import get_db
from app.core.security import get_current_user
from app.document.service import (
    add_documents_in_db,
    delete_file_in_db,
    extract_file_text,
    get_file_extension,
    get_files_in_db,
    process_docs,
)
from app.core.limiter import limiter

router = APIRouter(prefix="/document", tags=["Document"])


@router.post("", status_code=HTTPStatus.OK)
@limiter.limit("60/minute")
async def upload_file(
    file: UploadFile, session=Depends(get_db), current_user=Depends(get_current_user)
):
    extension = get_file_extension(file.filename)

    new_document = add_documents_in_db(
        user_id=current_user.id,
        file_name=extension[0],
        file_extension=extension[-1],
        session=session,
    )

    text = await extract_file_text(file=file)

    process_docs(documento_id=new_document.id, file_text=text, session=session)



@router.delete("", status_code=HTTPStatus.OK)
@limiter.limit("60/minute")
def delete_file(
    document_id: int, session=Depends(get_db), current_user=Depends(get_current_user)
):
    delete_file_in_db(document_id=document_id, user_id=current_user.id, session=session)

