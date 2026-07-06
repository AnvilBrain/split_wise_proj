from sqlalchemy import select, insert
from models.user import User
from fastapi import FastAPI, HTTPException
from core.security import hash_password, check_hashed_password
from models.group import Group

async def ask_db_about_email(email, db):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def check_if_email_available_register_user_into_db_indbask(email, db):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none() 

async def register_user_into_db(email, full_name, password, db):

    new_user = User(
        email=email,
        hashed_password= hash_password(password),
        full_name=full_name
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "success"}

async def create_group_ask_db(user, name, db):

    new_group = Group(
        name = name,
        created_by = user.id
    )
    db.add(new_group)
    await db.commit()
    await db.refresh(new_group)

    return {"message": "success"}
