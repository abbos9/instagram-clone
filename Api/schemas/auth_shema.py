from datetime import datetime
from pydantic import BaseModel, Field, EmailStr



class CreateUserSchema(BaseModel):
    username: str
    first_name:str
    last_name: str
    password: bytes
    emali: EmailStr = Field(examples=['nigga@gamil.com'])
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


class UserVerifications(BaseModel):
    password:str
    new_password: str = Field(min_length=6)