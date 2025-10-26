from datetime import datetime
from typing import Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlmodel import SQLModel, Field, Relationship


class Category(SQLModel, table=True):
    id: Optional[str] = Field(primary_key=True)
    name: str
    username: Optional[str]
    archived: Optional[bool]

    spends: list["Spend"] = Relationship(back_populates="category")

class Spend(SQLModel, table=True):
    id: str = Field(primary_key=True)
    amount: float
    description: str
    category_id: str = Field(foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="spends")
    # category: dict[str, str] = Field(default_factory=dict, sa_type=MutableDict.as_mutable(JSONB))
    spendDate: datetime
    currency: str