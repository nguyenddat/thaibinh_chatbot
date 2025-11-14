from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.mysql import JSONB
from sqlalchemy.dialects.postgresql import VECTOR

from models.model_base import BareBaseModel

class Procedure(BareBaseModel):
    ma_thu_tuc = Column(String, unique=True, nullable=False)
    ten_thu_tuc = Column(String, nullable=False)

    co_quan_thuc_hien = Column(String)       
    linh_vuc = Column(String)
    trinh_tu_thuc_hien = Column(String)
    doi_tuong_thuc_hien = Column(String)
    yeu_cau_dieu_kien = Column(String)
    can_cu_phap_ly = Column(String)
    cach_thuc_thuc_hien = Column(JSONB)
    thoi_han_giai_quyet = Column(String)     
    le_phi = Column(JSONB)
    thanh_phan_ho_so = Column(JSONB)

    vector = Column(VECTOR(1536))
    processed = Column(Boolean, default=False)