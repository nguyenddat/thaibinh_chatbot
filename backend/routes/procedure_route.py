import json
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from services import ProcedureService

router = APIRouter()

@router.post("/")
async def postProcedureJson(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    results = []
    for file in files:
        if not file.filename.endswith(".json"):
            continue

        try:
            content = await file.read()
            data = json.loads(content)

            proc_record = ProcedureService.createByJsonFile(data, db)
            results.append({
                "id": proc_record.id,
                "filename": file.filename,
                "success": True,
                "ma_thu_tuc": proc_record.ma_thu_tuc
            })
        
        except Exception as err:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(err)
            })
    db.commit()
    return results