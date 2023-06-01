from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey

engine = create_engine('postgresql://postgres:Tehn89tehn@127.0.0.1:5431/ads')

Session = sessionmaker(bind=engine)
Base = declarative_base(bind=engine)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=True, unique=True, index=True)
    password = Column(String, nullable=True)
    creationdate = Column(DateTime, server_default=func.now())
class AdsTable(Base):
    __tablename__ = 'adstable'

    id = Column(Integer, primary_key=True, autoincrement=True)
    head = Column(String, nullable=True, index=True)
    description = Column(String)
    creationdate = Column(DateTime, server_default=func.now())
    username = Column(Integer, ForeignKey('user.id'), nullable=True)

    user = relationship(User, backref='adstable')



Base.metadata.create_all()