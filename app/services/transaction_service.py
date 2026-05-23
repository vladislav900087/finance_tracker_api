import sqlalchemy.orm.exc
from app.models.models import User, Transaction, Category
from typing import Optional
from datetime import datetime, timezone
import math

# TRANSACTIONS CRUD

def is_valid_date(date_string: str, date_format: str) -> bool:
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False
def create_transaction(db, title, amount, transaction_type, username, category_title : Optional[str] = None):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise ValueError('User not found')





    try:
        created_at = datetime.now(timezone.utc)
        if category_title:
            category = db.query(Category).filter(Category.name == category_title).filter(
                Category.user_id == user.id).first()

            transaction = Transaction(title=title, amount=amount, type=transaction_type, category_id=category.id, user_id=user.id, created_at=created_at)
        else:
            transaction = Transaction(title=title, amount=amount, type=transaction_type,
                                  user_id=user.id, created_at=created_at)




        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return {f'{transaction.title}': 'created'}
    except (Exception, ValueError) as e:
        raise ValueError('Invalid parameters, {}'.format(e))

def get_all_transactions(db, username, page, size, title: Optional[str] = None, amount: Optional[int] = None, transaction_type: Optional[str] = None, category_title: Optional[str] = None, from_date: Optional[str] = None, to_date: Optional[str] = None):

    query = db.query(Transaction)

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise ValueError('User not found')






    try:
        query = query.filter(Transaction.user_id == user.id)

        offset = (page - 1) * size

        if title:
            query = query.filter(Transaction.title == title)
        if amount is not None:
            query = query.filter(Transaction.amount == amount)
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
        if category_title:
            category = db.query(Category).filter(Category.name == category_title).filter(Category.user_id == user.id).first()
            if not category:
                raise ValueError('No category found')
            query = query.filter(Transaction.category_id == category.id)
        if from_date:
            target_format = '%Y-%m-%d %H:%M:%S'
            if is_valid_date(from_date, target_format):
                from_date_obj = datetime.fromisoformat(from_date)

                query = query.filter(Transaction.created_at >= from_date_obj)
        if to_date:
            target_format = '%Y-%m-%d %H:%M:%S'
            if is_valid_date(to_date, target_format):
                to_date_obj = datetime.fromisoformat(to_date)

                query = query.filter(Transaction.created_at <= to_date_obj)

        total = query.count()
        transactions = query.order_by(Transaction.created_at.desc()).limit(size).offset(offset).all()

        return {'items': transactions, 'total': total, 'page': page, 'size': size, 'pages': math.ceil(total / size)}

    except (sqlalchemy.orm.exc.NoResultFound, ValueError) as e:
        raise ValueError('An error occurred {}'.format(e))


def update_transaction(db, username, transaction_title, new_title: Optional[str] = None, new_amount: Optional[int] = None, new_type: Optional[str] = None, new_category: Optional[str] = None):


    query = db.query(Transaction)
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise ValueError('User not found')
        query = query.filter(Transaction.user_id == user.id)
        transaction = query.filter(Transaction.title == transaction_title).first()
        if not transaction:
            raise ValueError('No transaction found')
        if new_title:
            transaction.title = new_title
        if new_amount is not None:
            transaction.amount = new_amount
        if new_type:
            transaction.type = new_type
        if new_category:
            category = db.query(Category).filter(Category.name == new_category).filter(Category.user_id == user.id).first()
            if not category:
                raise ValueError('No category found')
            transaction.category_id = category.id

        db.commit()
        db.refresh(transaction)

        return {f'{transaction.title}': 'updated'}

    except sqlalchemy.orm.exc.NoResultFound as e:
        raise ValueError('An error occurred {}'.format(e))



def delete_transaction(db, username, transaction_title):
    query = db.query(Transaction)

    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise ValueError('User not found')
        query = query.filter(Transaction.user_id == user.id)
        transaction = query.filter(Transaction.title == transaction_title).first()

        if not transaction:
            raise ValueError('No transaction found')

        transaction_title = transaction.title
        db.delete(transaction)
        db.commit()


        return {f'{transaction_title}': 'deleted'}

    except sqlalchemy.orm.exc.NoResultFound as e:
        raise ValueError('An error occurred {}'.format(e))

def get_transaction_stats(db, username, from_date: Optional[str] = None, to_date: Optional[str] = None, category_title: Optional[str] = None):

    user = db.query(User).filter(User.username == username).first()


    if not user:
        raise ValueError('User not found')

    query = db.query(Transaction).filter(Transaction.user_id == user.id)

    if from_date:
        target_format = '%Y-%m-%d %H:%M:%S'
        if is_valid_date(from_date, target_format):
            from_date_obj = datetime.fromisoformat(from_date)
            query = query.filter(Transaction.created_at >= from_date_obj)
        else:
            raise ValueError('Invalid parameters, {}'.format(from_date))
    if to_date:
        target_format = '%Y-%m-%d %H:%M:%S'
        if is_valid_date(to_date, target_format):
            to_date_obj = datetime.fromisoformat(to_date)
            query = query.filter(Transaction.created_at <= to_date_obj)
        else:
            raise ValueError('Invalid parameters, {}'.format(to_date))


    income_transactions = query.filter(Transaction.type == 'income')
    expense_transactions = query.filter(Transaction.type == 'expense')

    income_transaction_amounts = [transaction.amount for transaction in list(income_transactions.all())]
    expense_transaction_amounts = [transaction.amount for transaction in list(expense_transactions.all())]

    income_summary = sum(list(income_transaction_amounts))
    expense_summary = sum(list(expense_transaction_amounts))
    balance = income_summary - expense_summary

    result = {
        'Income': income_summary,
        'Expense': expense_summary,
        'Balance': balance,
        'Incomes by category': 0,
        'Expenses by category': 0
    }

    if category_title:
        category = db.query(Category).filter(Category.name == category_title).filter(Category.user_id == user.id).first()
        if not category:
            raise ValueError('Category not found')

        income_category_transactions = [transaction.amount for transaction in list(income_transactions.filter(Transaction.category_id == category.id).all())]
        expense_category_transactions = [transaction.amount for transaction in list(expense_transactions.filter(Transaction.category_id == category.id).all())]



        if len(income_category_transactions) != 0:

            income_category_summary = sum(income_category_transactions)
            result['Incomes by category'] = {category_title: income_category_summary}
        if len(expense_category_transactions) != 0:

            expense_category_summary = sum(expense_category_transactions)
            result['Expenses by category'] = {category_title: expense_category_summary}


    return result





























