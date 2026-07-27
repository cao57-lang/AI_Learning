from fastapi import FastAPI,Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.orm import declarative_base,sessionmaker,Session
from pydantic import BaseModel,Field
from typing import Any,Optional
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import Request
import bcrypt
from jose import JWTError,jwt
from datetime import datetime,timedelta,timezone
DB_USER="root"
DB_PASSWORD="123456"
DB_HOST="localhost"
DB_PORT=3306
DB_NAME="ai_dataset_db"
DATABASE_URL=f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine=create_engine(DATABASE_URL,echo=True)
Sessionlal=sessionmaker(bind=engine)
Base=declarative_base()
class User(Base):
    __tablename__="user"
    id=Column(Integer,primary_key=True,autoincrement=True)
    username=Column(String(50),unique=True,nullable=False)
    hashed_password=Column("password",String(255),nullable=False)
    email=Column(String(100),nullable=True)
    role=Column(String(20),default="annotator")
Base.metadata.create_all(engine)
def get_password_hash(password:str):
    salt=bcrypt.gensalt()
    hashed=bcrypt.hashpw(password.encode('utf-8'),salt)
    return hashed.decode('utf-8')
def verify_password(plain_password:str,hashed_password:str):
    return bcrypt.checkpw(plain_password.encode('utf-8'),hashed_password.encode('utf-8'))
SECRET_KEY="your-secret-key-keep-it-safe"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
def create_access_token(data:dict,expires_delta:Optional[timedelta]=None):
    to_encode=data.copy()
    expire=datetime.now(tz=timezone.utc)+(expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt
class ApiResponse(BaseModel):
    code:int=Field(200)
    msg:str=Field("请求成功")
    data:Any=Field(None)
class BizException(Exception):
    def __init__(self,msg:str,code:int=4000):
        self.msg=msg
        self.code=code
        super().__init__(msg)
def success_resp(data:Any=None,msg:str="请求成功",code:int=200):
    return ApiResponse(code=code,msg=msg,data=data)
def fail_resp(code:int,msg:str)->ApiResponse:
    return ApiResponse(code=code,msg=msg)
app=FastAPI()
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request:Request,exc:RequestValidationError):
    first_error=exc.errors()[0] if exc.errors else {"msg":"参数错误"}
    msg=first_error.get("msg","参数格式不正确")
    return JSONResponse(status_code=200,content=fail_resp(422,f"参数校验失败:{msg}").model_dump())
@app.exception_handler(BizException)
async def biz_exception_handler(request:Request,exc:BizException):
    return JSONResponse(status_code=200,content=fail_resp(exc.code,exc.msg).model_dump())
@app.exception_handler(Exception)
async def unkown_exception_handler(request:Request,exc:Exception):
    return JSONResponse(status_code=200,content=fail_resp(500,"服务器内部错误").model_dump())
def get_db():
    db=Sessionlal()
    try:
        yield db
    finally:
        db.close()
@app.post("/auth/login")
def login(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=db.query(User).filter(User.username==form_data.username).first()
    if not user:
        raise BizException(msg="账号不存在",code=4001)
    if not verify_password(form_data.password,user.hashed_password):
        raise BizException(msg="密码错误",code=4002)
    access_token=create_access_token(
        data={"sub":str(user.id),"role":user.role}
    )
    return success_resp(
        data={"access_token":access_token,"token_type":"bearer"},
        msg="登录成功"
    )