from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from schemas import UserOut
from crud.crud_user import get_user_list
from utils.response import success_resp
from utils.permission import RequireAdmin
from models import User
router=APIRouter(prefix="/api/v1/users",tags=["用户管理"])
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/list")
def list_users(
    page:int=Query(1,ge=1),
    page_size:int=Query(10,ge=1,le=100),
    db:Session=Depends(get_db),
    current_user:User=RequireAdmin
):
    result=get_user_list(db,page,page_size)
    items_pydantic=[UserOut.model_validate(u) for u in result["items"]]
    data={**result,"items":items_pydantic}
    return success_resp(data)