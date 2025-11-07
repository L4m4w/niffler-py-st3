from typing import Sequence

from sqlmodel import Session, select

from database.base_db import BaseDB
from models.config import Envs
from models.userdata import User


class UserDataDB(BaseDB):
    def __init__(self, env: Envs):
        super().__init__(env.userdata_db_url)

    def get_user_data(self, username: str):
        with Session(self.engine) as session:
            statement = select(User).where(User.username == username)
            return session.exec(statement).one()