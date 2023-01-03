from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
# from dotenv import load_dotenv, find_dotenv

# load_dotenv(find_dotenv())

DATABASE_URL = os.getenv('DATABASE_URL')
my_database_connection = (DATABASE_URL).replace("postgres://", "postgresql://", 1)

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