from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class ApartmentBase(BaseModel):
    complex_name: str
    area_label: int
    deal_type: str
    basic_info: Optional[Dict] = None
    area_detail: Optional[Dict] = None
    price_history: Optional[Dict] = None
    price_monthly_avg: Optional[Dict] = None

    class Config:
        orm_mode = True


class ApartmentCreate(ApartmentBase):
    pass


class ApartmentResponse(ApartmentBase):
    id: int
    crawled_at: datetime
    created_at: datetime
    updated_at: datetime
