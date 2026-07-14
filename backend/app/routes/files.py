from fastapi import APIRouter
from app.vector_db import delete_pdf
import os

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.get("/files")
def get_files():
    if not os.path.exists(UPLOAD_DIR):
        return []

    return os.listdir(UPLOAD_DIR)

@router.delete("/files/{filename}")
def remove_file(filename: str):

    path = os.path.join(UPLOAD_DIR, filename)

    if os.path.exists(path):
        os.remove(path)

    delete_pdf(filename)

    return {"message":"Deleted"}