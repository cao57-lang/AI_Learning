from fastapi import FastAPI,Depends
from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.orm import declarative_base,Session,sessionmaker
from pydantic import BaseModel,Field,EmailStr
from typing import Optional,Any
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import Request
import bcrypt
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
    __tablename__ = "user"
    id=Column(Integer,primary_key=True,autoincrement=True)
    username=Column(String(50),unique=True,nullable=False)
    hash_password=Column("password",String(255),nullable=False)
    email=Column(String(100),nullable=True)
    role=Column(String(20),default="annotator")
Base.metadata.create_all(engine)
def get_password_hash(password:str):
    salt=bcrypt.gensalt()
    hashed=bcrypt.hashpw(password.encode('utf-8'),salt)
    return hashed.decode('utf-8')
def verify_password(plain_password:str,hashed_password:str):
    return bcrypt.checkpw(plain_password.encode('utf-8'),hashed_password.encode('utf-8'))

class ApiResponse(BaseModel):
    code:int=Field(200)
    msg:str=Field("请求成功")
    data:Any=Field(None)
class BizException(Exception):
    def __init__(self,msg:str,code:int=4000):
        self.msg=msg
        self.code=code
        super().__init__(msg)
def success_resp(data:Any=None,msg:str="请求成功"):
    return ApiResponse(code=200,msg=msg,data=data)
def Fail_resp(code:int,msg:str):
    return ApiResponse(code=code,msg=msg)
class UserRegister(BaseModel):
    username:str=Field(...,min_length=3,max_length=20)
    password:str=Field(...,min_length=6,max_length=32)
    email:Optional[EmailStr]=None
app=FastAPI()
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request:Request,exc:RequestValidationError):
    first_error=exc.errors()[0] if exc.errors() else {"msg":"参数错误"}
    msg=first_error.get("msg","参数格式不正确")
    return JSONResponse(status_code=200,content=Fail_resp(422,f"参数校验失败{msg}").model_dump())    
@app.exception_handler(BizException)
async def biz_exception_handler(request:Request,exc:BizException):
    return JSONResponse(status_code=200,content=Fail_resp(exc.code,exc.msg).model_dump())
@app.exception_handler(Exception)
async def unknown_exception_handler(request:Request,exc:Exception):
    return JSONResponse(status_code=200,content=Fail_resp(500,"服务器内部错误").model_dump())
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.post("/auth/register")
def register(req:UserRegister,db:Session=Depends(get_db)):
    existing=db.query(User).filter(User.username==req.username).first()
    if existing:
        raise BizException("该账号已被注册",code=4001)
    hashed_pw=get_password_hash(req.password)
    new_user=User(username=req.username,hash_password=hashed_pw,email=req.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return success_resp(
        data={"id":new_user.id,"username":new_user.username,"email":new_user.email,"role":new_user.role},
        msg="注册成功"
    )