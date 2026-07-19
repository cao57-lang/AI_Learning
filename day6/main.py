from fastapi import FastAPI
app=FastAPI()
@app.get("/")
def read_root():
    return {"message":"欢迎来到FastAPI学习之旅！"}
students_db={
     "s001": {"name": "张三", "class_name": "计算机1班", "score": 88.5},
    "s002": {"name": "李四", "class_name": "计算机1班", "score": 83.0},
    "s003": {"name": "王五", "class_name": "计算机2班", "score": 95.0},
}
@app.get("/student/{stu_id}")
def get_student(stu_id:str):
    student=students_db.get(stu_id)
    if student:
        return {"stu_id":stu_id,"info":student}
    else:
        return {"error":f"未找到学号为{stu_id}的学生"}
@app.get("/query")
def query_student(name:str,class_name:str):
    return {
        "message":f"查询参数：姓名={name}，班级={class_name}",
        "name":name,
        "class":class_name
    }
