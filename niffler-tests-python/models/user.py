from pydantic import BaseModel, Field, field_validator
from typing import List


class UserData(BaseModel):
   username: str
   password: str

   # @property
   # def json(self) -> dict:
   #     return self.model_dump()

class GetUsers(BaseModel):
    data: List[UserData]

    @property
    def json(self) -> dict:
        return self.model_dump()