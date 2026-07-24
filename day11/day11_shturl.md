\# Day11 学习日志：JWT 身份认证与权限控制



\## 一、今日完成



\- 使用 bcrypt 对密码进行哈希存储与验证，替代 passlib 解决版本兼容性问题

\- 掌握 JWT 的签发、校验、过期时间控制

\- 使用 FastAPI Depends 实现 Token 自动提取与当前用户解析

\- 实现登录接口 /login，返回 JWT access\_token

\- 实现受保护接口 /users/me，返回当前用户信息

\- 实现管理员专属接口 /admin/data，普通用户返回 403

\- 统一 401/403 异常拦截，处理 token 不存在、无效、过期等情况

\- 排查并解决 Token 中 sub 类型不一致导致的 401 问题

\- 完成测试验证：无 token 访问、过期/伪造 token、角色权限控制



\## 二、核心概念



\### 1. bcrypt 密码哈希

\- 单向不可逆，每次生成不同哈希（随机盐）

\- 验证时自动提取盐值并比较

\- 直接使用 bcrypt 库：`hashpw()`、`checkpw()`、`gensalt()`

\- 安全存储：数据库中只存哈希值，绝不明文存储



\### 2. JWT 认证流程

\- 用户登录 → 服务器验证密码 → 签发 Token（含 sub、role、exp）

\- 客户端将 Token 放在 Authorization: Bearer <token> 头中携带

\- 服务器解码 Token，验证签名和有效期，获取用户身份

\- Token 自包含，减少数据库查询



\### 3. Depends 依赖注入

\- 将公共逻辑（如解析 Token、获取当前用户）抽成函数

\- 通过 Depends 注入到路径操作，减少重复代码

\- 可嵌套：require\_admin 内调用 get\_current\_user，实现权限组合



\### 4. 权限分级

\- 普通标注员（annotator）仅能访问 /users/me

\- 管理员（admin）可访问 /admin/data

\- 401 表示未认证（token 无效/过期/缺失）

\- 403 表示已认证但权限不足



\### 5. 密码哈希工具函数

```python

def get\_password\_hash(password: str) -> str:

&#x20;   salt = bcrypt.gensalt()

&#x20;   hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

&#x20;   return hashed.decode('utf-8')



def verify\_password(plain: str, hashed: str) -> bool:

&#x20;   return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

```



\## 三、踩坑记录



\### Bug 1：passlib 与 bcrypt 版本冲突导致 ValueError

\- \*\*错误\*\*：`ValueError: password cannot be longer than 72 bytes`

\- \*\*原因\*\*：passlib 1.7.4 与 bcrypt 5.0.0 不兼容，误判密码超长

\- \*\*解决\*\*：弃用 passlib，改用 bcrypt 库直接处理，代码更简洁



\### Bug 2：Token 验证返回 401 但用户存在且密码正确

\- \*\*原因\*\*：JWT 中 `sub` 字段被解码为字符串，而数据库查询时代码期望整数，类型不匹配导致查询失败

\- \*\*解决\*\*：签发 Token 时将 `user.id` 转为字符串 `str(user.id)`，验证时用 `int(user\_id\_str)` 转回整数再查询



\### Bug 3：login 依赖错误地使用了 get\_current\_user

\- \*\*错误\*\*：`db: Session = Depends(get\_current\_user)` 导致登录接口需要认证

\- \*\*修复\*\*：改为 `Depends(get\_db)`，登录接口不需要 token



\### Bug 4：HTTPException 中 status\_code 误用 ==

\- \*\*错误\*\*：`status\_code==status.HTTP\_401\_UNAUTHORIZED` 是比较运算

\- \*\*修复\*\*：改为赋值 `status\_code=status.HTTP\_401\_UNAUTHORIZED`



\### Bug 5：WWW-Authenticate 头大小写不规范

\- \*\*修复\*\*：统一为 `"WWW-Authenticate": "Bearer"`



\## 四、今日收获



1\. 掌握了从密码哈希 → 用户登录 → Token 签发 → 请求鉴权 → 角色授权的完整认证链条

2\. 理解了 JWT 无状态认证的优势，适用于分布式系统

3\. 学会了用依赖注入组织认证逻辑，代码更模块化、可复用

4\. 实现了基于角色的访问控制（RBAC），为后续项目打下安全基础

5\. 通过排查多个 Bug，加深了对类型一致性、库兼容性的理解

6\. 认证机制是后端安全的核心，任何用户系统都离不开

```

