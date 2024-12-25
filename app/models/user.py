from pydantic import BaseModel, EmailStr
from app.database import get_connection

class UserLogin(BaseModel):
    email: EmailStr
    password: str
