import os
import random
from typing import Dict, List

from tqdm import tqdm
from sqlalchemy.orm import Session

from core import setting
from database import get_db
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
    "can_cu_phap_ly_chi_tiet": "Căn cứ pháp lý chi tiet",
    "bieu_mau_dinh_kem": "Biểu mẫu đính kèm"
}

class ProcedureService:
    @staticmethod
    def getById(id: int, db: Session):
        return ProcedureRepository.getById(id, db)

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
            f"- {proc.id}: Đây là thủ tục **{proc.ten_thu_tuc}** thuộc lĩnh vực **{proc.linh_vuc}** do **{proc.co_quan_thuc_hien}** thực hiện." 
            for proc in procs
        ])
        return random_procedures
    
    @staticmethod
    def toString(proc: Procedure, fields: list[str] = None) -> str:
        text = (
            f"Đây là thủ tục **{proc.ten_thu_tuc}** "
            f"thuộc lĩnh vực **{proc.linh_vuc}** "
            f"do **{proc.co_quan_thuc_hien}** thực hiện."
        )

        if not fields:
            return text

        params_info = ""
        for field in fields:
            if field in ["ten_thu_tuc", "linh_vuc", "co_quan_thuc_hien"]:
                continue

            display_name = atrs.get(field, field)
            value = getattr(proc, field, None)

            if value is None:
                # Nếu không có thông tin → ghi chú
                value_str = "Chưa có thông tin cụ thể"
            else:
                if isinstance(value, list):
                    clean_list = list(dict.fromkeys([str(v).strip() for v in value if v]))
                    value_str = "\n".join(clean_list) if clean_list else "Chưa có thông tin cụ thể"
                elif isinstance(value, dict):
                    lines = [f"{k}: {v}" for k, v in value.items() if v is not None]
                    value_str = "\n".join(lines) if lines else "Chưa có thông tin cụ thể"
                else:
                    value_str = str(value).strip() or "Chưa có thông tin cụ thể"

            params_info += f"\n\n**{display_name}**:\n{value_str}"

        if params_info:
            text += "\n\n**Thông tin bạn cần tìm kiếm như sau:**" + params_info

        return text
    
    @staticmethod
    def preloadProcedure():
        db = next(get_db())
        
        dir = os.path.join(setting.artifact_dir, "procedures")
        os.makedirs(dir, exist_ok=True)

        procedures = db.query(Procedure).all()
        for proc in tqdm(procedures, desc="Preloading procedures"):
            proc_dir = os.path.join(dir, f"{proc.ma_thu_tuc}.txt")
            proc_des = f"{proc.id}: Đây là thủ tục **{proc.ten_thu_tuc}** thuộc lĩnh vực **{proc.linh_vuc}** do **{proc.co_quan_thuc_hien}** thực hiện."

            if os.path.exists(proc_dir):
                continue
            else:
                with open(proc_dir, "w", encoding="utf-8") as file:
                    file.write(proc_des)
        
        db.close()