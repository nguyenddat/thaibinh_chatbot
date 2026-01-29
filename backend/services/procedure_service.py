import random
from typing import Dict, Optional

from sqlalchemy.orm import Session

from database import get_db
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
    def getById(id: int, db: Session) -> Procedure:
        exist_proc = db.query(Procedure).filter(Procedure.id == id).first()
        return exist_proc

    @staticmethod
    def create(proc: Procedure, db: Session):
        db.add(proc)
        db.flush()
        db.refresh(proc)
        return proc

    @staticmethod
    def createByJsonFile(data, db: Session):        
        ma_thu_tuc = data["ma_thu_tuc"]
        existing = db.query(Procedure).filter(Procedure.ma_thu_tuc == ma_thu_tuc).first()
        if existing:
            return None
        else:
            filtered_data = {k: v for k, v in data.items() if k in Procedure.get_allowed_fields()}
            new = Procedure(**filtered_data)
            return ProcedureService.create(new, db)

    @staticmethod
    def updateById(proc: Procedure, update_data: Dict[str, str], db: Session):
        for key, value in update_data.items():
            if hasattr(proc, key):
                setattr(proc, key, value)
        db.flush()
        return proc

    @staticmethod
    def getRandomProcedures(db: Optional[Session] = None, n: int = 3) -> str:
        close_after = False
        if db is None:
            db = next(get_db())
            close_after = True

        all_procs = db.query(Procedure).all()
        chosen = random.sample(all_procs, min(n, len(all_procs)))
        result = "\n".join([
            f"- {p.id}: Đây là thủ tục **{p.ten_thu_tuc}** thuộc lĩnh vực **{p.linh_vuc}** do **{p.co_quan_thuc_hien}** thực hiện."
            for p in chosen
        ])

        if close_after:
            db.close()

        return result
    
    @staticmethod
    def toString(proc: Procedure, fields: list[str] = None) -> str:
        text = f"""Đây là thủ tục **{proc.ten_thu_tuc}** thuộc lĩnh vực **{proc.linh_vuc}** do **{proc.co_quan_thuc_hien}** thực hiện."""
        text += f"\**Thông tin bạn cần tìm kiếm như sau:**"

        if not fields:
            text += f"\nChi tiết thủ tục có thể xem tại: {proc.duong_dan}"
            return text

        details = ""
        for field in fields:
            if field in ["ten_thu_tuc", "linh_vuc", "co_quan_thuc_hien", "duong_dan"]:
                continue

            display_name = atrs.get(field, field)
            
            value = getattr(proc, field, None)
            if not value:
                details += f"\n\n## {display_name}\nChưa có thông tin cụ thể."
                continue

            if isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], dict):
                    rows = [v for v in value if any(str(x).strip() for x in v.values())]
                    if not rows:
                        details += f"\n\n## {display_name}\nChưa có thông tin cụ thể."
                        continue
                    headers = list(rows[0].keys())
                    table = [" | ".join(headers), " | ".join(["---"]*len(headers))]
                    for r in rows:
                        table.append(" | ".join(str(r.get(h, "")).strip() for h in headers))
                    details += f"\n\n## {display_name}\n" + "\n".join(table)
                else:
                    clean_list = [str(v).strip() for v in value if str(v).strip()]
                    if clean_list:
                        details += f"\n\n## {display_name}\n" + "\n".join(f"- {item}" for item in clean_list)
                    else:
                        details += f"\n\n## {display_name}\nChưa có thông tin cụ thể."
                continue

            if isinstance(value, dict):
                lines = [f"- {k}: {v}" for k, v in value.items() if v is not None and str(v).strip()]
                details += f"\n\n## {display_name}\n" + ("\n".join(lines) if lines else "Chưa có thông tin cụ thể.")
                continue

            details += f"\n\n## {display_name}\n{str(value).strip() or 'Chưa có thông tin cụ thể.'}"

        if details:
            text += "\n\n# Thông tin chi tiết" + details

        text += f"\n\nBạn có thể xem chi tiết thủ tục tại: {proc.duong_dan}"
        return text