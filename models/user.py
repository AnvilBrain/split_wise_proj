from sqlalchemy import Column, Integer, String
from core.db import Base
from sqlalchemy import DateTime
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, index=True)
    full_name = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

