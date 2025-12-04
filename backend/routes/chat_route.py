from typing import List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Body

from database import get_db
from utils.state import Intent
from services import ChatService, LLMService, ProcedureService

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

class GuardrailRequestBody(BaseModel):
    question: str

class AnalysisRequestBody(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]] = None

@router.post("/guardrail")
def verify_question(req: GuardrailRequestBody):
    response = ChatService.guardrail(req.question)
    response["question"] = req.question
    return response


@router.post("/analysis")
def analysis_question(req: AnalysisRequestBody):
    chat_history = req.chat_history or []
    crop = min(6, len(chat_history))
    chat_history = ChatService.format_chat_history(chat_history[-crop:])

    response = ChatService.analysis(req.question, chat_history)
    response["question"] = req.question
    return response
    
class ChatRequestBody(BaseModel):
    question: str
    intent: Intent
    tasks: Optional[List[str]] = None
    analysis_method: Optional[str] = None
    analysis_params: Optional[List[str]] = None

@router.post("/")
def chat(
    chat_request: ChatRequestBody = Body(...),
    db: Session = Depends(get_db)
):
    intent = chat_request.intent
    if intent == Intent.WELCOME:
        task = "welcome"
        params = {"question": chat_request.question,
                  "procedure_descriptions": ProcedureService.getRandomProcedures(db)}
        response = LLMService.get_chat_completion(task, params)
        
        final_response = response["response"]
        recommendations = response["recommendations"]
    
    else:
        # Params cho query db
        analysis_params = chat_request.analysis_params or []
        default_params = ["ma_thu_tuc", "ten_thu_tuc", "duong_dan", "co_quan_thuc_hien", "le_phi", "thoi_han_giai_quyet"]
        params = list(set(analysis_params + default_params))

        # Luồng chạy song song
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(ChatService.get_procedure_info, task, params, db)
                for task in chat_request.tasks
            ]
            for future in as_completed(futures):
                results.append(future.result())
        
        # Tổng hợp bước cuối
        task = "aggregate"
        params = {"question": chat_request.question, "procedures": results,  "analysis_method": chat_request.analysis_method}
        response = LLMService.get_chat_completion(task, params)

        final_response = response["response"]
        recommendations = []

    return {
        "result": "successfully",
        "status": 200,
        "output": {
            "user_answer": False,
            "response": [
                {
                    "type": "text",
                    "content": final_response,
                    "recommendations": recommendations,
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

    audio_file_bytes = await audio_file.read()
    audio_text = LLMService.transcribe(audio_bytes=audio_file_bytes)
    print(f"{audio_file.filename} --> {audio_text}")

    return {
        "result": "successfully",
        "status": 200,
        "output": {"type": "text", "value": audio_text},
    }