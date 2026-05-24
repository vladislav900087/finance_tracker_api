from datetime import datetime
from app.models.models import Category, User
from typing import Optional
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session

class CategoryService:
    def __init__(self, category_name, username, db: Session):
        self.category_name = category_name
        self.username = username
        self.db = db



    def get_all_categories(self, date_time: Optional[str] = None, before_or_after: Optional[str] = None):

        query = self.db.query(Category)

        user = self.db.query(User).filter(User.username == self.username).first()
        if not user:
            raise ValueError('User not found')

        try:
            if date_time:
                target_format = '%Y-%m-%d %H:%M:%S'
                if self.is_valid_date(date_time, target_format):
                    datetime_obj = datetime.fromisoformat(date_time)



                    if not before_or_after:
                        query = query.filter(Category.created_at == datetime_obj).filter(Category.user_id == user.id)
                    elif before_or_after == 'before':
                        query = query.filter(Category.created_at < datetime_obj).filter(Category.user_id == user.id)
                    elif before_or_after == 'after':
                        query = query.filter(Category.created_at > datetime_obj).filter(Category.user_id == user.id)
                    else:
                        raise ValueError('Invalid duration format')
                else:
                    raise ValueError('Invalid date format')

            return query.filter(Category.user_id == user.id).limit(10).all()

        except (NoResultFound, ValueError) as e:
            raise ValueError('Invalid data {}'.format(e))
    def is_valid_date(self, date_string: str, date_format: str) -> bool:
        try:
            datetime.strptime(date_string, date_format)
            return True
        except ValueError:
            return False

    def create_category(self):
        user = self.db.query(User).filter(User.username == self.username).first()
        if not user:
            raise ValueError(404, 'User not found')


        created_at = datetime.now()
        category = Category(name=self.category_name, user_id=user.id, created_at=created_at)

        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        return {category.name: 'created'}

    def delete_category(self):

        user = self.db.query(User).filter(User.username == self.username).first()
        if not user:
            raise ValueError(404, 'User not found')

        category = self.db.query(Category).filter(Category.user_id == user.id).filter(Category.name == self.category_name).first()

        if not category:
            raise ValueError(404, 'No category found')

        self.db.delete(category)
        self.db.commit()

        return {self.category_name: 'deleted'}



