from datetime import timedelta, datetime, timezone

from fastapi import APIRouter, Depends,HTTPException
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext

from ..database import SessionLocal
from ..models import Users
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)
SECRET_KEY = 'fcc334b62d74e7ebde4c2a3c522cc72e40a85059eae453d372f6de69bd616f01'
ALGORITHM = 'HS256'
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class CreateUserRequest(BaseModel):
    user_name: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class AuthenticationResponse(BaseModel):
    access_token: str
    token_type: str


async def get_current_user(token : Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate user")
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate user")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        user_name=create_user_request.user_name,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True
    )
    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=AuthenticationResponse, status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    is_valid_user = authenticate_user(form_data.username, form_data.password, db)
    if is_valid_user is not None:
        access_token = generate_access_token(is_valid_user.user_name, is_valid_user.id, timedelta(minutes=20))
        return {"access_token": access_token, "token_type": "Bearer"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate user")


def authenticate_user(user_name: str, password: str, db: db_dependency):
    user_model = db.query(Users).filter(Users.user_name == user_name).first()
    if user_model is None:
        return None
    else:
        if bcrypt_context.verify(password, user_model.hashed_password):
            return user_model
    return None


def generate_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
