from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.ocr_service import OCRService

router = APIRouter(prefix="/api/ocr", tags=["OCR"])

@router.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Must be an image file.")
        
    contents = await file.read()
    text = OCRService.extract_text(contents)
    
    return {
        "status": "success",
        "extracted_text": text
    }
