import uuid
import contextvars
from fastapi  import FastAPI,Depends,Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from logger_config import logger,trace_id_var
import uvicorn
async def set_trace_id(request:Request):
    trace_id=str(uuid.uuid4())[:8]
    trace_id_var.set(trace_id)
    request.state.trace_id=trace_id
class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request:Request, call_next):
        response=await call_next(request)
        if 200<=response.status_code<300:
            content_type=response.headers.get("content-type","")
            if "application/json" in content_type:
                body=b""
                async for chunk in response.body_iterator:
                    body+=chunk
                import json
                data=json.loads(body)
                if isinstance(data,dict):
                    data["trace_id"]=request.state.trace_id
                headers=dict(response.headers)
                headers.pop("content-length",None)
                headers.pop("transfer-encoding", None)
                headers.pop("content-encoding", None)
                return JSONResponse(
                    content=data,
                    status_code=response.status_code,
                    headers=headers,
                )
        return response
app=FastAPI(dependencies=[Depends(set_trace_id)])
app.add_middleware(TraceIdMiddleware)
@app.get("/")
def read_root():
    logger.info("访问了根路径")
    return {"msg":"Hello World"}
@app.get("/login")
def login(username:str):
    logger.info(f"用户尝试登录{username}")
    if username=="admin":
        logger.warning("检测到管理员登录尝试")
        return {"token":"fake-token"}
    return {"msg":"普通用户登录"}
@app.get("/error")
def trigger_error():
    try:
        1/0
    except ZeroDivisionError as e:
        logger.error("发生除零异常",exc_info=True)
        return JSONResponse(status_code=500,content={"detail":"内部错误","trace_id":trace_id_var.get()})
if __name__=="__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8000,reload=True)    