from typing import Sequence

from sqlmodel import Session, select

from database.base_db import BaseDB
from models.userdata import User


class UserDataDB(BaseDB):
    def __init__(self, db_url: str):
        super().__init__(db_url)

    def get_user_data(self, username: str):
        with Session(self.engine) as session:
            statement = select(User).where(User.username == username)
            return session.exec(statement).one()