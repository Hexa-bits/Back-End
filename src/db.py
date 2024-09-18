from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

db_url = "sqlite:///database.db"
engine = None

Session = None
Base = declarative_base()

def init_db():
    global engine, Session
    if engine is None:
        engine = create_engine(db_url)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()  

def create_table(table_name):
    table = Base.metadata.tables.get(table_name)
    if table is not None:
        table.create(engine)
    else:
        print(f'{table_name} no existe')
