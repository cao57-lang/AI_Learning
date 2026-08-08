# Day18 RBAC 简易权限中间件 - 开发日志

## 一、学习目标
- 基于 JWT 构建双角色（user / admin）轻量级 RBAC
- 封装通用权限校验依赖：`RequireLogin`、`RequireAdmin`
- 实现接口级权限隔离（公开接口、仅登录接口、管理员专属接口）
- 掌握 FastAPI 依赖注入在企业级权限系统中的标准用法

## 二、项目结构
```
day18/
├── api/v1/
│   ├── auth.py          # 登录签发含 role 的 JWT
│   ├── dataset.py       # 数据集接口，绑定权限
│   └── user.py          # 用户管理（管理员专属）
├── crud/
│   ├── dataset_crud.py
│   └── user_crud.py
├── utils/
│   ├── jwt_util.py      # JWT 签发/解析（携带 role）
│   ├── page_util.py     # 分页工具
│   ├── response.py      # 统一响应
│   └── permission.py    # 权限核心：RequireLogin/RequireAdmin
├── models.py            # User 新增 role 字段
├── schemas.py           # TokenResponse、UserOut
├── database.py
├── main.py
└── day18_notes.md
```

## 三、核心改造点

### 1. 用户模型改造（models.py）
```python
class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "user"
    # ... 原有字段
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
```
- 使用 Python 枚举限制角色值，防止脏数据。
- 数据库层面为 ENUM 类型，只能插入 `'user'` 或 `'admin'`。

### 2. JWT 载荷改造（jwt_util.py）
**签发**：
```python
create_access_token(data={"user_id": user.id, "role": user.role})
```
**解析**：
```python
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# payload 中直接包含 user_id 和 role
```
- 登录成功后，将角色打入 token，后续权限校验无需再查库获取角色。
- 尽管权限依赖中仍会查库获取完整 User 对象，但 token 内角色可用于快速校验或审计。

### 3. 权限校验依赖（permission.py）
```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_current_user(token = Depends(oauth2_scheme), db = Depends(get_db)):
    # 1. 提取 token（缺失→401）
    # 2. 解析 payload（无效→401）
    # 3. 查询用户（不存在→401）
    return user

async def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(403, "权限不足，仅管理员可执行此操作")
    return current_user

RequireLogin = Depends(get_current_user)
RequireAdmin = Depends(require_admin)
```
- `RequireLogin` 所有登录用户均可访问。
- `RequireAdmin` 在 `RequireLogin` 基础上追加角色检查，普通用户触发 403。

### 4. 接口权限绑定
| 接口 | 权限依赖 | 说明 |
|------|---------|------|
| `POST /api/v1/auth/login` | 无 | 公开 |
| `GET /api/v1/dataset/list` | `RequireLogin` | 普通员工只读 |
| `DELETE /api/v1/dataset/{id}` | `RequireAdmin` | 管理员删除 |
| `GET /api/v1/users/list` | `RequireAdmin` | 用户管理 |

## 四、踩坑记录

### 坑1：数据库存储明文或格式错误的哈希 → bcrypt.checkpw 报 Invalid salt
- **现象**：登录时报 500，堆栈显示 `ValueError: Invalid salt`
- **原因**：数据库中 `password` 字段存储的不是有效的 bcrypt 哈希（可能是明文、旧算法或截断）。
- **解决**：用 Python 生成新的 bcrypt 哈希并更新数据库
  ```python
  import bcrypt
  hashed = bcrypt.hashpw("123456".encode(), bcrypt.gensalt()).decode()
  ```
  然后 SQL 更新 `user SET password = '...' WHERE username='lisi'`

### 坑2：Swagger Authorize 表单与手动登录混淆
- **现象**：误认为 Authorize 弹窗是登录接口，或需要手动复制 token。
- **澄清**：Swagger 的 OAuth2 表单会自动调用 `/api/v1/auth/login` 完成认证并存储 token，直接填写用户名密码即可。

### 坑3：访问 GET 接口时 SQLAlchemy 打印 ROLLBACK
- **现象**：只读请求结束后日志出现 `ROLLBACK`，以为异常。
- **原因**：未显式调用 `commit()` 的事务在会话关闭时自动回滚，对只读查询完全正常。

### 坑4：响应中仍查询 password 列
- **现象**：SQL 日志中 `SELECT user.password`，虽然 Pydantic 不会序列化，但仍有安全隐患。
- **优化**：在 CRUD 查询中可加入 `db.query(User).options(defer(User.password))` 避免读取密码哈希到内存。

## 五、权限拦截流程图
```
请求到达
   ↓
路由匹配
   ↓
解析依赖项
   ├── get_db
   └── 权限依赖
         ├─ oauth2_scheme 提取 token（无→401）
         ├─ decode_access_token（无效→401）
         ├─ db.query(User)（不存在→401）
         └─ [仅 RequireAdmin] role == "admin"？（否→403）
   ↓
进入视图函数（正常处理）
   ↓
返回响应
```

## 六、自测验证
- ✅ 无 token 访问数据集列表 → 401
- ✅ 普通用户 (role=user) 删除数据集 → 403
- ✅ 普通用户访问用户管理 → 403
- ✅ 管理员访问所有接口 → 200
- ✅ 登录接口无需认证 → 200

## 七、收获总结
- FastAPI 的依赖注入是权限系统的天然载体，`Depends` 可任意组合。
- 权限依赖短路机制保证了安全：校验失败时视图函数体完全不会执行。
- 统一异常 + 统一响应 + 统一权限，三大“统一”奠定了后续业务扩展的基础。
- 密码安全必须从源头保证：注册时 bcrypt 哈希，修改时重新哈希，绝不用明文。
```