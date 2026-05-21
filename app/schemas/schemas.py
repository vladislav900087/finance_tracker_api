
from pydantic import BaseModel, EmailStr

# auth schemes

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserBase(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    is_active: bool | None = None

class UserInDB(UserBase):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    full_name: str | None = None
    email: EmailStr
    password: str

# transaction schemes
class TransactionGet(BaseModel):
    title: str | None
    amount: int | None
    type: str | None
    category_title: str | None
class TransactionCreate(BaseModel):
    title: str
    amount: int
    type: str
    category_title: str


class TransactionUpdate(BaseModel):
    transaction_title: str
    title: str | None
    amount: int | None
    type: str | None
    category_title: str | None


class TransactionDelete(BaseModel):
    transaction_title: str


# Category schemes

class CategoryCreate(BaseModel):
    category_title: str






