import uuid

from pydantic import BaseModel, Field, ConfigDict

class QdrantDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="ID của point trong Qdrant"
    )
    
    content: str = Field(
        ..., description="Nội dung của point"
    )