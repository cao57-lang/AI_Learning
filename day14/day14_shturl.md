\# Day14 学习日志：用户登录接口实战



\## 一、今日完成



\-  使用 OAuth2PasswordRequestForm 接收登录表单

\-  实现 POST /auth/login 登录接口

\-  根据用户名查询数据库，区分“账号不存在”和“密码错误”

\-  密码 bcrypt 校验，JWT Token 签发完整串联

\-  复用 Day9 数据库会话、Day11 密码工具与 JWT 工具、Day12 统一响应与异常处理

\-  完成注册 → 登录 → 携带 Token 访问受保护接口的全流程闭环

\-  排查并修正数据库驱动拼写、变量命名不一致等问题



\## 二、核心概念



\### 1. OAuth2PasswordRequestForm

\-  FastAPI 官方推荐的登录表单接收方式

\-  自动从请求体中解析 `username` 和 `password`

\-  符合 OAuth2 规范，Swagger 自动生成标准登录表单

\-  可与 OAuth2PasswordBearer 完美集成，实现 /docs 中的 Authorize 功能



\### 2. 登录流程

\-  ① 接收前端提交的 username、password

\-  ② 查询数据库，用户名不存在 → raise BizException("账号不存在")

\-  ③ 用户存在，bcrypt 校验密码哈希

\-  ④ 密码不匹配 → raise BizException("密码错误")

\-  ⑤ 校验通过，签发 JWT（载荷包含 sub、role、exp）

\-  ⑥ 返回标准格式：`{"access\_token": "...", "token\_type": "bearer"}`



\### 3. JWTError 作用

\-  `python-jose` 库中 JWT 相关异常的基类

\-  统一捕获签名不匹配、Token 过期、格式错误等所有解码异常

\-  在 get\_current\_user 依赖中使用 `except JWTError` 统一处理



\### 4. super().\_\_init\_\_(msg) 的作用

\-  在自定义异常类 `BizException` 中调用父类 `Exception` 的构造函数

\-  目的是让自定义异常也拥有标准异常的所有行为（打印、traceback、日志记录）

\-  是定义异常子类的最佳实践



\### 5. RequestValidationError 触发条件

\-  请求数据不符合 Pydantic 模型校验规则时，FastAPI 自动抛出

\-  包括：缺少必填字段、类型错误、字符串长度不够、格式校验失败、数值超出范围等

\-  由全局异常处理器捕获并转换为统一错误格式



\### 6. 函数传参的三种写法

\-  `fail\_resp(500, "服务器内部错误")`：全位置参数

\-  `fail\_resp(500, msg="服务器内部错误")`：混合（位置 + 关键字）

\-  `fail\_resp(code=500, msg="服务器内部错误")`：全关键字参数

\-  三种写法功能完全等价，推荐使用全关键字参数，可读性最高

\-  唯一规则：位置参数必须在关键字参数之前



\### 7. 字典 update 方法的行为

\-  传入的键不存在 → 新增键值对

\-  传入的键已存在 → 更新该键的值

\-  `to\_encode.update({"exp": expire})` 是新增 `exp` 字段（之前字典中没有 exp）



\### 8. 安全考虑

\-  学习阶段区分“账号不存在”和“密码错误”，便于调试

\-  生产环境通常模糊提示“账号或密码错误”，防止恶意枚举用户名



\## 三、踩坑记录



\### Bug 1：数据库驱动拼写错误

\-  \*\*错误\*\*：`mysql+pymsql://` 少了一个 `y`

\-  \*\*修复\*\*：改为 `mysql+pymysql://`



\### Bug 2：Session 变量名不一致

\-  \*\*错误\*\*：`Sessionlal` 和 `SessionLocal` 混用（字母 l 和 L 容易混淆）

\-  \*\*修复\*\*：统一为 `SessionLocal`



\### Bug 3：异常处理器拼写错误

\-  \*\*错误\*\*：`unkown\_exception\_handler` 少了一个 `n`

\-  \*\*修复\*\*：改为 `unknown\_exception\_handler`



\### Bug 4：数据库列名映射理解

\-  ORM 属性名是 Python 层面的变量名，实际数据库列名由 Column 的第一个参数决定

\-  当 Column 指定了列名（如 `"password"`）时，数据库列名与 ORM 属性名不同

\-  访问时使用 ORM 属性名，但 SQL 生成时会自动映射到数据库列名



\## 四、今日收获



1\.  完成了账号体系闭环：注册 → 登录 → 签发 Token → 鉴权访问

2\.  掌握了 FastAPI 标准登录表单 OAuth2PasswordRequestForm 的使用

3\.  串联了数据库查询、密码校验、JWT 签发、统一异常处理四大模块

4\.  理解了登录失败时错误信息的设计策略与安全考量

5\.  通过排查多个拼写错误，加深了对系统各层细节的敏感度

```

