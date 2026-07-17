from fastapi import APIRouter, UploadFile, File, HTTPException, Request
import os
from app.pdf import extract_text
from app.embedding import create_embeddings
from app.vector_db import store_chunks
from app.routes.auth import decode_token

router = APIRouter()

UPLOAD_ROOT = "uploads"

os.makedirs(UPLOAD_ROOT, exist_ok=True)


def get_user_upload_dir(user_id: str):
    user_dir = os.path.join(UPLOAD_ROOT, user_id)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir


def get_current_user(request: Request):
    auth = request.headers.get("authorization") or ""
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload.get("sub") or payload.get("email")

def clear_uploads(user_id: str):
    user_dir = get_user_upload_dir(user_id)
    for file in os.listdir(user_dir):
        file_path = os.path.join(user_dir, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

def clear_db():
    try:
        # Vector DB operations handled by vector_db module
        pass
    except Exception as e:
        print("DB operation error:", e)

def chunk_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

@router.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    user_id = get_current_user(request)
    user_dir = get_user_upload_dir(user_id)
    file_path = os.path.join(user_dir, file.filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    text = extract_text(file_path)
    chunks = chunk_text(text)
    embeddings = create_embeddings(chunks)

    store_chunks(chunks, embeddings, f"{user_id}/{file.filename}")

    return {
        "message": "uploaded",
        "file": file.filename,
        "user": user_id,
    }


@router.get("/files")
def get_files(request: Request):
    user_id = get_current_user(request)
    user_dir = get_user_upload_dir(user_id)
    if not os.path.exists(user_dir):
        return []
    return os.listdir(user_dir)


@router.delete("/files/{filename}")
def delete_file(request: Request, filename: str):
    user_id = get_current_user(request)
    user_dir = get_user_upload_dir(user_id)
    path = os.path.join(user_dir, filename)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(path)

    return {"message": "Deleted"}