from repositories.db_ask import ask_db_about_email, check_if_email_available_register_user_into_db_indbask, register_user_into_db, create_group_ask_db, add_member_to_group_askdb, delete_member_from_group_askdb, get_user_grups_askdb, get_every_user_askdb
from fastapi import FastAPI, HTTPException
from core.security import create_access_token, create_refresh_token, hash_password, check_hashed_password
async def get_user_by_email(email, password, db):
    decision = await ask_db_about_email(email, db)
    if decision is None:
        raise HTTPException(status_code=401, detail="юзер не найден")
    
    if not check_hashed_password(password, decision.hashed_password):
        raise HTTPException(status_code=401, detail="пароль не верный")


    access_token = create_access_token(decision.email)
    refresh_token = create_refresh_token(decision.email)

    return {
        "access_token": access_token,
        "refresh_tocken": refresh_token,
        "token_type": "bearer"
    }


async def refresh_token_by_email(email):

    access_token = create_access_token(email)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


async def register_user_in_database(email, full_name, password, db):
    desicion_register = await check_if_email_available_register_user_into_db_indbask(email, db)
    if desicion_register is not None:
        raise HTTPException(status_code=409, detail="email is already registered")
    is_registered = await register_user_into_db(email, full_name, password, db)
    return is_registered

async def create_group_service(user, name, db):
    is_created = await create_group_ask_db(user, name, db)
    return is_created

async def add_member_to_group_service(member_to_add, group_id, db):
    result = await add_member_to_group_askdb(member_to_add, group_id, db)
    return result


async def delete_member_from_group_service(member, group_id, db):
    result = await delete_member_from_group_askdb(member, group_id, db)
    return result
    #result = await db.execute(select(User).where(User.email == email))
    #return result


async def get_user_grups_service(current_user, db):
    result = await get_user_grups_askdb(current_user, db)
    return result

async def get_every_user_service(group_id, db):
    result = await get_every_user_askdb(group_id, db)
    return result

async def create_expense_service(expense, group_id, user, db):
    result = await create_expense_askdb(expense, group_id, user, db)
    if result is not True:
        raise HTTPException(status_code=404, detail="unexpected")
