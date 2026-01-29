from typing import *

from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

class RewriteResponse(BaseModel):
    response: str = Field(..., description="Câu hỏi sau khi được viết lại")

rewrite_with_history_parser = PydanticOutputParser(pydantic_object=RewriteResponse)