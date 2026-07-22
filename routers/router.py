from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from services.service import get_user_by_email, register_user_in_database, create_group_service, refresh_token_by_email, add_member_to_group_service, delete_member_from_group_service, get_user_grups_service, get_every_user_service
from core.db import get_db
from core.security import get_current_user, check_access

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

class AddMember(BaseModel):
    group_member:str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)

@router.post("/login")
async def login_user(login: UserLogin, db=Depends(get_db)):
    finally_des = await get_user_by_email(login.email, login.password, db)
    return finally_des

@router.post("/register")
async def register_user(register: UserRegister, db=Depends(get_db)):
    final_des = await register_user_in_database(register.email, register.full_name, register.password, db)
    return final_des

@router.get("/me")
async def read_current_user(current_user=Depends(get_current_user)):
    return {"email": current_user.email}

@router.post("/group")
async def create_group(name: GroupCreate, current_user=Depends(get_current_user), db=Depends(get_db)):
    is_group_created = await create_group_service(current_user, name.group_name, db)
    return is_group_created

@router.get("/refresh")
async def refresh_token(current_user=Depends(get_current_user)):
    refresh_result = await refresh_token_by_email(current_user.email)
    return refresh_result

@router.post("/groups/{group_id}/members")
async def add_member_to_group(member: AddMember, current_user=Depends(get_current_user), db=Depends(get_db), group_id=int):
    await check_access(current_user , db, group_id)
    is_member_added = add_member_to_group_service(member.group_member, group_id, db)
    return is_member_added

@router.delete("/groups/{group_id}/members")
async def delete_member_from_group(member: AddMember, current_user=Depends(get_current_user), db=Depends(get_db), group_id=int):
    await check_access(current_user , db, group_id)
    is_member_deleted = await delete_member_from_group_service(member.group_member, group_id, db)
    return is_member_deleted

@router.get("/groups")
async def get_user_groups(current_user=Depends(get_current_user), db=Depends(get_db)):
    result = await get_user_grups_service(current_user, db)
    return result

@router.get("/groups/{group_id}/members", response_model=list[UserResponse])
async def get_every_user(group_id:int, current_user=Depends(get_current_user), db=Depends(get_db)):
    await check_access(current_user , db, group_id)
    result = await get_every_user_service(group_id, db)
    return result