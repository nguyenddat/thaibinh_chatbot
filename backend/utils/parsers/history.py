from typing import *

from pydantic import BaseModel
from langchain_core.output_parsers import PydanticOutputParser

class HistoryResponse(BaseModel):
    question: str
    response: str

history_response_parser = PydanticOutputParser(pydantic_object=HistoryResponse)