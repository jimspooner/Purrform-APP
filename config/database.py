from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DB_CONNECTION_URL = os.getenv('DB_CONNECTION_URL')
my_database_connection = (DB_CONNECTION_URL).replace("postgres://", "postgresql://", 1)

engine=create_engine(my_database_connection,
    echo=True
)

Base=declarative_base()

SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    try:
        db=SessionLocal()
        yield db
    finally:
        db.close()