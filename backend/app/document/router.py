from fastapi import APIRouter, UploadFile, Depends
from http import HTTPStatus
from pypdf import PdfReader
from io import BytesIO
from app.document.service import process_docs
from app.core.database import get_db
from app.document.models import Documents

router = APIRouter(prefix="/document", tags=["Document"])


@router.post("/upload_file", status_code=HTTPStatus.OK)
async def upload_file(file: UploadFile, session = Depends(get_db)):

    session.add(Documents(
        user_id=1,
        name=file.filename,
        extension='pdf'
    ))
    session.commit()

    content = await file.read()
    pdf = PdfReader(BytesIO(content))
    text = ''
    for page in pdf.pages:
        text += page.extract_text()

    process_docs(1, text, session)

    return {
        "Message": "File Saved"
    }