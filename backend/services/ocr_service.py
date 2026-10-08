import io
import pytesseract
from PIL import Image
import os

class OCRService:
    @staticmethod
    def extract_text(image_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Attempt real OCR using pytesseract
            text = pytesseract.image_to_string(image)
            if text and text.strip():
                return text.strip()
        except Exception as e:
            print(f"OCR warning: {e}")
            
        # Fallback 1: Exif data (often empty, but we can try)
        try:
            image = Image.open(io.BytesIO(image_bytes))
            info = image.getexif()
            if info:
                return f"Extracted from EXIF metadata: {str(info)}"
        except Exception:
            pass
            
        # Fallback 2: Basic strings extraction from bytes
        # Extract readable ascii characters longer than 4 chars
        import re
        ascii_strings = re.findall(b'[a-zA-Z0-9 ]{5,}', image_bytes)
        if ascii_strings:
            return "Extracted binary strings: " + ", ".join([s.decode('ascii', errors='ignore') for s in ascii_strings[:10]])
            
        return "No text could be extracted."
