from typing import *

from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

class ProcedureResponse(BaseModel):
    procedure_id: str = Field(..., description="Thủ tục được chọn")

procedure_parser = PydanticOutputParser(pydantic_object=ProcedureResponse)