import json
import os
DATA_FILE="students.json"
students=[]
def load_students():
    global students
    if not os.path.exists(DATA_FILE):
        print("数据文件不存在，已初始化空数据集。")
        return
    try:
        with open(DATA_FILE,"r",encoding="utf-8") as f:
            data=json.load(f)
            if isinstance(data,list):
                students.clear()
                students.extend(data)
                print(f"已从文件加载{len(students)}条学生记录。")
            else:
                print("数据文件格式错误，将使用空数据集。")
                students.clear()
    except (json.JSONDecodeError,IOError) as e:
        print(f"读取数据文件出错：{e}，将使用空数据集。")
        students.clear()
def save_students():
    try:
        with open(DATA_FILE,"w",encoding="utf-8") as f:
            json.dump(students,f,ensure_ascii=False,indent=2)
            print("数据已保存。")
    except IOError as e:
        print(f"保存数据失败：{e}")
def input_student_info():
    name=input("请输入姓名：").strip()
    if not name:
        print("姓名不能为空")
        return None
    student_id=input("请输入学号：").strip()
    if not student_id:
        print("学号不能为空")
        return None
    for s in students:
        if s['student_id']==student_id:
            print(f"学号{student_id}已存在，请重新输入")
            return None
    score_str=input("请输入分数(0-100)：").strip()
    try:
        score=int(score_str)
    except ValueError:
        print("分数必须是整数，请重新输入。")
        return None
    if score < 0 or score > 100:
        print("分数必须在0-100之间")
        return None
    class_name=input("请输入班级：").strip()
    if not class_name:
        print("班级不能为空")
        return None
    return{
        'name':name,
        'student_id':student_id,
        'score':score,
        'class':class_name
    }
def add_student():
    student=input_student_info()
    if student is None:
        return
    students.append(student)
    save_students()
    print(f"学生{student['name']}添加成功")
def delete_student():
    student_id=input("请输入要删除的学生学号：").strip()
    for i,s in enumerate(students):
        if s['student_id']==student_id:
            confirm=input(f"确认删除{s['name']}?(y/n)：")
            if confirm.lower() == 'y':
                del_student=students.pop(i)
                save_students()
                print(f"学生{del_student['name']}已删除")
            else:
                print("取消删除")
            return
    print(f"未找到学号为{student_id}的学生")
def print_student(s):
    print(f"学号：{s['student_id']} | 姓名：{s['name']} | 分数：{s['score']} | 班级：{s['class']}")
def search_by_id():
    student_id=input("请输入学号：").strip()
    for s in students:
        if s['student_id'] == student_id:
            print_student(s)
            return
    print(f"未找到学号为{student_id}的学生")
def search_by_name():
    name=input("请输入姓名关键词：").strip()
    results=[s for s in students if name in s['name']]
    if not results:
        print(f"未找到姓名包含'{name}'的学生")
        return
    print(f"找到{len(results)}个匹配学生：")
    for s in results:
        print_student(s)
def sort_students():
    if not students:
        print("暂无学生数据")
        return
    print("1. 按分数升序")
    print("2. 按分数降序")
    print("3. 按学号排序")
    choice=input("请输入选项：").strip()
    if choice == '1':
        sorted_list=sorted(students,key=lambda s:s['score'])
        print("按分数升序排列：")
    elif choice == '2':
        sorted_list=sorted(students,key=lambda s:s['score'],reverse=True)
        print("按分数降序排列：")
    elif choice == '3':
        sorted_list=sorted(students,key=lambda s:s['student_id'])
        print("按学号排序：")
    else:
        print("无效选项")
        return
    for s in sorted_list:
        print_student(s)
def show_all():
    if not students:
        print("暂无学生数据")
        return
    print(f"共{len(students)}个学生：")
    for s in students:
        print_student(s)
def main():
    print("="*30)
    print("学生成绩管理系统")
    print("="*30)
    while True:
        print("\n请选择操作")
        print("1. 新增学生")
        print("2. 删除学生")
        print("3. 查询学生(按学号)")
        print("4. 查询学生(按姓名)")
        print("5. 排序显示")
        print("6. 显示全部学生")
        print("0. 退出系统")
        choice=input("请输入选项：")
        if choice == '1':
            add_student()
        elif choice == '2':
            delete_student()
        elif choice == '3':
            search_by_id()
        elif choice == '4':
            search_by_name()
        elif choice == '5':
            sort_students()
        elif choice == '6':
            show_all()
        elif choice == '0':
            print("退出系统，再见！")
            break
        else:
            print("无效选项")
if __name__=="__main__":
    load_students()
    main()