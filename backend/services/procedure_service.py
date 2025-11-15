import json
import random
from typing import Dict, List

from sqlalchemy.orm import Session

from repositories import ProcedureRepository
from models.model_procedure import Procedure

atrs = {
    "id": "rowid",
    "ma_thu_tuc": "Mã thủ tục",
    "ten_thu_tuc": "Tên thủ tục",
    "cach_thuc_thuc_hien": "Cách thức thực hiện của thủ tục",
    "co_quan_thuc_hien": "Cơ quan thực hiện",
    "linh_vuc": "Lĩnh vực thực hiện của thủ tục",
    "trinh_tu_thuc_hien": "Trình tự thực hiện của thủ tục",
    "thoi_han_giai_quyet": "Thời hạn giải quyết của thủ tục",
    "le_phi": "Lệ phí của thủ tục",
    "thanh_phan_ho_so": "Thành phần hồ sơ của thủ tục",
    "duong_dan": "Đường dẫn",
    "doi_tuong_thuc_hien": "Đối tượng thực hiện",
    "so_luong_bo_ho_so": "Số lượng bộ hồ sơ",
    "yeu_cau_dieu_kien": "Yêu cầu, điều kiện thực hiện",
    "can_cu_phap_ly": "Căn cứ pháp lý",
    "bieu_mau_dinh_kem": "Biểu mẫu đính kèm"
}

class ProcedureService:
    @staticmethod
    def getById(id: int, db: Session, fields: List[str] = None):
        return ProcedureRepository.getById(id, db, fields)

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

    @staticmethod
    def getRandomProcedures(db: Session, n: int = 3) -> List[Procedure]:
        all_procs = db.query(Procedure).all()
        procs = random.sample(all_procs, min(n, len(all_procs)))

        random_procedures = "\n".join([
            f"- {proc.id}: Đây là thủ tục **{proc.ten_thu_tuc}** thuộc lĩnh vực **{proc.linh_vuc_thuc_hien}** do **{proc.co_quan_thuc_hien}** thực hiện." 
            for proc in procs
        ])
        return random_procedures
    
    @staticmethod
    def toString(proc: Procedure) -> str:
        text = f"Đây là thủ tục **{proc.ten_thu_tuc}** thuộc lĩnh vực **{proc.linh_vuc}** do **{proc.co_quan_thuc_hien}** thực hiện."

        params_info = ""
        for key, display_name in ProcedureService.atrs.items():
            value = getattr(proc, key, None)
            if not value or key in ["ten_thu_tuc", "linh_vuc", "co_quan_thuc_hien"]:
                continue
            
            if isinstance(value, list):
                value_str = "\n".join([str(v) for v in value if v])
                if value_str:
                    params_info += f"\n\n**{display_name}**:\n{value_str}"
            else:
                params_info += f"\n\n**{display_name}**:\n{value}"

        if params_info:
            text += "\n\n**Thông tin bạn cần tìm kiếm như sau:**" + params_info

        return text
