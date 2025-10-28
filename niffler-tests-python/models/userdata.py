from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: Optional[UUID] = Field(primary_key=True)
    username: str
    currency: str
    firstname: Optional[str]
    surname: Optional[str]
    photo: Optional[str]
    photo_small: Optional[str]
    full_name: Optional[str]

class UserModel(BaseModel):
    id: str
    username: str
    currency: str
    firstname: str
    surname: str
    photo: str
    photo_small: str
    full_name: str

class UserUpdateProfile(BaseModel):
    id: str
    username: Optional[str] = Field(default=None)
    fullname: Optional[str] = Field(default=None)
    currency: Optional[str] = Field(default=None)
