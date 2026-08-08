from pydantic import BaseModel,Field
from typing import Optional
from datetime import datetime
class DatasetOut(BaseModel):
    id:int
    total_samples:int
    labeled_samples:int
    label_type:Optional[str]=None
    status:str
    model_config={'from_attributes':True}
class TokenRespose(BaseModel):
    access_token:str
    token_type:str
class DatasetCreat(BaseModel):
    total_samples:int
    labeled_samples:int=0
    label_type:Optional[str]=None
    status:str="pending"
class UserOut(BaseModel):
    id:int
    username:str
    email:Optional[str]=None
    role:str
    model_config={'from_attributes':True}