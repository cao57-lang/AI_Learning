import math
from sqlalchemy import desc,asc
from sqlalchemy.orm import Query
from typing import Optional,Any,Dict,List
def paginate(
        query:Query,
        page:int=1,
        page_size:int=10,
        sort_by:Optional[str] = None,
        sort_order:str="asc"
)->Dict[str,Any]:
    if page_size>100:
        page_size=100
    if page<1:
        page=1
    total=query.count()
    pages=math.ceil(total/page_size) if total else 0
    if sort_by:
        col=getattr(query.column_descriptions[0]['entity'],sort_by,None)
        if col is not None:
            if sort_order.lower()=="desc":
                query=query.order_by(desc(col))
            else:
                query=query.order_by(asc(col))
    offset=(page-1)*page_size
    items=query.offset(offset).limit(page_size).all()
    return {
        "total":total,
        "page":page,
        "page_size":page_size,
        "pages":pages,
        "items":items
    }