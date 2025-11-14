import json
from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session

from database import get_db
from services import ProcedureService

router = APIRouter()

@router.post("/")
async def multi_media_chat(
    text: Optional[str] = Form(None),
    audio_files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    if not text and not audio_files:
        raise HTTPException(status_code=400, detail="Phải gửi ít nhất text hoặc audio file")
    
    final_texts = []
    if text:
        final_texts.append(text)
    
    if audio_files:
        for audio_file in audio_files:
            audio_bytes = await audio_file.read()
            # Gọi service xử lý audio → text
            audio_text = ChatService.multiMediaInput(audio_file_bytes=audio_bytes)
            final_texts.append(audio_text)