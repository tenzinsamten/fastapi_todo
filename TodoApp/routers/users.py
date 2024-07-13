from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from ..database import SessionLocal
from ..models import Users
from .auth import get_current_user

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class ChanagePasswordRequest(BaseModel):
    password: str
    new_password: str

@router.get("", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency, ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return user_model


@router.put("/password", status_code=status.HTTP_202_ACCEPTED)
async def change_password(user: user_dependency, db: db_dependency,change_password_request: ChanagePasswordRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if not bcrypt_context.verify(change_password_request.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not vertification failed")
    user_model.hashed_password = bcrypt_context.hash(change_password_request.new_password)
    db.add(user_model)
    db.commit()
    return user_model
