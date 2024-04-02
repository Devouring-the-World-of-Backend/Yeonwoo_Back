import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_url=os.environ.get("DATABASE_URL","sqlite:///mydatabase.db")

engine=create_engine(db_url)

Session=sessionmaker(bind=engine)
session=Session()