from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import os
import uuid

router = APIRouter(prefix="/api/uploads", tags=["Uploads"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    ext = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "success", "url": f"http://127.0.0.1:8000/api/uploads/{filename}"}

@router.get("/{filename}")
async def get_file(filename: str):
    path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(path):
        return FileResponse(path)
    return {"status": "error", "message": "File not found"}
