from pydantic import BaseModel,Field,ValidationError
from typing import Optional,List
from datetime import date
class UserCreate(BaseModel):
    username:str=Field(...,min_length=3,max_length=50,description="用户名")
    password:str=Field(...,min_length=6,max_length=20,description="密码")
    email:Optional[str]=Field(None,pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",description="邮箱")
    role:str=Field("annotator",description="角色")
class UserOut(BaseModel):
    id:int
    username:str
    email:Optional[str]
    role:str
    model_config={'from_attributes':True}
class ProjectOut(BaseModel):
    id:int
    name:str
    description:Optional[str]=None
    deadline:Optional[date]=None
    manager_id:int
    datasets:List['DatasetOut']=[]
    model_config={'from_attributes':True}
class DatasetOut(BaseModel):
    id:int
    project_id:int
    total_samples:int
    labeled_samples:int
    label_type:Optional[str]=None
    status:str
    model_config={'from_attributes':True}
def main():
    print("="*40)
    print("Pydantic数据模型演示")
    print("="*40)
    try:
        user=UserCreate(username="zhangsan",password="123456",email="zhang@example.com",role="annotator")
        print("创建用户成功：",user)
        print("转字典：",user.model_dump())
    except ValidationError as e:
        print("校验失败：",e.errors())
    print("\n--- 非法参数测试 ---")
    try:
        user_bad=UserCreate(username="ab",password="123",email="notanemail")
    except ValidationError as e:
        print("非法参数被拦截：")
        for error in e.errors():
            print(f" - 字段{error['loc'][0]}:{error['msg']}")
    print("\n--- ORM对象转 JSON 演示 ---")
    orm_user={"id":1,"username":"zhangsan","email":"z@test.com","role":"annotator"}
    user_out=UserOut.model_validate(orm_user)
    print("转换后的 UserOut：",user_out)
    print("转 JSON：",user_out.model_dump_json(indent=2))
    print("\n--- 嵌套模型演示 ---")
    ds1=DatasetOut(id=1, project_id=1, total_samples=1000, labeled_samples=200, label_type="目标检测", status="in_progress")
    ds2=DatasetOut(id=2, project_id=1, total_samples=500, labeled_samples=500, label_type="分类", status="completed")
    proj=ProjectOut(id=1, name="自动驾驶标注", manager_id=1, datasets=[ds1, ds2])
    print("项目输出：",proj.model_dump_json(indent=2))
if __name__=="__main__":
    main()