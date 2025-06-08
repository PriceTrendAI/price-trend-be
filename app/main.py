from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, ApartmentData
from app.crawler import NaverLandCrawler
from app.crud import save_apartment_data
from app.utils import compute_monthly_avg
from datetime import datetime
from app.utils import *

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:5173",  
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/search")
def get_property_info(keyword: str):
    crawler = NaverLandCrawler()
    return crawler.fetch_property_info(keyword=keyword)

@app.get("/crawl/price-data", summary="가격 데이터 크롤링 및 저장")
def get_monthly_price(
    keyword: str = Query(..., description="검색어 예: '삼송동일스위트'"),
    index: int = Query(..., ge=1, description="검색 결과에서 선택할 항목 번호 (1부터)"),
    area: str = Query(..., description="면적 (예: '84')"),
    deal_type: str = Query(..., description="거래 유형 (예: '매매')"),
    db: Session = Depends(get_db),
) -> dict:
    crawler = NaverLandCrawler(headless=True)
    try:
        result = crawler.run(keyword, index - 1, area, deal_type)

        basic_info = result.get("complex_info", {})
        area_detail = result.get("area_info", {})
        price_history = result.get("price_history", {})
        price_monthly_avg = compute_monthly_avg(price_history)

        save_apartment_data(db=db, complex_name=keyword, area_label=int(area), deal_type=deal_type, 
                            crawled_at=datetime.utcnow(), basic_info=basic_info, area_detail=area_detail, 
                            price_history=price_history, price_monthly_avg=price_monthly_avg
                            )
        return {"status": "success", "saved": True}
    finally:
        crawler.close()

@app.get("/apartments", summary="모든 아파트 데이터 조회")
def get_all_apartments(db: Session = Depends(get_db)):
    return db.query(ApartmentData).order_by(ApartmentData.crawled_at.desc()).all()

@app.get("/apartments/{apartment_id}", summary="ID로 아파트 데이터 조회")
def get_apartment_by_id(apartment_id: int, db: Session = Depends(get_db)):
    return db.query(ApartmentData).filter(ApartmentData.id == apartment_id).first()
