from typing import List, Dict

from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage

from core import logger
from services import ProcedureService
from services.qdrant import qdrant_service
from services.llm.srv_llm import LLMService

class ChatService:
    @staticmethod
    def welcome(question: str, procedures: str):
        logger.info(f"[Welcome] question: {question}")
        
        task = "welcome"
        params = {"question": question, "procedure_descriptions": procedures}
        response = LLMService.get_chat_completion(task, params)
        
        logger.info(f"\t--> {response['response']}")
        return response
    
    @staticmethod
    def ask_again(question: str, procedures: str):
        logger.info(f"[AskAgain] question: {question}")
        
        task = "ask_again"
        params = {"question": question, "procedure_descriptions": procedures}
        response = LLMService.get_chat_completion(task, params)
        
        logger.info(f"\t--> {response['response']}")
        return response
    
    @staticmethod
    def rewrite_with_history(question: str, chat_history: str):
        logger.info(f"[Rewrite] question: {question}")
        
        task = "rewrite_with_history"
        params = {"question": question, "chat_history": chat_history}
        response = LLMService.get_chat_completion(task, params)
        
        logger.info(f"\t--> {response['response']}")
        return response
    
    @staticmethod
    def guardrail(question: str, chat_history: str):
        logger.info(f"[Guardrail] question: {question}")
        
        task = "guardrail"
        params = {"question": question, "chat_history": chat_history}
        response = LLMService.get_chat_completion(task, params)
        
        logger.info(f"\t--> {response['verified']}")
        return response
    
    @staticmethod
    def analysis(question: str):
        logger.info(f"[Analysis] question: {question}")
        
        # Lấy danh sách các thủ tục giống tên
        docs = qdrant_service.search(question, top_k=5)
        docs = "\n".join([doc["content"] for doc in docs])
        
        # Phân tích
        task = "analysis"
        params = {"question": question, "procedure_descriptions": docs}
        response = LLMService.get_chat_completion(task, params)
        
        logger.info(f"\t--> {response['intent']}")
        return response
    
    @staticmethod
    def get_procedure_info(question: str, query_params: List[str], db: Session):
        logger.info(f"[GetProcedureInfo] question: {question}, query_params: {query_params}")
        
        # Lấy danh sách các thủ tục giống tên
        docs = qdrant_service.search(question, top_k=5)
        docs = "\n".join([doc['content'] for doc in docs])
        logger.info(f"--> docs: \n{docs}")
        
        # Chọn thủ tục
        task = "procedure_select"
        params = {"procedure_descriptions": docs, "question": question}
        response = LLMService.get_chat_completion(task, params)
        procedure_id = response["procedure_id"]

        logger.info(f"\t--> {procedure_id}")
        # Nếu không có:
        if procedure_id == "":
            return f"Chúng tôi không tìm thấy thủ tục phù hợp với {question}."

        # Nếu có:
        else:
            procedure_selected = ProcedureService.getById(procedure_id, db)
            return ProcedureService.toString(procedure_selected, query_params)

    @staticmethod
    def format_chat_history(chat_history: List[Dict[str, str]]) -> List:
        converted_chat_history = []
        for message in chat_history:
            if message.get("human") is not None:
                converted_chat_history.append(HumanMessage(content=message["human"]))
            if message.get("ai") is not None:
                converted_chat_history.append(AIMessage(content=""))

        return converted_chat_history
