from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Numeric, Enum
from sqlalchemy.sql import func
from core.db import Base
import enum
from decimal import Decimal

class SplitType(enum.Enum):
    EQUAL = "EQUAL"
    EXACT = "EXACT"
    PERCENT = "PERCENT"

class Expense(Base):
    __tablename__ = "expense"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), index=True)
    paid_by = Column(Integer, ForeignKey("user.id"), index=True)
    title = Column(String, index=True)
    amount = Column(Numeric(10, 2), index=True)
    split_type = Column(
        Enum(SplitType, name="split_type"),
        default=SplitType.EQUAL,
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)