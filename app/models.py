from sqlalchemy import Column, Integer, String
from .database import Base

class TestTable(Base):
    __tablename__ = "test_table"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
