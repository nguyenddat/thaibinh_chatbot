from dataclasses import dataclass
from typing import List, Optional, Literal

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, \
    PointStruct, Filter, FieldCondition, MatchValue, MatchAny, \
    SearchParams

from core import setting, openai_embeddings
from .data_models import QdrantDocument

@dataclass
class QdrantService:
    
    collection_name: str
    vector_size: int
    distance: Distance = Distance.COSINE
    recreate: bool = False
    
    def __post_init__(self):
        self.client = QdrantClient(url=setting.qdrant_url)
        self._ensure_collection()
    
    def insert_chunks(self, documents: List[QdrantDocument], embeddings: List[List[float]]):
        if len(documents) != len(embeddings):
            raise ValueError("Số lượng documents và embeddings phải bằng nhau.")
        
        points: List[PointStruct] = []
        for doc, embedding in zip(documents, embeddings):
            payload = doc.model_dump(exclude={"id"})
            points.append(
                PointStruct(
                    id=doc.id,
                    vector=embedding,
                    payload=payload,
                )
            )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        return {"status": "inserted", "points": len(points)}
    
    def search(self, query: str, top_k: int = 10):
        query_embedding = openai_embeddings.embed_query(query)
        
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k,
            search_params=SearchParams(hnsw_ef=128),
        )
        return [
            {
                "score": r.score,
                "content": r.payload.get("content", ""),
            }
            for r in results.points
        ]
    
    def _ensure_collection(self):
        exists = self.client.collection_exists(self.collection_name)

        if exists:
            if not self.recreate:
                return
            self.client.delete_collection(self.collection_name)

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=self.distance,
            ),
        )
        
qdrant_service = QdrantService(
    collection_name=setting.qdrant_collection_name,
    vector_size=1024,
    distance=Distance.COSINE,
    recreate=False,
)