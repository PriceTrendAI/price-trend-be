from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models
from sqlalchemy import text

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/ping-db")
def ping_db(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1"))
        value = result.scalar()  # 단일 값으로 추출
        return {"status": "success", "result": value}
    except Exception as e:
        return {"status": "fail", "error": str(e)}