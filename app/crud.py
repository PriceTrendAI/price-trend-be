from sqlalchemy.orm import Session
from .models import ApartmentData
from typing import Optional, Dict
from datetime import datetime

def save_apartment_data(
    db: Session,
    complex_name: str,
    area_label: int,
    deal_type: str,
    crawled_at: Optional[datetime] = None,
    summary_data: Optional[Dict] = None,
    complex_info: Optional[Dict] = None,
    area_detail: Optional[Dict] = None,
    price_history: Optional[Dict] = None,
    price_monthly_avg: Optional[Dict] = None,
    forecast_json: Optional[Dict] = None
) -> ApartmentData:
    db_data = ApartmentData(
        complex_name=complex_name,
        area_label=area_label,
        deal_type=deal_type,
        crawled_at=crawled_at,
        summary_data=summary_data,
        complex_info=complex_info,
        area_detail=area_detail,
        price_history=price_history,
        price_monthly_avg=price_monthly_avg,
        forecast_json=forecast_json
    )
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data
