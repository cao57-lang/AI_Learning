from sqlalchemy import Column,Integer,String,DateTime,Enum,func,ForeignKey
from database import Base
class Dataset(Base):
    __tablename__="dataset"
    id=Column(Integer,primary_key=True,autoincrement=True)
    total_samples=Column(Integer,nullable=False,default=0)
    labeled_samples=Column(Integer,nullable=False,default=0)
    label_type=Column(String(50))
    status=Column(Enum("pending","in_progress","completed"),default="pending")
    