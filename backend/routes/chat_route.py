from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from services import ChatService

router = APIRouter()

@router.post("/")
async def multi_media_chat(
    text: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(default=None),
    chat_history: Optional[List[Dict[str, str]]] = Body(default=[]),
    db: Session = Depends(get_db)
):
    if not text and not audio_file:
        raise HTTPException(status_code=400, detail="Phải gửi ít nhất text hoặc audio file")
    
    final_texts = []
    if text:
        final_texts.append(text)
    
    if audio_file and audio_file.filename:
        audio_bytes = await audio_file.read()
        audio_text = ChatService.multiMediaInput(audio_file_bytes=audio_bytes)
        print(f"{audio_file.filename} --> {audio_text}")
        final_texts.append(audio_text)
    
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

@router.post("/stream")
async def multi_media_chat_stream(
    text: Optional[str] = Form(None),
    audio_file: Optional[List[UploadFile]] = File(default=None),
    chat_history: Optional[List[Dict[str, str]]] = Body(default=[]),
    db: Session = Depends(get_db)
):
    if not text and not audio_file:
        raise HTTPException(status_code=400, detail="Phải gửi ít nhất text hoặc audio file")
    
    final_texts = []
    if text:
        final_texts.append(text)
    
    if audio_file:
        audio_bytes = await audio_file.read()
        audio_text = ChatService.multiMediaInput(audio_file_bytes=audio_bytes)
        final_texts.append(audio_text)
    
    crop = min(6, len(chat_history))
    chat_history_request = chat_history[-crop:]
    chat_history_format = ChatService.formatChatHistory(chat_history_request)

    return StreamingResponse(
        ChatService.generateStream(ChatService.chat("\n".join(final_texts), chat_history_format, db)), media_type="text/plain"
    )