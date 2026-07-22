\# Day9 学习日志：SQLAlchemy ORM 数据库映射



\## 一、今日完成



\-  安装 SQLAlchemy 和 pymysql

\-  封装数据库引擎 `create\_engine` 和会话工厂 `sessionmaker`

\-  定义三个 ORM 实体类：`User`、`Project`、`Dataset`

\-  使用 `Base.metadata.create\_all()` 自动建表

\-  实现 ORM 增删改查：add/commit、query/filter、update、delete

\-  实现联表查询和聚合统计

\-  添加“先查询再插入”的防重复检查逻辑

\-  修正多个拼写和逻辑错误，代码可重复运行

\-  深入理解 pymysql 与 engine 的关系、模型列映射规则、Session 工厂模式



\## 二、核心概念



\### 1. pymysql 与 engine 的关系



| 组件 | 角色 | 职责 |

|------|------|------|

| pymysql | 驱动（工人） | 底层 TCP/IP 通信，发送 SQL 包，接收数据 |

| engine | 引擎（工头） | 连接池管理、SQL 执行调度、统一接口 |



\-  连接字符串 `mysql+pymysql://...` 中的 `pymysql` 指定了底层驱动

\-  切换数据库只需改连接字符串，代码不变



\### 2. 模型类属性与数据库列的关系



| 情况 | 结果 |

|------|------|

| 模型有字段，表无列 | 插入报错 `Unknown column`，查询不报错但值为 None |

| 表有列，模型无字段 | 插入该列填 NULL（或报错），代码无法访问该列 |

| 属性名 ≠ 列名 | 可通过 `Column("列名")` 显式映射，Python 名和 SQL 名可不同 |



\### 3. SessionLocal vs session



\-   \*\*SessionLocal\*\*：会话工厂，全局一个，负责生产会话

\-   \*\*session\*\*：具体会话实例，每次操作新开一个，用完即关

\-   \*\*原因\*\*：保证事务隔离、线程安全、避免数据污染



\### 4. ORM 关系映射 `relationship`



\-   `relationship("User", backref="projects")`：定义对象间关联

\-   `backref`：反向引用，自动在对方类添加属性

\-   \*\*好处\*\*：`project.manager` 直接拿到 User 对象，`user.projects` 拿到项目列表

\-   \*\*注意\*\*：relationship 是 ORM 层面的，不是数据库外键



\### 5. 防重复插入模式



```python

existing = session.query(User).filter(User.username == name).first()

if existing:

&#x20;   # 已存在，复用

&#x20;   added\[name] = existing

else:

&#x20;   # 不存在，新建

&#x20;   new\_user = User(username=name, ...)

&#x20;   session.add(new\_user)

&#x20;   added\[name] = new\_user

```



\-   “先查询，再插入”比“直接插入，捕获异常”更直观清晰

\-   使用字典 `{}` 而非列表 `\[]` 存放结果，方便通过用户名快速定位



\### 6. 字典 vs 列表 的选择



| 特性 | 列表 `\[]` | 字典 `{}` |

|------|-----------|-----------|

| 访问方式 | 位置索引 `\[0]` | 键索引 `\["key"]` |

| 查找速度 | 需遍历 | 直接定位 |

| 适用场景 | 顺序存储 | 需要通过唯一标识快速查找 |



\### 7. 字符串从“值”变为“键”



```python

user\_data = {"username": "zhangsan"}  # "zhangsan" 是值

added\_users\[user\_data\["username"]] = new\_user  # "zhangsan" 变成键

```



\-   同一字符串在不同上下文中扮演不同角色

\-   这是一种常见的“数据重组”或“索引”操作



\### 8. 事务与回滚



```python

try:

&#x20;   # 所有操作...

&#x20;   session.commit()  # 统一提交

except Exception as e:

&#x20;   session.rollback()  # 出错回滚

finally:

&#x20;   session.close()  # 关闭会话

```



\-   `commit()`：将所有操作打包成事务提交

\-   `rollback()`：撤销事务中所有未提交的操作

\-   `close()`：释放连接资源，防止泄漏



\### 9. `echo=True` 的作用



\-   将 ORM 自动生成的每一条 SQL 语句打印到控制台

\-   \*\*学习阶段强烈推荐开启\*\*，帮助理解 ORM 底层行为

\-   上线前改为 `False`



\## 三、今日遇到的 Bug 与修复



\### Bug 1：变量名拼写错误 `DATEBASE\_URL`

\-  \*\*错误\*\*：少写了一个 `A`，导致 `NameError`

\-  \*\*修复\*\*：改为 `DATABASE\_URL`



\### Bug 2：方法名拼写错误 `session.commint()`

\-  \*\*错误\*\*：`commit` 写成 `commint`，导致 `AttributeError`

\-  \*\*修复\*\*：全部替换为 `session.commit()`



\### Bug 3：`\_\_tablename\_\_` 拼写错误

\-  \*\*错误\*\*：写成了 `\_\_tabelname\_\_`，SQLAlchemy 不认识

\-  \*\*修复\*\*：改为正确的 `\_\_tablename\_\_`



\### Bug 4：`\_\_repr\_\_` 缩进错误

\-  \*\*错误\*\*：`def \_\_repr\_\_` 与类定义同级，没有缩进到类内部

\-  \*\*修复\*\*：缩进 4 格，与 `id`、`username` 等对齐



\### Bug 5：第二次运行报唯一键冲突

\-  \*\*错误\*\*：`username` 设置了 `unique=True`，重复插入相同用户名报错

\-  \*\*修复\*\*：添加“先查询再插入”的防重复检查逻辑



\### Bug 6：`print` 中误用关键字参数

\-  \*\*错误\*\*：`print("筛选：", datasets=...)`，`print` 不支持关键字参数

\-  \*\*修复\*\*：先赋值给变量，再 `print("筛选：", datasets)`



\## 四、今日收获



1\.  掌握了 ORM 的核心思想：用操作 Python 对象的方式操作数据库

2\.  理解了 Engine（连接池管理）和 Session（事务工作区）的分工

3\.  学会了 `relationship` 简化联表查询，告别手写 JOIN

4\.  养成了“每次操作新开会话，用完关闭”的工程习惯

5\.  实现了可重复运行的程序，不再因重复数据而崩溃

6\.  ORM 让数据库操作更安全、更 Pythonic，是后端开发的核心技能

