from typing import List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from core import setting
from database import get_db
from utils.state import Intent
from services import ChatService, LLMService, ProcedureService

router = APIRouter()
class GuardrailRequestBody(BaseModel):
    text: str
    chat_history: Optional[List[Dict[str, str]]] = None

@router.post("/")
@router.post("")
def full_chat(req: GuardrailRequestBody, db: Session = Depends(get_db)):
    chat_history = req.chat_history or []
    crop = min(6, len(chat_history))
    chat_history = ChatService.format_chat_history(chat_history[-crop:])

    # Gọi song song cả guardrail và analysis
    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_map = {
            executor.submit(ChatService.guardrail, req.text, chat_history): "guardrail",
            executor.submit(ChatService.rewrite_with_history, req.text, chat_history): "rewrite",
        }

        results = {}
        for future in as_completed(future_map):
            key = future_map[future]
            results[key] = future.result()
    rewrite_result = results["rewrite"]
    guardrail_result = results["guardrail"]
    
    if guardrail_result["verified"] == False:
        content = (
            f"Câu hỏi '{req.text}' của bạn không hợp lệ. Vui lòng nhập lại câu hỏi!",
            "\n\n**Tìm hiểu thêm tại Cổng Dịch vụ công Quốc gia:** \
            # [https://dichvucong.gov.vn](https://dichvucong.gov.vn/p/home/dvc-trang-chu.html)"
        )
        recommendations = []
    
    else:
        # Phân tích câu hỏi
        analysis_response = ChatService.analysis(rewrite_result["response"])
        
        # Nếu cần thêm
        if analysis_response["intent"] == Intent.MORE_INFORMATION:
            response = ChatService.ask_again(req.text, "\n".join(analysis_response["recommendations"]))                    
            content = response["response"]
            recommendations = analysis_response["recommendations"]
        
        elif analysis_response["intent"] == Intent.WELCOME:
            response = ChatService.welcome(req.text, ProcedureService.getRandomProcedures(db))                    
            content = response["response"]
            recommendations = response["recommendations"]
        
        else:
            # Params cho query db
            analysis_params = analysis_response["analysis_params"] or []
            default_params = ["ma_thu_tuc", "ten_thu_tuc", "linh_vuc_thuc_hien", "duong_dan", "co_quan_thuc_hien",
            "le_phi", "thoi_han_giai_quyet", "doi_tuong_thuc_hien", "can_cu_phap_ly"]
            params = list(set(analysis_params + default_params))

            # Luồng chạy song song
            results = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(ChatService.get_procedure_info, task, params, db)
                    for task in analysis_response["tasks"]
                ]
                for future in futures:
                    results.append(future.result())
            
            # Tổng hợp bước cuối
            task = "aggregate"
            procedures = "\n".join(results)
            params = {"question": req.text, "procedures": procedures,  "analysis_method": analysis_response["analysis_method"]}
            response = LLMService.get_chat_completion(task, params)
            
            content = response["response"]
            recommendations = []
    
    content += "\n\n**Tìm hiểu thêm tại Cổng Dịch vụ công Quốc gia:** \
    [https://dichvucong.gov.vn](https://dichvucong.gov.vn/p/home/dvc-trang-chu.html)"
    
    return {
        "result": "successfully",
        "status": 200,
        "output": {
            "user_answer": False,
            "response": [
                {
                    "type": "text",
                    "content": content,
                    "recommendations": recommendations
                }
            ]
        }
    }


@router.post("/stt")
async def stt(
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content_type = audio_file.content_type
    ext = audio_file.filename.split(".")[-1].lower()
    if content_type not in setting.allowed_mimes and ext not in setting.allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported audio type: {content_type}")

    audio_file_bytes = await audio_file.read()
    audio_text = LLMService.transcribe(audio_bytes=audio_file_bytes)
    print(f"{audio_file.filename} --> {audio_text}")

    return {
        "result": "successfully",
        "status": 200,
        "output": {"type": "text", "value": audio_text},
    }