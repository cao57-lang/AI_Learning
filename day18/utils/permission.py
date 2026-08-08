from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from utils.jwt_util import decode_access_token
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login",auto_error=False)
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
async def get_current_user(
        token:str=Depends(oauth2_scheme),
        db:Session=Depends(get_db)
):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate":"Bearer"},
        )
    payload=decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证令牌无效或已过期",
            headers={"WWW-Authenticate":"Bearer"},
        )
    user_id=payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="令牌缺少用户标识")
    user=db.query(User).filter(User.id==user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="用户不存在")
    return user
async def require_admin(current_user:User=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅管理员可执行此操作"
        )
    return current_user
REquireLogin=Depends(get_current_user)
RequireAdmin=Depends(require_admin)