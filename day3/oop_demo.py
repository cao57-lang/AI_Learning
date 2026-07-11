class Student:
    def __init__(self,student_id,name,class_name):
        self.student_id=student_id
        self.name=name
        self.class_name=class_name
        self.__scores=[]
    def add_score(self,score):
        if 0<=score<=100:
            self.__scores.append(score)
            print(f"已为{self.name}添加分数：{score}")
        else:
            print(f"分数{score}无效，必须在0-100之间")
    def average_score(self):
        if not self.__scores:
            return 0
        return sum(self.__scores)/len(self.__scores)
    def print_info(self):
        print(f"学号：{self.student_id} | 姓名：{self.name} | 班级：{self.class_name} | 平均分：{self.average_score():.1f}")
class Teacher:
    def __init__(self,teacher_id,name):
        self.teacher_id=teacher_id
        self.name=name
        self.__courses=[]
        self.__students=set()
    def add_course(self,course):
        if course not in self.__courses:
            self.__courses.append(course)
            print(f"教师{self.name}已关联课程：{course.course_name}")
    def bind_student(self,student):
        self.__students.add(student)
    def print_teaching_list(self):
        print(f"\n教师：{self.name}(工号：{self.teacher_id})")
        print(f"授课课程：")
        for c in self.__courses:
            print(f"-{c.course_name}")
        print(f"所带学生：{len(self.__students)}人")
        for s in self.__students:
            print(f"-{s.name}")
class Course:
    def __init__(self,course_id,course_name,teacher):
        self.course_id=course_id
        self.course_name=course_name
        self.teacher=teacher
        self.__students=[]
        teacher.add_course(self)
    def add_student(self,student):
        if student not in self.__students:
            self.__students.append(student)
            self.teacher.bind_student(student)
            print(f"学生{student.name}已选课：{self.course_name}")
    def print_roster(self):
        print(f"\n课程：{self.course_name}(编号：{self.course_id})")
        print(f"授课教师：{self.teacher.name}")
        print(f"选课学生：{len(self.__students)}人")
        for s in self.__students:
            print(f"-{s.name} | {s.class_name} | 平均分：{s.average_score():.1f}")
if __name__=="__main__":
    print("="*40)
    print("师生课程关系管理系统")
    print("="*40)
    t1=Teacher("T001","李老师")
    print("\n【创建老师】")
    t1.print_teaching_list()
    print("\n【创建学生】")
    s1=Student("s001","张三","计算机1班")
    s2=Student("s002","李四","计算机1班")
    s3=Student("s003","王五","计算机2班")
    print("\n【添加分数】")
    s1.add_score(85)
    s1.add_score(92)
    s2.add_score(78)
    s2.add_score(88)
    s3.add_score(95)
    print("\n【创建课程】")
    c1=Course("c101","Python编程",t1)
    c2=Course("c102","数据分析",t1)
    print("\n【学生选课】")
    c1.add_student(s1)
    c1.add_student(s2)
    c2.add_student(s2)
    c2.add_student(s3)
    print("\n"+"="*40)
    print("完整班级数据")
    print("="*40)
    print("\n【学生信息】")
    for s in [s1,s2,s3]:
        s.print_info()
    print("\n【课程花名册】")
    c1.print_roster()
    c2.print_roster()
    print("\n【教师授课清单】")
    t1.print_teaching_list()