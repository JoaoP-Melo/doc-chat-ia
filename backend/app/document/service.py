from sentence_transformers import SentenceTransformer
from app.document.models import DocumentsChunks, Documents
model = SentenceTransformer("all-MiniLM-L6-v2")

def create_chunks(
    texto: str,
    len_chunk: int = 500,
    overlap: int = 100
):
    inicio = 0

    while inicio < len(texto):
        fim = inicio + len_chunk

        yield texto[inicio:fim]

        inicio += len_chunk - overlap


def process_docs(documento_id: int, text: str, session):
    for index, chunk in enumerate(create_chunks(text)):
        embedding = model.encode(chunk)

        session.add(DocumentsChunks(
            document_id=documento_id,
            chunk_index=index,
            chunk_text=chunk,
            embedding=embedding.tolist()
            )
        )
        session.commit()