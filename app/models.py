from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ApartmentData(Base):
    __tablename__ = "apartment_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    complex_name = Column(String(255), nullable=False)
    area_label = Column(Integer, nullable=False)
    deal_type = Column(String(20), nullable=False) 
    crawled_at = Column(DateTime, nullable=True)
    summary_data = Column(JSON, nullable=True)
    basic_info = Column(JSON, nullable=True)
    area_detail = Column(JSON, nullable=True)
    price_history = Column(JSON, nullable=True)
    price_monthly_avg = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False) 
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False) 
