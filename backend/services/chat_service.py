import io
import json
from typing import Dict, Any, Generator, List

import librosa
import numpy as np
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage
from omnilingual_asr.models.inference.pipeline import ASRInferencePipeline

from core import llm
from utils.get_prompt import get_prompt_by_task
from services import ProcedureService
from utils.retriever import retriever
from utils.convert import convert_audio

pipe = ASRInferencePipeline(model_card="omniASR_CTC_7B")
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
                      "question": question}

        else:
            docs = retriever.retriever.invoke(procedure, config={"k": 5})
            docs = "\n".join([doc.page_content for doc in docs])
            task = "procedure"
            params = {"procedure_descriptions": docs,
                      "question": procedure}
        
        # Reponse
        response = ChatService.getChatCompletion(task, params)
        recommendations = response["recommendations"]
        if task == "welcome" or (task == "procedure" and response["procedure_id"] == ""):
            final_response = response["response"]
            return {"response": final_response, "recommendations": recommendations}

        procedure_id = int(response["procedure_id"])
        print(procedure_params)
        procedure_selected = ProcedureService.getById(procedure_id, db, procedure_params)
        
        final_response = ProcedureService.toString(procedure_selected)
        return {"response": final_response, "recommendations": recommendations}

    @staticmethod
    def chatStream(question: str, chat_history: Any, db: Session):
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
            full_text = " "
            recommendations = []
            for chunk in ChatService.getChatStream(
                task="welcome", 
                params={
                    "procedure_descriptions": ProcedureService.getRandomProcedures(db),
                    "question": question,
                }):
                try:
                    full_text = chunk.response
                    recommendations = chunk.recommendations
                    yield full_text
                except:
                    full_text = chunk
                    yield full_text
            yield json.dumps({"response": full_text, "recommendations": recommendations})
        
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
                response = response["response"]
                recommendations = response["recommendations"]
            else:
                procedure_id = response["procedure_id"]
                procedure_selected = ProcedureService.getById(procedure_id, db, procedure_params)
                
                response = ProcedureService.toString(procedure_selected)
                recommendations = response["recommendations"]
            
            full_text = " "
            for chunk in ChatService.split_into_chunks(response):
                full_text = chunk
                yield full_text

            yield json.dumps({"response": full_text, "recommendations": recommendations})
            
    @staticmethod
    def split_into_chunks(text: str, chunk_size: int = 200) -> Generator[str, None, None]:
        words = text.split()
        chunk = []
        char_count = 0
        for word in words:
            chunk.append(word)
            char_count += len(word) + 1
            if char_count >= chunk_size:
                yield " ".join(chunk)
                chunk = []
                char_count = 0
        if chunk:
            yield " ".join(chunk)

    @staticmethod
    def multiMediaInput(audio_file_bytes: bytes = None, text: str = None) -> str:
        if text:
            return text

        if audio_file_bytes:
            # audio_buffer = io.BytesIO(audio_file_bytes)
            # y, sr = librosa.load(audio_buffer, sr=16000)
            # y = ((y + 1.0) * 127.5).astype(np.uint8)

            y = convert_audio(audio_file_bytes)
            sr = 16000
            bytes_per_sample = 2

            chunk_length_sec = 40
            chunk_size = chunk_length_sec * sr * bytes_per_sample

            if len(y) <= chunk_size:
                chunks = [y]
            else:
                chunks = [
                    y[i:i+chunk_size]
                    for i in range(0, len(y), chunk_size)
                    if len(y[i:i+chunk_size]) > 0
                ]

            for c in chunks:
                print("Chunk:", len(c))  

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

    @staticmethod
    def generateStream(generation: Generator):
        try:
            chunk_count = 0
            last_answer = ""

            for chunk in generation:
                chunk_count += 1
                last_answer = chunk
                response_data = {
                    "type": "content",
                    "chunk_id": chunk_count,
                    "content": chunk,
                    "status": "streaming"        
                }
                yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
            
            final_data = {
                "type": "content",
                "chunk_id": chunk_count + 1,
                "content": last_answer,
                "status": "completed"
            }
            yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"

        except Exception as e:
            error_data = {
                "type": "error",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        finally:
            yield "event: close\ndata: {}\n\n"
    
    @staticmethod
    def formatChatHistory(chat_history: List[Dict[str, str]]) -> List:
        converted_chat_history = []
        for message in chat_history:
            if message.get("human") is not None:
                converted_chat_history.append(HumanMessage(content=message["human"]))
            if message.get("ai") is not None:
                converted_chat_history.append(AIMessage(content=""))

        return converted_chat_history
