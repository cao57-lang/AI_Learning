from fastapi import FastAPI
from api.v1.dataset import router as dataset_router
from api.v1 import auth,user
from database import engine, Base
from models import Dataset  # 确保模型被导入
Base.metadata.create_all(bind=engine)
app=FastAPI()
app.include_router(dataset_router)
app.include_router(auth.router)
app.include_router(user.router)
if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app",host="127.0.0.1",port=8000,reload=True)