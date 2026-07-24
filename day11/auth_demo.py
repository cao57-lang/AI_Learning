from fastapi import FastAPI,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from sqlalchemy import create_engine,Column,Integer,String,Enum
from sqlalchemy.orm import declarative_base,sessionmaker,Session
from pydantic import BaseModel
import bcrypt
from jose import JWTError,jwt
from datetime import datetime,timedelta,timezone
from typing import Optional
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
    username=Column(String(50),unique=True,nullable=False)
    hashed_password=Column("password",String(255),nullable=False)
    role=Column(Enum("annotator","admin"),nullable=False,default="annotator")
Base.metadata.create_all(engine)
class ToKen(BaseModel):
    access_token:str
    token_type:str
class UserOut(BaseModel):
    id:int
    username:str
    role:str
    model_config={'from_attributes':True}
def get_password_hash(password: str) -> str:
    salt=bcrypt.gensalt()
    hashed=bcrypt.hashpw(password.encode('utf-8'),salt)
    return hashed.decode('utf-8')
def verify_password(plain_password:str,hashed_password:str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'),hashed_password.encode('utf-8'))
SECRET_KEY="your-secret-key-keep-it-safe"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
def create_access_token(data:dict,expires_delta:Optional[timedelta]=None)->str:
    to_encode=data.copy()
    expire=datetime.now(tz=timezone.utc)+(expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp":expire})
    encode_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt
app=FastAPI()
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/login")
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db))->User:
    credentials_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate":"Bearer"},
    )
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id_str:int=payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id=int(user_id_str)
    except JWTError:
        raise credentials_exception
    user=db.query(User).filter(User.id==user_id).first()
    if user is None:
        raise credentials_exception
    return user
def require_admin(current_user:User=Depends(get_current_user)):
    if current_user.role !="admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="权限不足")
    return current_user
@app.post("/login",response_model=ToKen)
def login(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=db.query(User).filter(User.username==form_data.username).first()
    if not user or not verify_password(form_data.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate":"Bearer"},
        )
    access_token=create_access_token(data={"sub":str(user.id),"role":user.role})
    return {"access_token": access_token,"token_type": "bearer"}
@app.get("/users/me",response_model=UserOut)
def read_users_me(current_user:User=Depends(get_current_user)):
    return current_user
@app.get("/admin/data")
def admin_data(admin_user:User=Depends(require_admin)):
    return {"message": f"欢迎管理员{admin_user.username}","data":"这是敏感数据"}
if __name__=="__main__":
    db=SessionLocal()
    if not db.query(User).filter(User.username=="admin").first():
        db.add(User(username="admin",hashed_password=get_password_hash("admin123"),role="admin"))
        db.add(User(username="annotator1",hashed_password=get_password_hash("123456"),role="annotator"))
        db.commit()
        print("测试用户已插入")
    db.close()