from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.category_service import CategoryService
from typing import Optional
from app.schemas.schemas import CategoryCreate
from app.auth.auth import get_current_active_user
from app.schemas.schemas import UserBase

category_router = APIRouter()

@category_router.get('/{username}')
def get_user_categories(category_name: Optional[str] = None, date_time: Optional[str] = None, before_or_after: Optional[str] = None, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    service = CategoryService(db=db, username=current_user.username, category_name=category_name)
    try:
        return service.get_all_categories(date_time=date_time, before_or_after=before_or_after)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@category_router.post('/add')
def create_new_category(data: CategoryCreate, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    service = CategoryService(db=db, username=current_user.username, category_name=data.category_title)
    try:
        return service.create_category()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@category_router.delete('/delete')
def delete_category(category_name: str, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    service = CategoryService(db=db, category_name=category_name, username=current_user.username)
    try:
        return service.delete_category()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




