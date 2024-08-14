from datetime import datetime, timedelta
from typing import Annotated
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.posts_model import PostTable
from general_api.config import ALGORITHM, SECRET_KEY
from schemas.auth_shema import UserResponseSchema
from database import get_db
from models.auth_models import UsersTable


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = HTTPBearer()

db_dependency = Annotated[Session, Depends(get_db)]


def create_access_token(username: str, user_id: int, first_name: str, last_name: str, expires_delta: timedelta, role:str):
    encode = {
        "sub": username,
        "id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "role": role,
        "exp": datetime.utcnow() + expires_delta
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(db: Session, username: str, password: str):
    db_user = db.query(UsersTable).filter(UsersTable.username == username).first()
    if not db_user or not bcrypt_context.verify(password, db_user.password):
        return False
    return db_user

def decode_jwt(token: str):
    try:
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload
    except JWTError as e:
        # Handle JWT decoding errors
        print(f"Error decoding token: {e}")
        return None
    except Exception as e:
        # Handle other exceptions
        print(f"Unexpected error: {e}")
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request, session: Session = Depends(get_db)):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            payload = decode_jwt(token=credentials.credentials)
            user = session.query(UsersTable).filter(UsersTable.id == payload.get("id")).first()
            if user is None:
                raise HTTPException(status_code=403, detail="Invalid authorization code.")
            return user
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def get_user_data(self, token:str,db: Session = Depends(get_db)):
        try:
            payload =decode_jwt(token)
            username: str = payload.get("sub")
            user_id: int = payload.get("id")
            role: str = payload.get("role")
            if username is None or user_id is None or role is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
            db_user = db.query(UsersTable).filter(UsersTable.id == user_id).first()
            if db_user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
            return UserResponseSchema.from_orm(db_user)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_jwt(token=jwtoken)
        except Exception as e:
            payload = None
        if payload:
            isTokenValid = True

        return isTokenValid


class JWTHandler(JWTBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    def get_premium_user(current_user: UserResponseSchema = Depends(JWTBearer())):
        if current_user.role != "premium":
            raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")
        return current_user
        
    def get_user(current_user: UserResponseSchema = Depends(JWTBearer())):
        if current_user.role not in ["user"]:
            raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")
        return current_user

    async def get_owner(post_id: int, current_user: UserResponseSchema = Depends(JWTBearer()), db: Session = db_dependency,):
        post = (db.execute(select(PostTable).filter(PostTable.id == post_id))).scalars().first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        return post
