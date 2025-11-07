from typing import Sequence

from sqlmodel import Session, select

from database.base_db import BaseDB
from models.spend import Category
from models.config import Envs


class SpendDB(BaseDB):
    def __init__(self, env: Envs):
        super().__init__(env.spend_db_url)

    def get_user_categories(self, username: str) -> Sequence[Category]:
        with Session(self.engine) as session:
            statement = select(Category).where(Category.username == username)
            return session.exec(statement).all()

    def get_user_categories_by_name(self, username: str, name: str) -> Sequence[Category]:
        with Session(self.engine) as session:
            statement = select(Category).where(Category.username == username and Category.name == name)
            return session.exec(statement).all()

    def delete_category(self, category_id):
        with Session(self.engine) as session:
            category = session.get(Category, category_id)
            session.delete(category)
            session.commit()