from sqlalchemy import select, delete, or_
from models.user import User
from fastapi import FastAPI, HTTPException
from core.security import hash_password, check_hashed_password
from models.group import Group
from models.group_member import GroupMember
from models.expense_share import ExpenseShare
from models.expense import Expense
from decimal import Decimal

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


async def add_member_to_group_askdb(member_to_add, group_id, db):
    user = await db.execute(select(User).where(or_(User.email == member_to_add, User.full_name == member_to_add)))
    user_fin = user.scalar_one_or_none()

    if user_fin is None:
        raise HTTPException(status_code=404, detail="unexpected user")
    
    if_exists = await db.execute(select(GroupMember).where(GroupMember.user_id == user_fin.id, GroupMember.group_id == group_id))
    if_exists_fin = if_exists.scalar_one_or_none()

    if if_exists_fin is not None:
        raise HTTPException(status_code=409, detail="unexpected behavior, user already exists")
    
    new_member = GroupMember(
        group_id=group_id,
        user_id=user_fin.id
    )

    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    return{"message": "success"}



async def delete_member_from_group_askdb(member, group_id, db):
    user_idd =  await db.execute(select(User).where(or_(User.email == member, User.full_name == member)))
    user = user_idd.scalar_one_or_none()

    if user is None:
            raise HTTPException(status_code=404, detail="unexpected behavior")
    
    amount_owed = db.execute(select(ExpenseShare).where(ExpenseShare.user_id == user.id))
    is_owed = await amount_owed.scalar_one_or_none()

    if is_owed != 0:
        raise HTTPException(status_code=409, detail="cannot delete user with amount owed > 0")
    
    to_delete = await db.execute(delete(GroupMember).where(GroupMember.user_id == user.id))
    db.commit()
    return {"message": "success"}



#stmt = delete(User).where(User.id == 1)


async def get_user_grups_askdb(current_user, db):
    gruops = await db.execute(select(GroupMember).where(GroupMember.user_id == current_user.id))
    groups_user = gruops.scalars().all()
    return groups_user

async def get_every_user_askdb(group_id, current_user, db):
    result = await db.execute(select(User).join(GroupMember, GroupMember.user_id == User.id).where(GroupMember.group_id == group_id))
    users = result.scalars().all()
    return users

async def create_expense_askdb(expense, group_id, user, db):
    new_expense = Expense(
        group_id = group_id,
        paid_by = expense.paid_by,
        title = expense.title,
        amount = expense.amount,
        split_type = expense.split_type
    )

    db.add(new_expense)
    await db.commit()
    await db.refresh(new_expense)

    len_of_members = int(len(expense.members)) #3
    if len_of_members == 0:
        raise HTTPException(status_code=404, detail="cannot be empty list")
    to_expense = (expense.amount / len_of_members).quantize(Decimal("0.01")) #33.333333 -> 99.99 -> 100- 99.99 -> = 0.1
    accurate_expense = (expense.amount - (to_expense * len_of_members))

    to_accurate = True

    for i in range (len_of_members):
        if to_accurate is True:
            to_expense += accurate_expense
        new_expense_share = ExpenseShare(
                expense_id = new_expense.id,
                user_id = expense.members[i],
                amount_owed = to_expense
            )
        db.add(new_expense_share)
    await db.commit()
    await db.refresh(new_expense_share)
    
    return True


# class ExpenseShare(Base):
#     __tablename__ = "expense_share"
#     id = Column(Integer, primary_key=True, index=True)
#     expense_id = Column(Integer, ForeignKey("expense.id"), index=True)
#     user_id = Column(Integer, ForeignKey("user.id"), index=True)
#     amount_owed = Column(Numeric(10, 2), index=True)