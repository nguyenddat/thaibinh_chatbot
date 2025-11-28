from typing import List, Dict

from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage

from utils.retriever import retriever
from services import ProcedureService
from services.llm_service import LLMService

class ChatService:
    @staticmethod
    def guardrail(question: str, chat_history: str):
        task = "guardrail"
        params = {"question": question, "chat_history": chat_history}
        response = LLMService.get_chat_completion(task, params)
        return response
    
    @staticmethod
    def analysis(question: str, chat_history: str):
        # Lấy danh sách các thủ tục giống tên
        docs = retriever.retriever.invoke(question, config={"k": 5})
        docs = "\n".join([doc.page_content for doc in docs])
        
        # Phân tích
        task = "analysis"
        params = {"question": question, "chat_history": chat_history, "procedure_descriptions": docs}
        response = LLMService.get_chat_completion(task, params)
        return response
    
    @staticmethod
    def get_procedure_info(question: str, query_params: List[str], db: Session):
        # Lấy danh sách các thủ tục giống tên
        docs = retriever.retriever.invoke(question, config={"k": 5})
        docs = "\n".join([doc.page_content for doc in docs])

        # Chọn thủ tục
        task = "procedure_select"
        params = {"procedure_descriptions": docs, "question": question}
        response = LLMService.get_chat_completion(task, params)
        procedure_id = response["procedure_id"]

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
