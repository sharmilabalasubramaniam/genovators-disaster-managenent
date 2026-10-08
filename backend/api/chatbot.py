from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from backend.database.db import get_db
from backend.models.models import User
from backend.api import deps
from backend.services.chatbot.chatbot_service import process_message

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

class ChatMessage(BaseModel):
    message: str
    case_vrn: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    category: str
    sources: List[str] = []
    data_used: bool = False

@router.post("/message", response_model=ChatResponse)
def handle_chat_message(
    chat_message: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    try:
        response = process_message(chat_message.message, chat_message.case_vrn, db, current_user)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
