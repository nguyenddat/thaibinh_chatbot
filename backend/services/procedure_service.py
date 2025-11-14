import json
from typing import Dict

from sqlalchemy.orm import Session

from repositories import ProcedureRepository
from models.model_procedure import Procedure

class ProcedureService:
    @staticmethod
    def create(proc: Procedure, db: Session):
        return ProcedureRepository.create(proc, db)

    @staticmethod
    def createByJsonFile(data, db: Session):        
        ma_thu_tuc = data["ma_thu_tuc"]
        existing = db.query(Procedure).filter(Procedure.ma_thu_tuc == ma_thu_tuc).first()
        if existing:
            return ProcedureService.updateById(existing, data, db)
        else:
            new = Procedure(**data)
            return ProcedureService.create(new, db)

    @staticmethod
    def updateById(proc: Procedure, update_data: Dict[str, str], db: Session):
        for key, value in update_data.items():
            if hasattr(proc, key):
                setattr(proc, key, value)
        db.flush()
        return proc