from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from schemas import TokenRespose
from utils.jwt_util import create_access_token
from utils.response import success_resp,fail_resp
import bcrypt
router=APIRouter(prefix="/api/v1/auth",tags=["认证"])
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.post("/login",response_model=TokenRespose)
def login(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=db.query(User).filter(User.username==form_data.username).first()
    if not user:
        raise HTTPException(status_code=400,detail="账号不存在")
    if not bcrypt.checkpw(form_data.password.encode('utf-8'),user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=400,detail="密码错误")
    access_token=create_access_token(data={"user_id":user.id,"role":user.role})
    return TokenRespose(access_token=access_token,token_type="bearer")