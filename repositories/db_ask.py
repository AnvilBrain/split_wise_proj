from sqlalchemy import select
from models.user import User

async def ask_db_about_email(email, db):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
