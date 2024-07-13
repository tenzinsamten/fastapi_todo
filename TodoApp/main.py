from fastapi import FastAPI
from .models import Base
from .database import engine
from .routers import auth, todos, users

app = FastAPI()


@app.get("/health")
async def get_healthy():
    return {'status': 'healthy'}

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
