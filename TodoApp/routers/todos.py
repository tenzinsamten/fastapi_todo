from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Todos
from typing import Annotated
from starlette import status
from .auth import get_current_user

router = APIRouter(
    prefix='/todos',
    tags=['TODOS']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0)
    complete: bool


db_dependency = Annotated[Session, Depends(get_db)]

user_depency = Annotated[dict, Depends(get_current_user)]


@router.get("", status_code=status.HTTP_200_OK)
async def read_all_todos(user: user_depency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication failed")
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_depency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication failed")
    new_todo = Todos(**todo_request.model_dump())
    new_todo.owner_id = user.get('id')
    db.add(new_todo)
    db.commit()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo_by_id(user: user_depency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication failed")
    todo = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=404, detail='Not found')


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_id: int, todo_request: TodoRequest):
    updated_todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if updated_todo is not None:
        updated_todo.title = todo_request.title
        updated_todo.description = todo_request.description
        updated_todo.priority = todo_request.priority
        updated_todo.complete = todo_request.complete
        db.add(updated_todo)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail='Todo not found')


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int):
    deleted_todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if deleted_todo is not None:
        db.delete(deleted_todo)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail='Todo not found')
