from typing import Optional
import uuid

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship

class SpendCategoryLink(SQLModel, table=True):
    spend_id: str | None = Field(default=None, foreign_key="spend.id", primary_key=True)
    category_id: str | None = Field(default=None, foreign_key="category.id", primary_key=True)

class Category(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(primary_key=True)
    name: str
    username: Optional[str]
    archived: Optional[bool]
    spends: list["Spend"] = Relationship(back_populates="category")
    # spends: list["Spend"] = Relationship(back_populates="category", link_model=SpendCategoryLink)

class Spend(SQLModel, table=True):
    id: str = Field(primary_key=True)
    amount: float
    description: str
    # category: Optional[Category] = Relationship(back_populates="spends", link_model=SpendCategoryLink)
    category_id: Optional[str] = Field(default=None, foreign_key="category.id")  # внешний ключ
    category: Optional[Category] = Relationship(back_populates="spends")
    spend_date: str
    currency: str
    username: Optional[str]

class SpendModel(BaseModel):
    id: Optional[str] = Field(default=None)
    amount: float
    description: str
    category_id: Optional[str] = Field(default=None, foreign_key="category.id")  # внешний ключ
    category: Optional[Category] = Relationship(back_populates="spends")
    spendDate: str
    currency: str
    username: Optional[str] = Field(default=None)

class CategoryModel(BaseModel):
    id: Optional[str] = Field(primary_key=True)
    name: str
    username: Optional[str]
    archived: Optional[bool]