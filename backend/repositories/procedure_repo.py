from sqlalchemy.orm import Session

from models.model_procedure import Procedure

class ProcedureRepository:
    @staticmethod
    def getById(id: int, db: Session, fields: list[str] = None):
        query = db.query(Procedure)
        if fields:
            columns = [getattr(Procedure, f) for f in fields if hasattr(Procedure, f)]
            query = db.query(*columns)

        return query.filter(Procedure.id == id).first()    

    @staticmethod
    def create(proc: Procedure, db: Session):
        db.add(proc)
        db.flush()
        return proc