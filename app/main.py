from fastapi import FastAPI
from app.api.auth_api import auth_router
from app.api.transaction_api import transaction_router
from app.database.database import engine
from app.database.database import Base
from app.models import models
from app.api.category_api import category_router
main_app = FastAPI(title='Finance Tracker API')

main_app.include_router(auth_router, prefix='/auth', tags=['Authentication'])
main_app.include_router(transaction_router, prefix='/transactions', tags=['Manage Transactions'])
main_app.include_router(category_router, prefix='/categories', tags=['Category'])

Base.metadata.create_all(bind=engine)

@main_app.get('/')
async def main_route():
    return {'message': 'Welcome to the main app!'}
