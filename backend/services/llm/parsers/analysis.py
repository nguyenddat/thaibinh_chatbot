from typing import *

from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

from utils.state import Intent

class AnalysisResponse(BaseModel):
    intent: Intent = Field(..., description="Intent của câu hỏi")
    tasks: List[str] = Field(..., description="Tên các thủ tục độc lập với nhau")
    recommendations: List[str] = Field(..., description="Các câu hỏi gợi ý dựa trên câu hỏi người dùng và thủ tục chúng tôi cung cấp, tối đa 3 câu hỏi")
    analysis_method: Optional[str] = Field(..., description="Phương pháp phân tích, ví dụ: so sánh, tổng hợp, ...")
    analysis_params: Optional[List[str]] = Field(..., description="Các thông tin chi tiết của thủ tục cần phân tích")

analysis_parser = PydanticOutputParser(pydantic_object=AnalysisResponse)