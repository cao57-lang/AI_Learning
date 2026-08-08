from sqlalchemy import Column,Integer,String,DateTime,Enum,func,ForeignKey
from database import Base
class Dataset(Base):
    __tablename__="dataset"
    id=Column(Integer,primary_key=True,autoincrement=True)
    total_samples=Column(Integer,nullable=False,default=0)
    labeled_samples=Column(Integer,nullable=False,default=0)
    label_type=Column(String(50))
    status=Column(Enum("pending","in_progress","completed"),default="pending")
class User(Base):
    __tablename__="user"
    id=Column(Integer,primary_key=True,autoincrement=True)
    username=Column(String(50),unique=True,nullable=False)
    hashed_password=Column("password",String(255),nullable=False)
    email=Column(String(100),nullable=True)
    role=Column(String(20),default="annotator")