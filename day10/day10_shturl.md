\# Day10 学习日志：Pydantic 数据模型、请求校验、序列化



\## 一、今日完成



\-  理解 Pydantic 在 FastAPI 中的核心作用：数据校验 + 序列化

\-  定义三套 Pydantic 模型：UserCreate/UserOut、ProjectCreate/ProjectOut、DatasetCreate/DatasetOut

\-  掌握字段约束：min\_length、max\_length、pattern 正则、gt/ge 数值范围

\-  实现嵌套模型：ProjectOut 中包含 List\[DatasetOut]

\-  掌握 ORM 对象与 Pydantic 模型互转：from\_attributes + model\_validate

\-  演示非法参数自动拦截与 ValidationError 捕获

\-  修正多个语法错误：类型注解括号、max\_length 矛盾、打印格式错误



\## 二、核心概念



\### 1. Pydantic 的双重身份

\-  \*\*数据校验员\*\*：自动检查请求体 JSON 是否合法，非法数据直接拦截

\-  \*\*数据翻译员\*\*：将 Python 对象（ORM）自动翻译成 JSON 返回给客户端



\### 2. 字段约束速查



| 约束 | 含义 | 示例 |

|------|------|------|

| `...` (Ellipsis) | 必填 | `Field(...)` |

| `min\_length` | 字符串最小长度 | `min\_length=3` |

| `max\_length` | 字符串最大长度 | `max\_length=50` |

| `pattern` | 正则表达式校验 | `pattern=r"^\[a-z]+$"` |

| `gt` | 大于（>） | `gt=0` |

| `ge` | 大于等于（>=） | `ge=0` |

| `Optional\[str]` | 可选，可为 None | `Optional\[str] = None` |



\### 3. 输入输出模型分离

\-  \*\*Create 模型\*\*：接收客户端输入，不包含服务端生成的字段（如 id）

\-  \*\*Out 模型\*\*：返回给客户端，包含完整字段，隐藏敏感信息（如 password）

\-  \*\*企业级规范\*\*：请求体与响应体使用不同模型，职责清晰，安全



\### 4. 嵌套模型

\-  一个 Pydantic 模型中可以包含另一个模型，如 `datasets: List\[DatasetOut]`

\-  可以一次性返回项目及其下的所有数据集，减少前端请求次数



\### 5. ORM 转 Pydantic（from\_attributes）

\-  `model\_config = {'from\_attributes': True}`：允许从 ORM 对象属性直接读取值

\-  `UserOut.model\_validate(orm\_obj)`：将数据库对象转为输出模型

\-  Pydantic v2 写法，替代 v1 的 `orm\_mode = True` 和 `.from\_orm()`



\### 6. ValidationError 捕获

\-  `e.errors()` 返回所有校验错误的列表，每个错误包含字段名和错误描述

\-  `error\['loc']\[0]`：出错字段名

\-  `error\['msg']`：错误描述

\-  一次可收集多个字段的错误，提升用户体验



\### 7. 正则表达式的心态

\-  \*\*不需要背\*\*：搜索引擎 + 复制粘贴是工程师的正常工作方式

\-  \*\*需要能看懂\*\*：理解 `^`（开始）、`$`（结束）、`+`（一个以上）等基本符号

\-  \*\*工业级替代\*\*：`EmailStr` 类型更准确，但需额外安装



\## 三、今日遇到的 Bug 与修复



\### Bug 1：类型注解语法错误

\-  \*\*错误\*\*：`username:(str) = Field(...)`，冒号后加了括号

\-  \*\*修复\*\*：改为 `username: str = Field(...)`



\### Bug 2：密码字段约束矛盾

\-  \*\*错误\*\*：`min\_length=6, max\_length=0`，最小6最大0，任何密码都无法通过

\-  \*\*修复\*\*：改为 `max\_length=20`



\### Bug 3：打印长度错误

\-  \*\*错误\*\*：`print("="\*0)` 打印空字符串

\-  \*\*修复\*\*：改为 `print("="\*40)`



\### Bug 4：错误信息打印语法错误

\-  \*\*错误\*\*：`error\['masg']`（拼写错误）且缺少括号

\-  \*\*修复\*\*：改为 `error\['msg']`，补全括号



\### Bug 5：ModuleNotFoundError: No module named 'pydantic'

\-  \*\*错误\*\*：当前 Python 环境未安装 Pydantic

\-  \*\*修复\*\*：执行 `pip install pydantic`



\## 四、今日收获



1\.  Pydantic 是 FastAPI 的“数据守门员”，集校验与序列化于一体

2\.  输入输出模型分离让接口职责清晰，防止安全问题（如密码泄露）

3\.  嵌套模型可以构建复杂业务对象，适配 AI 项目的数据结构

4\.  `from\_attributes` 打通了从数据库到 API 响应的最后一步

5\.  正则表达式不需要背，理解基本语法即可，工业项目可用库替代

6\.  语法细节决定程序能否跑通，每次报错都是一次学习机会

