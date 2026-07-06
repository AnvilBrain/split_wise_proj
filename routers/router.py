from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel 
from services.service import get_user_by_email, register_user_in_database, create_group_service
from core.db import get_db
from core.security import get_current_user

router = APIRouter()

class UserLogin(BaseModel):
    email:str
    password:str

class UserRegister(BaseModel):
    email:str
    password:str
    full_name:str

class GroupCreate(BaseModel):
    group_name:str

@router.post("/login")
async def login_user(login: UserLogin, db=Depends(get_db)):
    finally_des = await get_user_by_email(login.email, login.password, db)
    return finally_des

@router.post("/register")
async def register_user(register: UserRegister, db=Depends(get_db)):
    final_des = await register_user_in_database(register.email, register.full_name, register.password, db)
    return final_des

@router.get("/me")
async def read_current_user(current_user=Depends(get_current_user), db=Depends(get_db)):
    user = await get_user_by_email(current_user, db)
    if user is None:
        raise HTTPException(status_code=401, detail="unexpected behavior")
    return {"email": user.email}

@router.post("/group")
async def create_group(name: GroupCreate, current_user=Depends(get_current_user), db=Depends(get_db)):
    user = await get_user_by_email(current_user, db)
    if user is None:
        raise HTTPException(status_code=401, detail="unexpected behavior")
    is_group_created = await create_group_service(user, name.group_name, db)
    return is_group_created