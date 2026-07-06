from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from core.db import Base

class GroupMember(Base):
    __tablename__ = "group_member"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())