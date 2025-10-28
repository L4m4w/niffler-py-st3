from typing import Sequence

from sqlalchemy import create_engine, Engine
from sqlmodel import Session, select

from models.spend import Category


class BaseDB:

    engine: Engine

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)