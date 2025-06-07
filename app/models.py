from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ApartmentData(Base):
    __tablename__ = "apartment_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    complex_name = Column(String(255), nullable=False)
    area_label = Column(Integer, nullable=False)  # 예: 84㎡ → 84
    deal_type = Column(String(20), nullable=False)  # 예: 매매, 전세
    crawled_at = Column(DateTime, nullable=True)  # 크롤링된 실제 시점

    basic_info = Column(JSON, nullable=True)
    area_detail = Column(JSON, nullable=True)
    price_history = Column(JSON, nullable=True)
    price_monthly_avg = Column(JSON, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False) 
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False) 
