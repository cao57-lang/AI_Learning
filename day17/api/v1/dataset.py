from fastapi import APIRouter,Depends,Query
from sqlalchemy.orm import Session
from typing import Optional
from database import SessionLocal
from schemas import DatasetOut
from crud.crud_dataset import get_dataset_list
from utils.response import success_resp,ApiResponse
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
    sort_order:str=Query("desc",regex="^(asc|desc)$",description="排序方向"),
    db:Session=Depends(get_db),
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