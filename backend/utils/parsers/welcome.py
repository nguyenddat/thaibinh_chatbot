from typing import *

from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

class WelcomeResponse(BaseModel):
    """
    Function calling response schema.
    """
    response: str = Field(..., description="Phản hồi")
    recommendations: List[str] = Field(..., description="Gợi ý câu hỏi")

welcome_parser = PydanticOutputParser(pydantic_object=WelcomeResponse)
