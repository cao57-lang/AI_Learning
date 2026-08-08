from datetime import datetime,timedelta,timezone
from jose import jwt,JWTError
from typing import Optional,Dict
SECRET_KEY="your-secret-key-keep-it-secret"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
def create_access_token(data:dict):
    to_encode=data.copy()
    expire= expire=datetime.now(tz=timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
def decode_access_token(token:str):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
