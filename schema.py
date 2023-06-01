import pydantic
from typing import Optional

class CreateAds(pydantic.BaseModel):
    head: str
    description: Optional[str]
    username: str
class PatchAds(pydantic.BaseModel):
    head: Optional[str]
    description: Optional[str]
    username: Optional[str]