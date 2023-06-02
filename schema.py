import pydantic
from typing import Optional
from models import User

class CreateAds(pydantic.BaseModel):
    head: str
    description: Optional[str]
    username: str
    password: str
class PatchAds(pydantic.BaseModel):
    head: Optional[str]
    description: Optional[str]
    username: Optional[str]
    password: Optional[str]

class CreateUser(pydantic.BaseModel):
    """
     Валидация полей при создании записи в модели User
    """
    email: str
    password: str

    @pydantic.validator('email')
    def validate_email(cls, value):
        if not('@' in value):
            raise ValueError('Enter correct email')
        if not('.' in value):
            raise ValueError('Enter correct email')
        return value

    @pydantic.validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('Password short')
        return value

class PatchUser(pydantic.BaseModel):
    email: Optional[str]
    password: Optional[str]