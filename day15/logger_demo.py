import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
import colorlog
LOG_DIR=Path("logs")
LOG_FILE=LOG_DIR/"app.log"
MAX_BYTES=5*1024*1024
BACKUP_COUNT=10
LOG_FORMAT="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s"
DATE_FORMAT="%Y-%m-%d %H:%M:%S"
CONSOLE_FORMAT=colorlog.ColoredFormatter(
    "%(asctime)s | %(log_color)s%(levelname)-8s%(reset)s | %(filename)s:%(lineno)d | %(message)s",
    datefmt=DATE_FORMAT,
    log_colors={
        'DEBUG':'cyan',
        'INFO':'green',
        'WARNING':'yellow',
        'ERROR':'red',
        'CRITICAL':'bold_red',
    }
)
def setup_logger(name:str="app",level:int=logging.DEBUG)->logging.Logger:
    logger=logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)
    LOG_DIR.mkdir(exist_ok=True)
    file_handler=RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_fomatter=logging.Formatter(LOG_FORMAT,datefmt=DATE_FORMAT)
    file_handler.setFormatter(file_fomatter)
    console_handler=logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(CONSOLE_FORMAT)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
logger=setup_logger("app")
from fastapi import FastAPI,HTTPException
import uvicorn
app=FastAPI()
@app.get("/")
def read_root():
    logger.info("访问了根路径")
    return {"msg":"Hello World"}
@app.get("/login")
def login(username:str):
    logger.info(f"用户尝试登录：{username}")
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
        raise HTTPException(status_code=500,detail="内部错误")
if __name__=="__main__":
    uvicorn.run("logger_demo:app",host="127.0.0.1",port=8000,reload=True)