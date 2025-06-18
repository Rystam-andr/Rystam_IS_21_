from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    type = Column(String)
    date_added = Column(DateTime, default=datetime.datetime.utcnow)
    file_path = Column(String)