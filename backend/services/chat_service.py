import io
from typing import Dict, Any

import librosa
from sqlalchemy.orm import Session
from omnilingual_asr.models.inference.pipeline import ASRInferencePipeline

from core import llm
from utils.get_prompt import get_prompt_by_task
from services import ProcedureService

pipe = ASRInferencePipeline(model_card="omniASR_CTC_7B")
class ChatService:
    @staticmethod
    def chat(question: str, chat_history: Any, db: Session):
        agent_selector_response = ChatService.getChatCompletion(
            task="agent_selector", 
            params = {
                "question": question,
                "chat_history": chat_history
            })
        procedure = agent_selector_response["procedure"]
        procedure_params = agent_selector_response["procedure_params"]

        # Nếu không hỏi đến procedure nào
        if len(procedure) == 0:
            for chunk in ChatService.getChatStream(
                task="welcome", 
                params={
                    "procedure_descriptions": ProcedureService.getRandomProcedures(),
                    "question": question,
                }):
                yield chunk
        
        else:
            docs = retriever.retriever.invoke(procedure, config={"k": 5})
            docs = "\n".join([doc.page_content for doc in docs])

            response = ChatService.getChatCompletion(
                task="procedure",
                params={
                    "procedure_descriptions": docs,
                    "question": procedure,
                })

            if response["procedure_id"] == "":
                return {"response": response["response"],
                        "recommendations": response["recommendations"]}
            else:
                procedure_id = response["procedure_id"]
                procedure_selected = ProcedureService.getById(procedure_id, db, procedure_params)
                response = {
                    "response": ProcedureService.toString(procedure_selected),
                    "recommendations": response["recommendations"],
                }


    @staticmethod
    def multiMediaInput(audio_file_bytes: bytes = None, text: str = None) -> str:
        if text:
            return text
        if audio_file_bytes:
            audio_buffer = io.BytesIO(audio_file_bytes)
            y, sr = librosa.load(audio_buffer, sr=16000)
            chunk_length_sec = 40
            chunk_size = chunk_length_sec * sr
            chunks = [y[i:i+chunk_size] for i in range(0, len(y), chunk_size)]
            lang_codes = ["vie_Latn"] * len(chunks)
            texts = pipe.transcribe(chunks, lang=lang_codes)
            return " ".join(texts)
        raise ValueError("Phải gửi ít nhất text hoặc audio file")

    @staticmethod
    def getChatCompletion(task: str, params: Dict[str, str]):
        prompt, parser = ChatService.getPromptByTask(task=task)

        chain = prompt | llm | parser
        response = chain.invoke(params).dict()
        return response

    @staticmethod
    def getChatStream(task: str, params: Dict[str, str]):
        prompt, parser = ChatService.getPromptByTask(task=task)

        chain = prompt | llm | parser
        for chunk in chain.stream(params):
            yield chunk

    @staticmethod
    def getPromptByTask(task: str):
        return get_prompt_by_task(task)