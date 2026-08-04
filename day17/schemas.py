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