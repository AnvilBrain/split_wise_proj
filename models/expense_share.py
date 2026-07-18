from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from core.db import Base
from sqlalchemy import Numeric

class ExpenseShare(Base):
    __tablename__ = "expense_share"
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expense.id"), index=True)
    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    amount_owed = Column(Numeric(10, 2), index=True)