from fastapi import APIRouter,Depends,Query,HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import SessionLocal
from schemas import DatasetOut,DatasetCreat
from crud.crud_dataset import get_dataset_list,create_dataset,delete_dataset
from utils.response import success_resp,ApiResponse
from utils.permission import RequireAdmin,REquireLogin
from models import User,Dataset
router=APIRouter(prefix="/api/v1/dataset",tags=["dataset"])
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/list",response_model=ApiResponse)
def list_dataset(
    page:int=Query(1,ge=1,description="页码"),
    page_size:int=Query(10,ge=1,le=100,description="每页条数，最大100"),
    label_type:Optional[str]=Query(None,description="数据集名称(模糊搜索)"),
    sort_by:Optional[str]=Query("id",description="排序字段"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="排序方向"),
    db:Session=Depends(get_db),
    current_user:User=REquireLogin
):
    result=get_dataset_list(
        db=db,
        page=page,
        page_size=page_size,
        label_type=label_type,
        sort_by=sort_by,
        sort_order=sort_order
    )
    items_orm=result["items"]
    items_pydantic = [DatasetOut.model_validate(item) for item in items_orm]
    data={
        "total":result["total"],
        "page":result["page"],
        "page_size":result["page_size"],
        "pages":result["pages"],
        "items":items_pydantic
    }
    return success_resp(data)
@router.get("/{dataset_id}",response_model=ApiResponse)
def get_dataset(
    dataset_id:int,
    db:Session=Depends(get_db),
    current_user:User=REquireLogin
):
    dataset=db.query(Dataset).filter(Dataset.id==dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404,detail="数据集不存在")
    return success_resp(DatasetOut.model_validate(dataset))
@router.post("/create",response_model=ApiResponse)
def create_dataset_api(
    dataset_in:DatasetCreat,
    db:Session=Depends(get_db),
    current_user:User=RequireAdmin
):
    dataset=create_dataset(db,dataset_in)
    return success_resp(DatasetOut.model_validate(dataset))
