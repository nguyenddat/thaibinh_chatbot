from sqlalchemy.orm import Session

from models.model_procedure import Procedure

class ProcedureRepository:
    @staticmethod
    def getById(id: int, db: Session):
        return db.query(Procedure).filter(Procedure.id == id).first()    

    @staticmethod
    def create(proc: Procedure, db: Session):
        db.add(proc)
        db.flush()
        return proc