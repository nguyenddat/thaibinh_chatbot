import os
import json
from concurrent.futures import ThreadPoolExecutor
import requests
from typing import Dict, Any, Optional

BASE_URL = os.environ.get("API_BASE_URL", "https://chatbot-tb-back.ript.vn/api/chat")

GUARDRAIL_ENDPOINT = f"{BASE_URL}/guardrail"
ANALYSIS_ENDPOINT = f"{BASE_URL}/analysis"
CHAT_CORE_ENDPOINT = os.environ.get("CHAT_ENDPOINT", f"{BASE_URL}/")

TIMEOUT = 20
FIXED_BLOCKED_REPLY = {
    "result": "blocked",
    "status": 200,
    "output": {
        "user_answer": False,
        "response": [
            {
                "type": "text",
                "content": "Mình không thể xử lý yêu cầu này do không phù hợp với chính sách của hệ thống. Bạn vui lòng hỏi nội dung khác nhé!",
                "recommendations": []
            }
        ],
    },
}

def call_guardrail(question: str, chat_history: Optional[list]) -> Dict[str, Any]:
    payload = {"question": question, "chat_history": chat_history}
    r = requests.post(GUARDRAIL_ENDPOINT, json=payload, timeout=TIMEOUT)
    r.raise_for_status()

    print(f"[GUARDRAIL] --> {r.json()['verified']}")
    return r.json()

def call_analysis(question: str, chat_history: Optional[list]) -> Dict[str, Any]:
    payload = {"question": question, "chat_history": chat_history}
    r = requests.post(ANALYSIS_ENDPOINT, json=payload, timeout=TIMEOUT)
    r.raise_for_status()

    print(f"[ANALYSIS] --> {r.json()['intent']}")
    return r.json()

def call_chat_core_from_analysis(analysis_resp: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "question": analysis_resp.get("question"),
        "intent": analysis_resp.get("intent"),
        "tasks": analysis_resp.get("tasks", []),
        "analysis_method": analysis_resp.get("analysis_method"),
        "analysis_params": analysis_resp.get("analysis_params", []),
    }
    r = requests.post(CHAT_CORE_ENDPOINT, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def test_flow(question: str, chat_history: Optional[list] = None) -> Dict[str, Any]:
    chat_history = chat_history or []

    with ThreadPoolExecutor(max_workers=2) as ex:
        future_guard = ex.submit(call_guardrail, question, chat_history)
        future_analysis = ex.submit(call_analysis, question, chat_history)

        # Wait both to finish (they run in parallel in threads)
        guardrail_result = None
        analysis_result = None

        try:
            guardrail_result = future_guard.result(timeout=TIMEOUT + 1)
        except Exception as e:
            print("Guardrail call failed:", e)
            return {"error": "guardrail_failed", "details": str(e)}

        try:
            analysis_result = future_analysis.result(timeout=TIMEOUT + 1)
        except Exception as e:
            # If analysis fails, we could still decide to block or return error
            print("Analysis call failed:", e)
            return {"error": "analysis_failed", "details": str(e)}

    # 1) If guardrail denies -> immediate fixed reply
    if not guardrail_result.get("verified", True):
        return FIXED_BLOCKED_REPLY

    # 2) If analysis intent == more_information -> return its recommendations
    if analysis_result.get("intent") == "more_information":
        recs = analysis_result.get("recommendations", [])
        return {
            "result": "need_more_info",
            "status": 200,
            "output": {
                "user_answer": False,
                "response": [
                    {
                        "type": "text",
                        "content": "Mình cần thêm một vài thông tin nữa để hỗ trợ bạn chính xác hơn. Bạn hãy chọn hoặc cung cấp thêm nội dung ở dưới nhé.",
                        "recommendations": recs,
                    }
                ],
            },
        }

    # 3) Normal -> forward full analysis response to chat-core
    chat_resp = call_chat_core_from_analysis(analysis_result)

    # Normalize / adapt return shape as you need
    return {
        "result": "successfully",
        "status": 200,
        "analysis": analysis_result,
        "chat_core_response": chat_resp,
    }

if __name__ == "__main__":
    question = input("Nhập câu hỏi của bạn:\n")
    history = []

    out = test_flow(question, history)
    print(json.dumps(out, ensure_ascii=False, indent=2))