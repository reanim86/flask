import pydantic
from typing import Optional
from models import User

class CreateAds(pydantic.BaseModel):
    head: str
    description: Optional[str]
    username: int
class PatchAds(pydantic.BaseModel):
    head: Optional[str]
    description: Optional[str]
    username: Optional[int]