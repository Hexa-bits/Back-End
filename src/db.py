from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError

db_url = "sqlite:///database.db"

Base = declarative_base()
engine = create_engine(db_url)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)