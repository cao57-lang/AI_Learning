from sqlalchemy.orm import Session
from typing import Optional
from models import Dataset
from utils.pagination import paginate
def get_dataset_list(
        db:Session,
        page:int=1,
        page_size: int = 10,
        label_type:Optional[str]=None,
        sort_by:Optional[str] = "id",
        sort_order:str="desc"
):
    query=db.query(Dataset)
    if label_type:
        query=query.filter(Dataset.label_type.like(f"%{label_type}%"))
    return paginate(
        query=query,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )