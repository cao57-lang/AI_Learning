from pydantic import BaseModel
from typing import Any,Optional
class ApiResponse(BaseModel):
    code:int=200
    msg:str="success"
    data:Optional[Any]=None
def success_resp(data:Any=None,msg:str="success")->ApiResponse:
    return ApiResponse(code=200,msg=msg,data=data)
def fail_resp(code:int,msg:str)->ApiResponse:
    return ApiResponse(code=code,msg=msg)