from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    name: str

    class Config:
        from_attributes = True
