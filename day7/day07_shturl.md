```markdown

\# Day7 学习日志：FastAPI 完整 CRUD Todo 接口



\## 一、今日完成



\-  使用 Pydantic 定义请求体模型 `TodoCreate` 和响应模型 `Todo`

\-  基于内存列表实现待办事项的增删改查（CRUD）

\-  实现五个 RESTful 接口：POST / GET（全部+单个）/ PUT / DELETE

\-  使用 `HTTPException` 处理 404 资源不存在

\-  通过 Swagger UI 完整测试所有接口

\-  修正三个关键 Bug：字符串字段误用数字约束、循环变量写错、路由装饰器参数位置错误



\## 二、核心概念



\### 1. Pydantic 库



\-  \*\*本质\*\*：Python 中用于定义数据“应该长什么样”的库，自动完成检查与转换

\-  \*\*核心作用\*\*：数据校验（检查请求体是否合法）+ 序列化（将 Python 对象转为 JSON）

\-  \*\*使用方式\*\*：继承 `BaseModel`，通过类型注解和 `Field` 定义字段规则



\### 2. 数据校验与序列化



| 概念 | 通俗解释 | 触发时机 |

|------|----------|----------|

| 校验 | 检查进来的数据合不合规矩 | 收到请求时，Pydantic 自动验证请求体 |

| 序列化 | 把出去的数据包装成标准 JSON | 返回响应时，FastAPI 自动转换 |



\-  校验失败自动返回 \*\*422\*\* 状态码，无需手动编写 `if` 判断

\-  `response\_model` 控制返回数据的结构



\### 3. HTTPException 抛出异常



\-  \*\*为什么用 `raise` 而不是 `return`？\*\* 为了正确设置 HTTP 状态码

\-  `return {"error": "..."}` 状态码仍是 200，客户端无法判断操作成败

\-  `raise HTTPException(status\_code=404)` 让 FastAPI 返回标准的 404 错误响应

\-  \*\*`raise` 是程序的紧急刹车，告诉调用者“我遇到了无法继续的意外情况”\*\*



\### 4. JSON 数据类型选择



| 类型 | 语法 | 适用场景 |

|------|------|----------|

| 字典 `{}` | `{"key": "value"}` | 单个对象 |

| 列表 `\[]` | `\[{...}, {...}]` | 多个对象，每个元素是字典 |



\-  `isinstance(data, list)` 用于确保文件顶层是列表而非字典



\### 5. Swagger 文档与 `description`



\-  Swagger 是 FastAPI 自动生成的交互式 API 文档网页（访问 `/docs`）

\-  可在网页上直接点击 "Try it out" 测试接口，无需额外工具

\-  `Field(description="...")` 的内容\*\*不会出现在响应 JSON 里\*\*

\-  它会作为字段说明显示在 Swagger 文档界面的 Schema 标签页中



\### 6. `\*\*todo.model\_dump()` 作用



\-  `model\_dump()` 将 Pydantic 模型对象转换为普通字典

\-  `\*\*` 将字典解包为独立的命名参数

\-  \*\*目的\*\*：将 `TodoCreate`（无 id）的字段展开，加上新生成的 `id`，一起传给 `Todo` 构造函数



\### 7. `enumerate` 与普通 `for` 的区别



| 写法 | 获取什么 | 能否修改列表元素 |

|------|----------|-----------------|

| `for todo in todos\_db:` | 只有元素本身 | ❌ 不能，`todo = new` 只改变局部变量 |

| `for i, todo in enumerate(todos\_db):` | 索引 + 元素 | ✅ 能，`todos\_db\[i] = new` 真正修改列表 |



\-  需要原地替换或删除列表元素时，必须使用 `enumerate` 获取索引



\### 8. HTTP 状态码速查



| 状态码 | 含义 | 我们的场景 |

|--------|------|-----------|

| 200 | 成功 | GET 查询成功 |

| 201 | 创建成功 | POST 新增待办成功 |

| 204 | 无内容 | DELETE 删除成功，无响应体 |

| 404 | 资源不存在 | 查询/修改/删除不存在的 ID |

| 422 | 请求格式错误 | 请求体不符合 Pydantic 模型（自动返回） |



\## 三、今日遇到的 Bug 与修复



\### Bug 1：字符串字段误用 `max\_digits`

\-  \*\*错误\*\*：`title: str = Field(..., max\_digits=1)`

\-  \*\*原因\*\*：`max\_digits` 是数字类型专用约束，字符串字段不能使用

\-  \*\*修复\*\*：改为 `min\_length=1`



\### Bug 2：PUT 接口循环变量写错

\-  \*\*错误\*\*：`for i, todo in enumerate(todo\_id):`

\-  \*\*原因\*\*：误将路径参数 `todo\_id`（字符串）当作列表遍历

\-  \*\*修复\*\*：改为 `for i, todo in enumerate(todos\_db):`



\### Bug 3：DELETE 路由装饰器参数位置错误

\-  \*\*错误\*\*：`@app.delete("/todo/{todo\_id},status\_code=204")`

\-  \*\*原因\*\*：将 `status\_code` 写入了路径字符串内部

\-  \*\*修复\*\*：改为 `@app.delete("/todo/{todo\_id}", status\_code=204)`



\### Bug 4：尝试通过 `todo = new\_todo` 修改列表

\-  \*\*错误认知\*\*：以为在 for 循环中给循环变量赋值就能修改列表

\-  \*\*正确理解\*\*：循环变量只是临时指向，修改它不影响原列表；必须通过索引 `todos\_db\[i] = new\_todo` 才能生效



\### Bug 5：Swagger 测试时 JSON 格式错误

\-  \*\*错误\*\*：手动输入 JSON 时缺少逗号或使用了中文标点

\-  \*\*修复\*\*：使用 Swagger 自动生成的 JSON 模板，只填入值，不修改结构



\## 四、今日收获



1\.  掌握了 RESTful API 的标准设计与完整实现

2\.  理解了 Pydantic 在请求校验和响应序列化中的双重作用

3\.  学会了用 `HTTPException` 正确设置错误状态码

4\.  明确了普通 for 循环与 enumerate 的本质区别

5\.  CRUD 是后端开发的基石，任何复杂业务都是它的变体

6\.  错误是学习最好的老师——今天修了 5 个 Bug，每个都加深了对系统的理解

```

