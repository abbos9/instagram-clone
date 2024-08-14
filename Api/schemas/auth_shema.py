from datetime import datetime
from pydantic import BaseModel, Field



class CreateUserSchema(BaseModel):
    username: str
    first_name:str
    last_name: str
    password: bytes
    emali: str = Field(examples=['nigga@gamil.com'], pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    phone_num:str = Field(examples=['+998901454477'], pattern=r'^\+\d{12}$')
    role:str = Field(examples=["user|premium"], pattern="^(user|premium)$")
    gender:str = Field(examples=["male|female"], pattern="^(male|female)$")
    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token:str
    token_type:str

class UserResponseSchema(BaseModel):
    id: int
    username: str
    first_name:str
    last_name:str
    role:str

    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    username:str
    password:str