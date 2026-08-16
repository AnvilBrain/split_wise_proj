from sqlalchemy import select, delete, or_
from models.user import User
from fastapi import HTTPException
from core.security import hash_password
from models.group import Group
from models.group_member import GroupMember
from models.expense_share import ExpenseShare
from models.expense import Expense
from decimal import Decimal
from log import activity_log

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


async def add_member_to_group_askdb(member_to_add, group_id, user, db):
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
    await activity_log(group_id, user.user_id, "add member to group", f"added {user_fin.id}", db)
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

#equal
async def create_expense_equal(expense, group_id, user, db):
    if len_of_members == 0:
            raise HTTPException(status_code=404, detail="cannot be empty list")
    
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
    
    to_expense = (expense.amount / len_of_members).quantize(Decimal("0.01")) #33.333333 -> 99.99 -> 100- 99.99 -> = 0.1
    accurate_expense = (expense.amount - (to_expense * len_of_members))
    
    if accurate_expense > 0:
        to_accurate = True
    else:
        to_accurate = False

    for i in range (len_of_members):
        if to_accurate is True:
            to_expense += accurate_expense
            to_accurate = False
        new_expense_share = ExpenseShare(
                expense_id = new_expense.id,
                user_id = expense.members[i],
                amount_owed = to_expense
            )
        db.add(new_expense_share)
    await db.commit()
    await db.refresh(new_expense_share)
    await activity_log(group_id, user.user_id, "created equal expense", f"{user.user_id} created equal expense", db)
    
    return True

#exact
async def create_expense_exact(expense, group_id, user, db):
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

    total = sum(share.amount for share in expense.shares)
    if total != expense.amount:
        raise HTTPException(status_code=400, detail="суммы не сходятся")
    for share in expense.shares:
        new_expense_share = ExpenseShare(
                expense_id = new_expense.id,
                user_id = share.user_id,
                amount_owed = share.amount
            )
        db.add(new_expense_share)
    await db.commit()
    await db.refresh(new_expense_share)
    await activity_log(group_id, user.user_id, "created exact expense", f"{user.user_id} created exact expense", db)

    return True


#percent
async def create_expense_percent(expense, group_id, user, db):
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

    
    total = sum(share.percent for share in expense.shares)
    if total != 100:
        raise HTTPException(status_code=400, detail="сумма процентов должна быть 100")
    for share in expense.shares:
        amount_owed = expense.amount * share.percent / 100
        new_expense_share = ExpenseShare(
                expense_id = new_expense.id,
                user_id = share.user_id,
                amount_owed = amount_owed
            )
        db.add(new_expense_share)
    await db.commit()
    await db.refresh(new_expense_share)
    await activity_log(group_id, user.user_id, "created percent expense", f"{user.user_id} created percent expense", db)

    return True
# class ExpenseShare(Base):
#     __tablename__ = "expense_share"
#     id = Column(Integer, primary_key=True, index=True)
#     expense_id = Column(Integer, ForeignKey("expense.id"), index=True)
#     user_id = Column(Integer, ForeignKey("user.id"), index=True)
#     amount_owed = Column(Numeric(10, 2), index=True)



async def get_expenses_db_ask(group_id, page, limit, db):
    offset = (page - 1) * limit
    result = await db.execute(select(Expense).where(Expense.group_id == group_id).limit(limit).offset(offset))
    return result.scalars().all()


async def delete_expense_db_ask(expense_id, group_id, user, db):
    result = await db.execute(select(Expense).where(Expense.group_id == group_id, Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if expense is None:
        raise HTTPException(status_code=404, detail="invalid data")
    expense.is_deleted = True
    await db.execute(delete(ExpenseShare).where(ExpenseShare.expense_id == expense_id))
    await db.commit()
    await activity_log(group_id, user.user_id, "deleted expense", f"{user.user_id} deleted expense {expense_id}", db)
    return {"message": "success"}

async def balance_ask_db(group_id, current_user, db):
    result = await db.execute(select(GroupMember).where(GroupMember.group_id == group_id))
    cycle = result.scalars().all()
    balances = []
    for member in cycle:
        paid = await db.scalar(select(func.sum(Expense.amount)).where(Expense.paid_by == member.user_id, Expense.is_deleted != True, Expense.group_id == group_id))
        owed = await db.scalar(select(func.sum(ExpenseShare.amount_owed)).join(Expense, Expense.id == ExpenseShare.expense_id).where(ExpenseShare.user_id == member.user_id, Expense.group_id == group_id, Expense.is_deleted == False))
        paid = paid or Decimal("0")
        owed = owed or Decimal("0")
        balance = paid - owed
        member_balance = {"user_id": member.user_id, "balance": balance}
        balances.append(member_balance)
    return balances



async def get_activity_askdb(group_id, page, limit, db)
