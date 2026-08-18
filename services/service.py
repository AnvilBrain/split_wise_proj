from repositories.db_ask import ask_db_about_email, check_if_email_available_register_user_into_db_indbask, register_user_into_db, create_group_ask_db, add_member_to_group_askdb, delete_member_from_group_askdb, get_user_grups_askdb, get_every_user_askdb, create_expense_equal, create_expense_exact, create_expense_percent, get_expenses_db_ask, delete_expense_db_ask, balance_ask_db, get_activity_askdb
from fastapi import FastAPI, HTTPException
from core.security import create_access_token, create_refresh_token, hash_password, check_hashed_password

async def get_user_by_email(email, password, db):
    decision = await ask_db_about_email(email, db)
    if decision is None:
        raise HTTPException(status_code=401, detail="юзер не найден")
    
    if not check_hashed_password(password, decision.hashed_password):
        raise HTTPException(status_code=401, detail="пароль не верный")


    access_token = await create_access_token(decision.email, db)
    refresh_token = create_refresh_token(decision.email, db)

    return {
        "access_token": access_token,
        "refresh_tocken": refresh_token,
        "token_type": "bearer"
    }


async def refresh_token_by_email(email, db, token):

    access_token = await create_access_token(email, db, token)

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

async def add_member_to_group_service(member_to_add, group_id, user, db):
    result = await add_member_to_group_askdb(member_to_add, group_id, user, db)
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
    if expense.split_type == SplitType.EQUAL:
        result = await create_expense_equal(expense, group_id, user, db)

    elif expense.split_type == SplitType.EXACT:
        result = await create_expense_exact(expense, group_id, user, db)

    elif expense.split_type == SplitType.PERCENT:
        result = await create_expense_percent(expense, group_id, user, db)
        
    if result is not True:
        raise HTTPException(status_code=404, detail="unexpected")
    return {"message": "success"}

async def get_expenses_service(group_id, page, limit, user, db):
    result = await get_expenses_db_ask(group_id, page, limit, db)
    return result

async def delete_expense_service(expense_id, group_id, db):
    result = await delete_expense_db_ask(expense_id, group_id, db)
    return result

async def balance_service(group_id, current_user, db):
    result = await balance_ask_db(group_id, current_user, db)

    positive_balance = []
    negative_balance = []

    complex_balance = []

    for member in result:
        if member["balance"] < 0:
            negative_balance.append(member)
        else:
            positive_balance.append(member)
    while positive_balance and negative_balance:
        debtor = min(negative_balance, key = lambda x: x["balance"])
        creditor = max(positive_balance, key = lambda x: x["balance"])
        micro_result = creditor["balance"] + debtor["balance"]
        if micro_result >= 0:
            adds = {"from": debtor["user_id"], "to": creditor["user_id"], "amount": abs(debtor["balance"])}
            negative_balance.remove(debtor)
            creditor["balance"] = micro_result
            complex_balance.append(adds)
        else:
            adds = {"from": debtor["user_id"], "to": creditor["user_id"], "amount": creditor["balance"]}
            positive_balance.remove(creditor)
            debtor["balance"] = micro_result
            complex_balance.append(adds)
    return complex_balance

async def get_creditor_service(creditor_id, group_id, current_user, db):
    result = await balance_ask_db(group_id, current_user, db)

    positive_balance = []
    negative_balance = []

    for member in result:
        if member["balance"] < 0:
            negative_balance.append(member)
        else:
            positive_balance.append(member)
    while positive_balance and negative_balance:
        debtor = min(negative_balance, key = lambda x: x["balance"])
        creditor = max(positive_balance, key = lambda x: x["balance"])
        micro_result = creditor["balance"] + debtor["balance"]
        if micro_result >= 0:
            adds = {"from": debtor["user_id"], "to": creditor["user_id"], "amount": abs(debtor["balance"])}
            if adds["from"] == current_user.id and adds["to"] == creditor_id:
                return adds
            negative_balance.remove(debtor)
            creditor["balance"] = micro_result

        else:
            adds = {"from": debtor["user_id"], "to": creditor["user_id"], "amount": creditor["balance"]}
            if adds["from"] == current_user.id and adds["to"] == creditor_id:
                return adds
            positive_balance.remove(creditor)
            debtor["balance"] = micro_result
    return {"message": "You have no debts to this person"}


async def get_activity_service(group_id, page, limit, db):
    result = await get_activity_askdb(group_id, page, limit, db)
    return result








    