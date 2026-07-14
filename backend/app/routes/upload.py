from fastapi import APIRouter, UploadFile, File, HTTPException
import os, time
from app.pdf import extract_text
from app.embedding import create_embeddings
from app.vector_db import store_chunks

router = APIRouter()

UPLOAD_DIR = "uploads"
DB_PATH = "chroma_db"

os.makedirs(UPLOAD_DIR, exist_ok=True)

def clear_uploads():
    for file in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

def clear_db():
    try:
        import chromadb
        client = chromadb.PersistentClient(path="chroma_db")
        # client.reset()
    except Exception as e:
        print("DB reset error:", e)

def chunk_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    text = extract_text(file_path)
    chunks = chunk_text(text)
    embeddings = create_embeddings(chunks)

    store_chunks(chunks, embeddings, file.filename)

    return {
        "message": "uploaded",
        "file": file.filename
    }
    
@router.get("/files")
def get_files():
    return os.listdir(UPLOAD_DIR)


@router.delete("/files/{filename}")
def delete_file(filename: str):
    path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(path)

    return {"message": "Deleted"}