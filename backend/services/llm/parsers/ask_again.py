from typing import *

from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

from utils.state import Intent

class AskAgainResponse(BaseModel):
    response: str = Field(..., description="Nội dung câu trả lời cho người dùng")

ask_again_parser = PydanticOutputParser(pydantic_object=AskAgainResponse)