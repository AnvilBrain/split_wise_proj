from fastapi import FastAPI, HTTPException
from core.security import hash_password, check_hashed_password
from models.activity_log import ActivityLog

async def activity_log(group_id, user_id, action_type, description, db):
    new_log = ActivityLog(
        group_id=group_id,
        user_id=user_id,
        action_type=action_type,
        description=description
    )
    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)

















# class ActivityLog(Base):
#     __tablename__ = "activity_log"
#     id = Column(Integer, primary_key=True, index=True)
#     group_id = Column(Integer, ForeignKey("groups.id"))
#     user_id = Column(Integer, ForeignKey("user.id"))
#     action_type = Column(String(50), nullable=False, index=True)
#     description = Column(String, index=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())