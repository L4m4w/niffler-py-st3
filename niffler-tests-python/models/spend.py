from datetime import datetime
from typing import Optional

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlmodel import SQLModel, Field, Relationship

class SpendCategoryLink(SQLModel, table=True):
    spend_id: int | None = Field(default=None, foreign_key="spend.id", primary_key=True)
    category_id: int | None = Field(default=None, foreign_key="category.id", primary_key=True)

class Category(SQLModel, table=True):
    id: Optional[str] = Field(primary_key=True)
    name: str
    username: Optional[str]
    archived: Optional[bool]

    spends: list["Spend"] = Relationship(back_populates="category", link_model=SpendCategoryLink)

class Spend(SQLModel, table=True):
    id: str = Field(primary_key=True)
    amount: float
    description: str
    category: Optional[Category] = Relationship(back_populates="spends", link_model=SpendCategoryLink)
    spendDate: datetime
    currency: str
    username: Optional[str]
