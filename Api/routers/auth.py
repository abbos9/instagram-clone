from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv
from database import get_db
from general_api.config import Tashkent_tz
from models.auth_models import UsersTable
from schemas.auth_shema import CreateUserSchema, TokenSchema, UserResponseSchema, UserLoginSchema, UserVerifications
from utils.auth_utils import JWTBearer, bcrypt_context, authenticate_user, create_access_token

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

router = APIRouter(
    prefix="/auth",
    tags=['Auth']
)

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(db: db_dependency, create_user_schema: CreateUserSchema):
    try:
        create_user_model = UsersTable(
            username=create_user_schema.username,
            password=bcrypt_context.hash(create_user_schema.password),
            first_name=create_user_schema.first_name,
            last_name=create_user_schema.last_name,
            role=create_user_schema.role,
            phone_num=create_user_schema.phone_num,
            gender=create_user_schema.gender,
            email=create_user_schema.emali,
            date_joined=datetime.now(Tashkent_tz),  # Setting date joined
        )
        db.add(create_user_model)
        db.commit()
        db.refresh(create_user_model)
        return {"message": f"Successfully registered {create_user_schema.first_name} {create_user_schema.last_name}"}
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username, phone number, or email already exists")



@router.post('/token/', response_model=TokenSchema)
async def signin_by_access_token(db: db_dependency, data: UserLoginSchema):
    user = authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
    token = create_access_token(user.username, user.id, user.first_name, user.last_name, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), user.role)
    return {
        'access_token': token,
        'token_type': 'Bearer'
    }

@router.get("/me/", response_model=UserResponseSchema)
async def get_me(current_user: UserResponseSchema = Depends(JWTBearer())):
    return current_user


@router.put("/password/change", status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema)
async def change_password(db: db_dependency, user_ver:UserVerifications, current_user: UserResponseSchema = Depends(JWTBearer())):
    user = db.query(UsersTable).filter(UsersTable.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not bcrypt_context.verify(user_ver.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong password")
    
    user.password = bcrypt_context.hash(user_ver.new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user