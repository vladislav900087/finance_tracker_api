from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.schemas import TransactionCreate, TransactionDelete, TransactionUpdate
from app.database.database import get_db
from app.services.transaction_service import create_transaction, update_transaction, delete_transaction, get_all_transactions, get_transaction_stats
from sqlalchemy.orm.exc import NoResultFound
from typing import Annotated
from app.schemas.schemas import UserBase
from app.auth.auth import get_current_active_user




transaction_router = APIRouter()

@transaction_router.post('/transactions/add/')
def add_transaction(data: TransactionCreate, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    try:
        return create_transaction(db=db, title=data.title, amount=data.amount, category_title=data.category_title, transaction_type=data.type, username=current_user.username)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@transaction_router.post('/transactions/update/')
def update_user_transaction(data: TransactionUpdate, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):

    try:
        return update_transaction(db=db, username=current_user.username, transaction_title=data.transaction_title, new_title=data.title, new_amount=data.amount, new_category=data.category_title, new_type=data.type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@transaction_router.delete('/transactions/delete/')
def delete_user_transaction(current_user: Annotated[UserBase, Depends(get_current_active_user)], data: TransactionDelete, db: Session = Depends(get_db)):
    try:
        return delete_transaction(db=db, username=current_user.username, transaction_title=data.transaction_title)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@transaction_router.get('/transactions/{username}/')
def get_user_transactions(
    current_user: Annotated[UserBase, Depends(get_current_active_user)],
    title: str | None = None,
    amount: int | None = None,
    transaction_type: str | None = None,
    category_title: str | None = None,
    page: int = Query(1, ge=1, le=100),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return get_all_transactions(
        username=current_user.username,
        db=db,
        title=title,
        amount=amount,
        category_title=category_title,
        transaction_type=transaction_type,
        page=page,
        size=size
    )

@transaction_router.get('/transactions/{username}/stats/')
def get_user_transactions_stats(current_user: UserBase = Depends(get_current_active_user), from_date: str | None = None, to_date: str | None = None, category_title: str | None = None, db: Session = Depends(get_db)):

    try:
        return get_transaction_stats(username=current_user.username, from_date=from_date, to_date=to_date, db=db, category_title=category_title)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


