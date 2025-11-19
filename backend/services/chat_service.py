import requests
import os
from typing import Dict, Any, List

from io import BytesIO
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage

from core import llm
from utils.get_prompt import get_prompt_by_task
from services import ProcedureService
from utils.retriever import retriever
from utils.convert import convert_audio

class ChatService:
    @staticmethod
    def chat(question: str, chat_history: Any, db: Session):
        # Select agent
        agent_selector_params = {"question": question, "chat_history": chat_history}
        agent_selector_response = ChatService.getChatCompletion(
            task="agent_selector", 
            params = agent_selector_params)
        procedure = agent_selector_response["procedure"]
        procedure_params = agent_selector_response["procedure_params"]
        
        # Check
        if len(procedure) == 0:
            task = "welcome"
            params = {"procedure_descriptions": ProcedureService.getRandomProcedures(db),
                      "question": procedure}

        else:
            docs = retriever.retriever.invoke(procedure, config={"k": 5})
            docs = "\n".join([doc.page_content for doc in docs])
            task = "procedure"
            params = {"procedure_descriptions": docs,
                      "question": question}
        
        # Reponse
        response = ChatService.getChatCompletion(task, params)
        recommendations = response["recommendations"]
        if task == "welcome" or (task == "procedure" and response["procedure_id"] == ""):
            final_response = response["response"]
            return {"response": final_response, "recommendations": recommendations}

        procedure_id = int(response["procedure_id"])
        procedure_selected = ProcedureService.getById(procedure_id, db)
        final_response = ProcedureService.toString(procedure_selected, procedure_params)
        return {"response": final_response, "recommendations": recommendations}


    @staticmethod
    def multiMediaInput(audio_file_bytes: bytes = None, text: str = None) -> str:
        if text:
            return text
        if audio_file_bytes:
            processed_audio_bytes = convert_audio(audio_file_bytes)
            url = "https://api.openai.com/v1/audio/transcriptions"
            files = {
                "file": ("audio.wav", BytesIO(processed_audio_bytes), "audio/wav")
            }

            data = {
                "model": "whisper-1",
                "language": "vi"
            }

            headers = {
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
            }

            response = requests.post(url, headers=headers, data=data, files=files)

            if response.status_code != 200:
                raise Exception(f"Whisper error {response.status_code}: {response.text}")

            return response.json().get("text", "")
        raise ValueError("Phải gửi ít nhất text hoặc audio file")


    @staticmethod
    def getChatCompletion(task: str, params: Dict[str, str]):
        prompt, parser = ChatService.getPromptByTask(task=task)

        chain = prompt | llm | parser
        response = chain.invoke(params).dict()
        return response

    @staticmethod
    def getPromptByTask(task: str):
        return get_prompt_by_task(task)


    @staticmethod
    def formatChatHistory(chat_history: List[Dict[str, str]]) -> List:
        converted_chat_history = []
        for message in chat_history:
            if message.get("human") is not None:
                converted_chat_history.append(HumanMessage(content=message["human"]))
            if message.get("ai") is not None:
                converted_chat_history.append(AIMessage(content=""))

        return converted_chat_history
