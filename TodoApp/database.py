from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# replace SQLALCHEMY_DATABASE_URL with postgres db url
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'

# remove connect_args={'check_same_thread': False} for postgres
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autoflush=False, bind=engine, autocommit=False)

Base = declarative_base()