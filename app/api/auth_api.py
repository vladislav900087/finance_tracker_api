from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.auth import *
from app.schemas.schemas import UserCreate, UserBase, Token
from sqlalchemy.orm import Session
from app.database.database import get_db


auth_router = APIRouter()





@auth_router.post('/token', response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    username = user.username
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': username}, expires_delta=access_token_expires)

    return {'access_token': access_token, 'token_type': 'bearer'}

@auth_router.post('/register')
def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(username=user.username, password=user.password, email=user.email, full_name=user.full_name, db=db)



@auth_router.get('/users/me', response_model=UserBase)
def read_current_user(current_user: UserBase = Depends(get_current_user)):
    return current_user

@auth_router.get('/users/me/items')
def read_current_user_items(current_user: UserBase = Depends(get_current_user)):
    return [{'username': current_user.username, 'items': 2}]

