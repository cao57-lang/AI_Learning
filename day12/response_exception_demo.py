from fastapi import FastAPI,Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field
from typing import Any,Optional
class ApiResponse(BaseModel):
    code:int=Field(200,description="业务状态码，200成功，其它失败")
    msg:str=Field("请求成功",description="提示信息")
    data:Any=Field(None,description="返回数据，可以是对象、列表、null")
class BizException(Exception):
    def __init__(self,msg:str,code:int=4000):
        self.msg=msg
        self.code=code
        super().__init__(msg)
def success_resp(data:Any=None,msg:str="请求成功")->ApiResponse:
    return ApiResponse(code=200,msg=msg,data=data)
def fail_resp(code:int,msg:str,data:Any=None)->ApiResponse:
    return ApiResponse(code=code,msg=msg,data=data)
app=FastAPI()
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request:Request,exc:RequestValidationError):
    errors=exc.errors()
    first_error=errors[0] if errors else {"msg":"参数错误"}
    msg=first_error.get("msg","参数格式不正确")
    return JSONResponse(
        status_code=200,
        content=fail_resp(code=422,msg=f"参数校验失败:{msg}").model_dump()
    )
@app.exception_handler(BizException)
async def biz_exception_handler(request:Request,exc:BizException):
    return JSONResponse(
        status_code=200,
        content=fail_resp(code=exc.code,msg=exc.msg).model_dump()
    )
@app.exception_handler(Exception)
async def unknow_exception_handler(request:Request,exc:Exception):
    return JSONResponse(
        status_code=200,
        content=fail_resp(code=500,msg="服务器内部错误，请稍后重试").model_dump()
    )
class CreateUserRep(BaseModel):
    username:str=Field(...,min_length=3)
    password:str=Field(...,min_length=6)
EXISTING_USERS=["admin","zhangsan"]
@app.post("/user/register")
def register(rep:CreateUserRep):
    if rep.username in EXISTING_USERS:
        raise BizException(f"账号{rep.username}已存在",code=4001)
    return success_resp(data={"username":rep.username},msg="注册成功")
@app.get("/user/info")
def get_user_info(username:str="default"):
    return success_resp(data={"username":username,"role":"annotator"})
@app.get("/error/zero")
def zero_division_error():
    1/0
    return success_resp()