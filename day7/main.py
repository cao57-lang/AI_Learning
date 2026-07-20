from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from typing import Optional
import uuid
app=FastAPI(title="Tode API",description="待办事项 CRUD 示例")
class TodoCreate(BaseModel):
    title:str=Field(...,min_length=1,description="代办标题")
    content:Optional[str]=Field(None,description="详细内容")
    completed:bool=Field(False,description="是否完成")
class Todo(TodoCreate):
    id:str=Field(...,description="唯一标识符")
todos_db:list[Todo]=[]
example_todo=Todo(
    id=str(uuid.uuid4()),
    title="学习 FastAPI",
    content="完成 CRUD 接口开发",
    completed=False
)
todos_db.append(example_todo)
@app.post("/todo",response_model=Todo,status_code=201)
def create_todo(todo:TodoCreate):
    new_todo=Todo(
        id=str(uuid.uuid4()),
        **todo.model_dump()
    )
    todos_db.append(new_todo)
    return new_todo
@app.get("/todo",response_model=list[Todo])
def get_all_todos():
    return todos_db
@app.get("/todo/{todo_id}",response_model=Todo)
def get_todo(todo_id:str):
    for todo in todos_db:
        if todo.id ==todo_id:
            return todo
    raise HTTPException(status_code=404,detail=f"待办{todo_id}不存在")
@app.put("/todo/{todo_id}",response_model=Todo)
def update_todo(todo_id:str,updated:TodoCreate):
    for i,todo in enumerate(todos_db):
        if todo.id==todo_id:
            new_todo=Todo(
                id=todo_id,
                **updated.model_dump()
            )
            todos_db[i]=new_todo
            return new_todo
    raise HTTPException(status_code=404,detail=f"待办{todo_id}不存在")
@app.delete("/todo/{todo_id}",status_code=204)
def delete_todo(todo_id:str):
    for i ,todo in enumerate(todos_db):
        if todo.id == todo_id:
            del todos_db[i]
            return
    raise HTTPException(status_code=404,detail=f"待办{todo_id}不存在")
