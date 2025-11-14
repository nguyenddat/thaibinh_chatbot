from typing import *

from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

class FunctionCallingResponse(BaseModel):
    """
    Function calling response schema.
    """
    procedure: str = Field(..., description="Một thủ tục đang được đề cập đến")
    procedure_params: List[str] = Field(..., description="Thông tin chi tiết của thủ tục")

agent_selector_parser = PydanticOutputParser(pydantic_object=FunctionCallingResponse)
