from fastapi import APIRouter, Depends
from pydantic import BaseModel 
from services.service import get_user_by_email
from core.db import get_db

router = APIRouter()

class UserLogin(BaseModel):
    email:str
    password:str
    full_name:str

@router.post("/login")
async def login_user(login: UserLogin, db=Depends(get_db)):
    finally_des = await get_user_by_email(login.email, login.password, db)
    return finally_des

    