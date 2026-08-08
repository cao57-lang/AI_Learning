from sqlalchemy.orm import Session
from models import User
from utils.pagination import paginate
def get_user_list(db:Session,page:int,page_size:int):
    query=db.query(User)
    return paginate(query,page=page,page_size=page_size)