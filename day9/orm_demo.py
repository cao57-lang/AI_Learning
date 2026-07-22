from sqlalchemy import (
    create_engine,Column,Integer,String,Text,Date,Enum,ForeignKey
)
from sqlalchemy.orm import(
    declarative_base,sessionmaker,relationship
)
from datetime import date
from sqlalchemy import func
DB_USER="root"
DB_PASSWORD="123456"
DB_HOST="localhost"
DB_PORT=3306
DB_NAME="ai_dataset_db"
DATABASE_URL=f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine=create_engine(DATABASE_URL,echo=True)
SessionLocal=sessionmaker(bind=engine)
Base=declarative_base()
class User(Base):
    __tablename__="user"
    id=Column(Integer,primary_key=True,autoincrement=True)
    username=Column(String(50),nullable=False,unique=True)
    password=Column(String(255),nullable=False)
    role=Column(Enum("annotator","admin"),nullable=False,default="annotator")
    def __repr__(self):
        return f"<User(id={self.id},username='{self.username}',role='{self.role}')>"
class Project(Base):
    __tablename__="project"
    id=Column(Integer,primary_key=True,autoincrement=True)
    name=Column(String(100),nullable=False)
    description=Column(Text)
    deadline=Column(Date)
    manager_id=Column(Integer,ForeignKey("user.id",ondelete="RESTRICT"),nullable=False)
    manager=relationship("User",backref="projects")
class Dataset(Base):
    __tablename__="dataset"
    id=Column(Integer,primary_key=True,autoincrement=True)
    project_id=Column(Integer,ForeignKey("project.id",ondelete="CASCADE"),nullable=False)
    total_samples=Column(Integer,nullable=False,default=0)
    labeled_samples=Column(Integer,nullable=False,default=0)
    label_type=Column(String(50))
    status=Column(Enum("pending","in_progress","completed"),default="pending")
    project=relationship("Project",backref="datasets")
def create_tables():
    Base.metadata.create_all(engine)
    print("数据库表已创建(若已存在则跳过)")
def main():
    create_tables()
    session=SessionLocal()
    try:
        user_to_add=[
            {"username": "zhangsan", "password": "123", "role": "annotator"},
            {"username": "admin_wang", "password": "123", "role": "admin"},
            {"username": "lisi", "password": "456", "role": "annotator"}
        ]
        added_users={}
        for user_data in user_to_add:
            existing_user=session.query(User).filter(
                User.username==user_data["username"]
            ).first()
            if existing_user:
                print(f":用户'{user_data['username']}'已存在，跳过插入。")
                added_users[user_data["username"]]=existing_user
            else:
                new_user=User(
                    username=user_data["username"],
                    password=user_data["password"],
                    role=user_data["role"]
                )
                session.add(new_user)
                added_users[user_data["username"]]=new_user
                print(f"用户'{user_data['username']}'创建成功。")
        session.commit()
        u1=added_users.get("zhangsan")
        u2=added_users.get("admin_wang")
        p1=Project(name="自动驾驶标注",deadline=date(2026,9,30),manager=u2)
        session.add(p1)
        session.commit()
        d1=Dataset(total_samples=10000,labeled_samples=3500,label_type="目标检测",status="in_progress",project=p1)
        session.add(d1)
        session.commit()
        print("所有用户：",session.query(User).all())
        datasets=session.query(Dataset).filter(
            Dataset.total_samples>5000,
            Dataset.status=="in_progress"
        ).all()
        print("筛选：",datasets)
        ds=session.query(Dataset).first()
        print("数据：",ds.id,"项目：",ds.project.name,"负责人：",ds.project.manager.username)
        us=session.query(Dataset).filter(Dataset.id==1).first()
        us.labeled_samples=6000
        session.commit()
        os=session.query(User).filter(User.username=="zhangsan").first()
        session.delete(os)
        session.commit()
        stats=session.query(
            Dataset.project_id,
            func.sum(Dataset.total_samples).label("总样本"),
            func.sum(Dataset.labeled_samples).label("已完成"),
        ).group_by(Dataset.project_id).all()
        for row in stats:
            print(row.project_id,row.总样本,row.已完成)
    except Exception as e:
        session.rollback()
        print("出错回滚：",e)
    finally:
        session.close()    
if __name__=="__main__":
    main()