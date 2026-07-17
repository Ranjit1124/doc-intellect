import os
import tempfile

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from app.embedding import create_embeddings
from app.pdf import extract_text
from app.routes.auth import decode_token
from app.vector_db import store_chunks

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

    if isinstance(payload, dict) and "user" in payload:
        payload = payload["user"]

    return payload


def clear_uploads(user_id: str):
    user_dir = get_user_upload_dir(user_id)
    for file in os.listdir(user_dir):
        file_path = os.path.join(user_dir, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


def clear_db():
    try:
        pass
    except Exception as exc:
        print("DB operation error:", exc)


def chunk_text(text, chunk_size=500):
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


@router.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    payload = get_current_user(request)
    user_id = payload.get("id") or payload.get("sub") or payload.get("email")
    user_dir = get_user_upload_dir(str(user_id))

    original_name = os.path.basename(file.filename or "upload.pdf")
    safe_name = original_name
    counter = 1
    while os.path.exists(os.path.join(user_dir, safe_name)):
        name, ext = os.path.splitext(original_name)
        safe_name = f"{name}_{counter}{ext}"
        counter += 1

    file_path = os.path.join(user_dir, safe_name)

    content = await file.read()
    with open(file_path, "wb") as handle:
        handle.write(content)

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            temp_path = tmp.name

        text = extract_text(temp_path)
        chunks = chunk_text(text)
        embeddings = create_embeddings(chunks)
        store_chunks(chunks, embeddings, f"{user_id}/{safe_name}")
    except Exception as exc:
        print(f"Document indexing failed, but upload was saved: {exc}")
    finally:
        if "temp_path" in locals() and os.path.exists(temp_path):
            os.remove(temp_path)

    return {
        "message": "uploaded",
        "file": safe_name,
        "user": user_id,
    }


@router.get("/files")
def get_files(request: Request):
    payload = get_current_user(request)
    user_id = payload.get("id") or payload.get("sub") or payload.get("email")
    user_dir = get_user_upload_dir(str(user_id))
    if not os.path.exists(user_dir):
        return []

    return os.listdir(user_dir)


@router.delete("/files/{filename}")
def delete_file(request: Request, filename: str):
    payload = get_current_user(request)
    user_id = payload.get("id") or payload.get("sub") or payload.get("email")
    user_dir = get_user_upload_dir(str(user_id))
    path = os.path.join(user_dir, filename)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(path)

    return {"message": "Deleted"}