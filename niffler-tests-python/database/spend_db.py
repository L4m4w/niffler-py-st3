from typing import Sequence

from sqlmodel import Session, select

from database.base_db import BaseDB
from models.spend import Category


class SpendDB(BaseDB):
    def __init__(self, db_url: str):
        super().__init__(db_url)

    def get_user_categories(self, username: str) -> Sequence[Category]:
        with Session(self.engine) as session:
            statement = select(Category).where(Category.username == username)
            return session.exec(statement).all()

    def delete_category(self, category_id):
        with Session(self.engine) as session:
            category = session.get(Category, category_id)
            session.delete(category)
            session.commit()