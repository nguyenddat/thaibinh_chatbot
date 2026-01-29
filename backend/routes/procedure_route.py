import json
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from core import openai_embeddings
from services.qdrant.data_models import QdrantDocument
from services import qdrant_service, ProcedureService

router = APIRouter()

@router.post("/")
async def postProcedureJson(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):  
    documents = []
    embeddings = []

    results = {"success": True, "success_files": [], "failed_files": []}
    for file in files:
        if not file.filename.endswith(".json"):
            continue
        
        # đọc file
        content = await file.read()
        data = json.loads(content)

        # thêm vào db
        proc_record = ProcedureService.createByJsonFile(data, db)
        if proc_record is None:
            results["failed_files"].append(file.filename)
            continue
        else:
            # thêm vào vector db
            document = QdrantDocument(
                content=f"{proc_record.id}: {proc_record.ten_thu_tuc}, lĩnh vực {proc_record.linh_vuc}, {proc_record.co_quan_thuc_hien} thực hiện."
            )
            embedding = openai_embeddings.embed_query(document.content)
            documents.append(document)
            embeddings.append(embedding)
            
            results["success_files"].append(file.filename)
    
    if results["success_files"]:    
        qdrant_service.insert_chunks(documents, embeddings)   
        db.commit()
    else:
        results["success"] = False
        
    return results