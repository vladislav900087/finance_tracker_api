from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from app.schemas.schemas import TokenData, UserBase, UserInDB
from app.database.database import get_db
from app.models.models import User
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30





password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash('dummypassword')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def get_user(db, username: str):
    db_user = db.query(User).filter(User.username == username).first()

    if not db_user:
        raise HTTPException(status_code=404, detail='User not found')

    user = UserInDB(username=db_user.username, full_name=db_user.full_name, email=db_user.email, hashed_password=db_user.password)

    return user

def authenticate_user(db, username, password):
    user = get_user(db, username)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False

    if not verify_password(password, user.hashed_password):
        return False

    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({'exp': expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):

    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials', headers={'WWW-Authenticate': 'Bearer'})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception

    return user

def get_current_active_user(current_user: Annotated[UserBase, Depends(get_current_user)]):
    if current_user.is_active == False:
        raise HTTPException(status_code=400, detail='Inactive user')

    return current_user

def create_user(db, username, password, full_name, email):
    password_hashed = get_password_hash(password)
    try:
        user = User(username=username, password=password_hashed, full_name=full_name, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        return {username: 'created'}

    except IntegrityError:
        raise HTTPException(status_code=409, detail='User already exists')


















