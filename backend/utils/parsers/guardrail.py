from typing import *

from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

from utils.state import Intent

class GuardrailResponse(BaseModel):
    verified: bool = Field(..., description="True nếu câu hỏi hợp lệ, False nếu không")
    
    intent: Intent = Field(..., description="Intent của câu hỏi")
    tasks: List[str] = Field(..., description="Tên các thủ tục độc lập với nhau")
    analysis_method: Optional[str] = Field(..., description="Phương pháp phân tích, ví dụ: so sánh, tổng hợp, ...")
    analysis_params: Optional[List[str]] = Field(..., description="Các thông tin chi tiết của thủ tục cần phân tích")

guardrail_parser = PydanticOutputParser(pydantic_object=GuardrailResponse)