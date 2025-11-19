from typing import List, Optional, Dict

from pydantic import BaseModel

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from services import ChatService

router = APIRouter()

ALLOWED_MIME = {
    "audio/webm",
    "video/webm",   # Android
    "audio/mp4",    # iOS Safari/Chrome
    "audio/m4a",    # iOS/Mac
    "audio/x-m4a",
    "audio/aac",
    "audio/mpeg",
    "audio/wav",
    "audio/mp3",
}

ALLOWED_EXT = {"webm", "mp4", "m4a", "aac"}

class ChatRequestBodyModel(BaseModel):
    text: Optional[str] = None
    chat_history: Optional[List[Dict[str, str]]] = []

@router.post("/")
async def multi_media_chat(
    chat_request: ChatRequestBodyModel = Body(...),
    db: Session = Depends(get_db)
):
    text = chat_request.text
    chat_history = chat_request.chat_history or []

    # When this route accepts JSON body (no file uploads), require `text` to be present
    if not text:
        raise HTTPException(status_code=400, detail="Phải gửi ít nhất text")

    final_texts = []
    final_texts.append(text)

    crop = min(6, len(chat_history))
    chat_history_request = chat_history[-crop:]

    question = "\n".join(final_texts)
    chat_history = ChatService.formatChatHistory(chat_history_request)

    response = ChatService.chat(question, chat_history, db)
    return {
        "result": "successfully",
        "status": 200,
        "output": {
            "user_answer": False,
            "response": [
                {
                    "type": "text",
                    "content": response["response"],
                    "recommendations": response["recommendations"],
                }
            ],
        },
    }


@router.post("/stt")
async def stt(
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content_type = audio_file.content_type
    ext = audio_file.filename.split(".")[-1].lower()
    if content_type not in ALLOWED_MIME and ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"Unsupported audio type: {content_type}")

    audio_bytes = await audio_file.read()
    audio_text = ChatService.multiMediaInput(audio_file_bytes=audio_bytes)
    print(f"{audio_file.filename} --> {audio_text}")

    return {
        "result": "successfully",
        "status": 200,
        "output": {"type": "text", "value": audio_text},
    }