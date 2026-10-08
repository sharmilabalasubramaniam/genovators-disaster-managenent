import os
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models.models import User, UserRole

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
SECRET_KEY = os.environ.get("SECRET_KEY", "sahyat_super_secret_key_2026")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], role: str, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60*24*7) # 7 days
    
    to_encode = {"exp": expire, "sub": str(subject), "role": role}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def require_role(roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user
    return role_checker
