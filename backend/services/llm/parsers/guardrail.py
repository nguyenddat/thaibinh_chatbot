from typing import *

from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

class GuardrailResponse(BaseModel):
    verified: bool = Field(..., description="True nếu câu hỏi hợp lệ, False nếu không")
    
guardrail_parser = PydanticOutputParser(pydantic_object=GuardrailResponse)