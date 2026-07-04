from repositories.db_ask import ask_db_about_email
from fastapi import FastAPI, HTTPException

async def get_user_by_email(email, password, db):
    decision = await ask_db_about_email(email, db)
    if decision is None:
        raise HTTPException(status_code=401, detail="юзер не найден")
    if decision.password != password:
        raise HTTPException(status_code=401, detail="пароль не верный")

    return decision

    
    #result = await db.execute(select(User).where(User.email == email))
    #return result