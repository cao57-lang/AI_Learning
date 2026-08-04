\# Day17 通用分页查询封装 - 开发日志



\## 学习目标

\- 封装通用分页工具函数，避免每个列表接口重复写分页逻辑

\- 标准化分页返回结构（total、page、page\_size、pages、items）

\- 支持动态排序和模糊条件筛选

\- 所有接口使用 Pydantic Query 参数校验，Swagger 文档自动生成



\## 项目结构

```

day17/

├── database.py          # 数据库引擎与会话工厂

├── models.py            # Dataset ORM 模型

├── schemas.py           # Pydantic 输出模型

├── utils/

│   ├── \_\_init\_\_.py

│   ├── response.py      # 统一响应 ApiResponse

│   └── pagination.py    # 通用分页工具

├── crud/

│   └── crud\_dataset.py  # 数据集 CRUD（使用分页工具）

├── api/

│   └── v1/

│       └── dataset.py   # 数据集分页列表接口

└── main.py              # 入口，注册路由

```



\## 核心知识点回顾



\### 1. SQLAlchemy 分页原理

\- `offset(n)`：跳过前 n 条记录

\- `limit(m)`：只取 m 条记录

\- 分页公式：`offset = (page - 1) \* page\_size`

\- 总条数通过 `query.count()` 高效获取（生成 SELECT COUNT(\*) 子查询）

\- 总页数使用 `math.ceil(total / page\_size)` 向上取整



\### 2. 通用分页函数设计

\- 入参：`query`（Query 对象）、`page`、`page\_size`、`sort\_by`、`sort\_order`

\- 防御性处理：限制 `page\_size` 最大 100，`page` 最小 1

\- 动态排序：通过 `getattr` 获取模型列对象，安全添加 order\_by

\- 返回统一字典，不耦合具体 Pydantic 模型，上层负责序列化



\### 3. 分层架构优势

\- `api/`：处理 HTTP 请求解析、参数校验、响应格式化

\- `crud/`：封装具体数据库操作，不依赖 HTTP 上下文

\- `utils/`：纯工具函数，可跨业务复用

\- 任何层修改不影响其他层，易于测试和维护



\### 4. FastAPI 依赖注入

\- 使用 `Depends(get\_db)` 自动获取数据库会话

\- 生成器函数 `yield db` 确保请求结束后自动关闭会话

\- 全局异常处理器可自动捕获未处理异常



\## 踩坑记录



\### 坑1：Pydantic 模型类名拼写错误

\- \*\*现象\*\*：`schemas.py` 中类名写成 `DateseiOut`（应为 `DatasetOut`）

\- \*\*后果\*\*：接口层导入失败，服务无法启动

\- \*\*修复\*\*：统一改为 `DatasetOut`



\### 坑2：API 参数名与 CRUD 函数参数名不一致

\- \*\*现象\*\*：`dataset.py` 中定义参数 `sor\_by`，调用 CRUD 时传入 `sort\_by=sor\_by` 导致关键字错误

\- \*\*后果\*\*：`TypeError: get\_dataset\_list() got an unexpected keyword argument 'sor\_by'`

\- \*\*修复\*\*：将 API 参数名改为 `sort\_by`，保持一致



\### 坑3：Pydantic v2 中使用了已弃用的 `from\_orm()`

\- \*\*现象\*\*：`DatasetOut.from\_orm(item)` 报 AttributeError

\- \*\*原因\*\*：在 Pydantic v2 中，ORM 转换方法已从 `from\_orm()` 改为 `model\_validate()`

\- \*\*修复\*\*：使用 `DatasetOut.model\_validate(item)` 进行 ORM 到 Pydantic 的转换

\- \*\*注意\*\*：配置中需使用 `model\_config = {'from\_attributes': True}` 才能正确读取 ORM 属性



\### 坑4：数据库与表的准备工作

\- 确保 MySQL 中存在 `ai\_dataset\_db` 数据库

\- 首次运行前需执行 `Base.metadata.create\_all(bind=engine)` 创建表结构

\- 需插入测试数据验证分页功能



\## 测试验证

\- 启动服务后访问 Swagger：`http://127.0.0.1:8000/docs`

\- 测试场景：

&#x20; - 默认分页：`GET /api/v1/dataset/list` 返回首页 10 条

&#x20; - 翻页：`page=2\&page\_size=5` 正常切换

&#x20; - 模糊搜索：`label\_type=图像` 返回匹配数据

&#x20; - 边界校验：`page=0` 返回 422，`page\_size=200` 返回 422

\- 日志（若集成）中正常记录请求与查询信息



\## 收获与总结

\- 通用分页工具的核心是\*\*接收查询对象、返回标准字典\*\*，让所有列表接口都有统一的输出格式

\- 防御性编程很重要：限制 page\_size 最大值、修正非法页码，保护数据库

\- 动态排序通过 `getattr` 安全获取列对象，避免字符串拼接 SQL 风险

\- FastAPI 的 `Query` 校验让 Swagger 自动生成带约束的文档，前端可直接参考

\- 分层设计让代码清晰，扩展新业务时只需新增模型、CRUD 和接口文件，不影响已有功能

