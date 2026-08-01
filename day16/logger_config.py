import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import colorlog
import contextvars
trace_id_var:contextvars.ContextVar[str]=contextvars.ContextVar("trace_id",default="-")
class TraceIdFilter(logging.Filter):
    def filter(self, record:logging.LogRecord)->bool:
        record.trace_id=trace_id_var.get() or "-"
        return True
LOG_DIR=Path("logs")
LOG_FILE=LOG_DIR/"app.log"
MAX_BYTES=5*1024*1024
BACKUP_COUNT=10
LOG_FORMAT="%(asctime)s | %(levelname)-8s | %(trace_id)s | %(filename)s:%(lineno)d | %(message)s"
DATE_FORMAT="%Y-%m-%d %H:%M:%S"
CONSOLE_FORMAT=colorlog.ColoredFormatter(
    "%(asctime)s | %(log_color)s%(levelname)-8s%(reset)s | %(trace_id)s | %(filename)s:%(lineno)d | %(message)s",
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
        LOG_FILE,maxBytes=MAX_BYTES,backupCount=BACKUP_COUNT,encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_formatter=logging.Formatter(LOG_FORMAT,datefmt=DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(TraceIdFilter())
    console_handler=logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(CONSOLE_FORMAT)
    console_handler.addFilter(TraceIdFilter())
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
logger=setup_logger("app")