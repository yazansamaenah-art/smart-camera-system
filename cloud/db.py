import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
DATABASE_URL=os.getenv('DATABASE_URL','sqlite:///./smartpole.db')
engine=create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal=sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
def init_db(): Base.metadata.create_all(bind=engine)
