from pydantic import BaseModel, validator
from typing import Optional


class CreateAdvSchema(BaseModel):
    title: str
    desc: str
    owner: str

    @validator("title")
    def check_title(cls, value):
        if len(value) <= 10:
            raise ValueError("title is too short")
        elif len(value) > 50:
            raise ValueError("title is too long")
        return value


class UpdateAdvSchema(BaseModel):
    title: Optional[str]
    desc: Optional[str]

    @validator("title")
    def check_title(cls, value):
        if len(value) <= 10:
            raise ValueError("title is too short")
        elif len(value) > 50:
            raise ValueError("title is too long")
        return value


class UserSchema(BaseModel):
    nickname: str
    email: str
    password: str
    is_admin: bool = False
