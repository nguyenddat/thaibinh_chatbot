from typing import *

from pydantic import BaseModel
from langchain_core.output_parsers import PydanticOutputParser

class AggregateResponse(BaseModel):
    response: str

aggregate_response_parser = PydanticOutputParser(pydantic_object=AggregateResponse)