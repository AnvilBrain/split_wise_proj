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
from sqlalchemy import select, delete, or_

async def create_access_token(email: str, db, token: str | None = None):
    if not token:
        result = await db.execute(select(User).where(User.email == email))
        result2 = result.scalar_one_or_none()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": email, "type": "access", "exp": expire}
        tokcen = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        result2.acces_token = tokcen

        await db.commit()
        await db.refresh(result2)
        return tokcen
    else:
        try:
            to_check = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            details = to_check.get("sub")
            token_type = to_check.get("type")
        except:
            raise HTTPException(status_code=401, detail="unexpected behavior2")
    if token_type == "refresh":
        result = await db.execute(select(User).where(User.email == details, User.refresh_token == token))
        result2 = result.scalar_one_or_none()
        if not result2:
            raise HTTPException(status_code=401, detail="wrong token")
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": email, "type": "access", "exp": expire}
        tokcen = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        result2.acces_token = tokcen

        await db.commit()
        await db.refresh(result2)
        return tokcen


async def create_refresh_token(email: str, db):
    result = await db.scalar(select(User).where(User.email == email))
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": email, "type": "refresh", "exp": expire}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    result.refresh_token = token
    await db.commit()
    await db.refresh(result)

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
        type_t = to_check.get("type")
    except:
        raise HTTPException(status_code=401, detail="unexpected behavior2")
    if type_t == "refresh":
        raise HTTPException(status_code=401, detail="wrong token type")
    user = await db.execute(select(User).where(User.email == emeail, User.acces_token == token))
    user2 = user.scalar_one_or_none() 
    if user2 is None:
        raise HTTPException(status_code=401, detail="unexpected behavior")
    return user2


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
async def get_current_user_refresh(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        to_check = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        emeail = to_check.get("sub")
        type_t = to_check.get("type")
    except:
        raise HTTPException(status_code=401, detail="unexpected behavior2")
    if type_t == "access":
        raise HTTPException(status_code=401, detail="wrong token type")
    user = await db.execute(select(User).where(User.email == emeail, User.resresh_token == token))
    user2 = user.scalar_one_or_none() 
    if user2 is None:
        raise HTTPException(status_code=401, detail="unexpected behavior")
    return user2

async def check_access(user, db, group_id):
    result = await db.execute(select(GroupMember).where(GroupMember.user_id == user.id, GroupMember.group_id == group_id))
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=403, detail="access denied")
    return True
