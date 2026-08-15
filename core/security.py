from datetime import datetime, timedelta
from jose import jwt
from settings import settings
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from core.db import get_db
from sqlalchemy import select, insert
from models.user import User
from models.group_member import GroupMember

def create_access_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

def create_refresh_token(email: str):
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str):
    return pwd_context.hash(password)

def check_hashed_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        to_check = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        emeail = to_check.get("sub")
    except:
        raise HTTPException(status_code=401, detail="unexpected behavior")
    user = await db.execute(select(User).where(User.email == emeail))
    if user is None:
        raise HTTPException(status_code=401, detail="unexpected behavior")
    return user.scalar_one_or_none() 



async def check_access(user, db, group_id):
    result = await db.execute(select(GroupMember).where(GroupMember.user_id == user.id, GroupMember.group_id == group_id))
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=403, detail="access denied")
    return True
