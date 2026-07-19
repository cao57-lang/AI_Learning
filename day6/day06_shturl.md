```markdown

\# Day6 学习日志：FastAPI 基础入门



\## 一、今日完成



\-  安装 FastAPI 和 uvicorn

\-  实现 Hello World 根路径接口 `GET /`

\-  实现路径参数接口 `GET /student/{stu\_id}`

\-  实现查询参数接口 `GET /query`

\-  从 JSON 文件加载数据，替代硬编码模拟数据

\-  使用 uvicorn 热重载启动服务

\-  体验 Swagger 自动文档 `/docs`

\-  理解 `\_\_pycache\_\_` 文件夹的作用



\## 二、核心概念



\### 1. FastAPI 应用结构



```python

from fastapi import FastAPI

app = FastAPI()



@app.get("/path")

def handler():

&#x20;   return {"key": "value"}

```



\-  `app = FastAPI()` 创建应用实例

\-  `@app.get()` 声明 GET 路由

\-  函数返回的字典自动转为 JSON 响应



\### 2. 路径参数 vs 查询参数



| 类型 | 写法 | URL 示例 | 用途 |

|------|------|----------|------|

| 路径参数 | `/student/{stu\_id}` | `/student/s001` | 唯一标识资源 |

| 查询参数 | 函数参数（不在路径中） | `/query?name=张三\&class=1班` | 过滤、搜索、附加条件 |



\-  路径参数是路由的一部分，必须传递

\-  查询参数在 `?` 后面，可以带默认值变成可选



\### 3. 热重载



```bash

uvicorn main:app --reload

```



\-  `main`：文件名（不含 .py）

\-  `app`：FastAPI 实例变量名

\-  `--reload`：代码修改后自动重启，开发必备



\### 4. Swagger 自动文档



\-  访问 `http://127.0.0.1:8000/docs` 即可获得交互式 API 文档

\-  基于 OpenAPI 规范自动生成

\-  可直接在网页上测试所有接口，无需 Postman



\### 5. 从 JSON 文件加载数据



```python

import json

import os



def load\_students(file\_path):

&#x20;   with open(file\_path, "r", encoding="utf-8") as f:

&#x20;       data = json.load(f)

&#x20;   return data

```



\-  `json.load(f)` 将文件内容解析为 Python 对象

\-  需要配合异常处理，防止文件不存在或格式错误导致崩溃



\### 6. `isinstance(data, list)` 类型检查



\-  检查变量是否属于指定类型

\-  防止 JSON 文件格式错误（如顶层是字典而非列表）导致后续代码崩溃

\-  比 `type(data) == list` 更推荐，因为兼容继承关系



\### 7. 多异常捕获 `except (A, B) as e`



```python

except (json.JSONDecodeError, IOError) as e:

&#x20;   print(f"错误：{e}")

```



\-  同时捕获多种异常类型

\-  `as e` 获取异常详情，方便排查

\-  `JSONDecodeError`：JSON 格式不合法

\-  `IOError`：文件读写失败



\### 8. 文件路径最佳实践



```python

BASE\_DIR = os.path.dirname(\_\_file\_\_)

DATA\_FILE = os.path.join(BASE\_DIR, "students.json")

```



\-  `\_\_file\_\_` 是当前脚本的绝对路径

\-  `os.path.dirname()` 取出所在目录

\-  `os.path.join()` 安全拼接路径

\-  好处：无论从哪个目录运行脚本，都能正确找到文件



\### 9. `\_\_pycache\_\_` 文件夹



\-  Python 自动生成的字节码缓存，加速后续启动

\-  可以删除，不影响运行，下次会自动重新生成

\-  应在 `.gitignore` 中添加 `\_\_pycache\_\_/` 和 `\*.pyc`，不提交到 Git



\## 三、踩坑记录



1\.  \*\*端口占用\*\*：8000 端口被占用时，使用 `--port 8001` 换端口

2\.  \*\*热重载失效\*\*：确认命令中有 `--reload`，且代码无语法错误

3\.  \*\*路径参数与查询参数混淆\*\*：路径参数在路由中用 `{}` 包裹，查询参数直接写在函数签名里

4\.  \*\*JSON 文件路径问题\*\*：使用 `os.path.join(os.path.dirname(\_\_file\_\_), "students.json")` 解决跨目录运行找不到文件的问题



\## 四、今日收获



1\.  FastAPI 让 Python Web 开发变得极其简洁优雅

2\.  自动文档生成是提升开发效率的神器

3\.  路径参数用于资源定位，查询参数用于条件筛选

4\.  文件路径处理要基于 `\_\_file\_\_`，而非依赖当前工作目录

5\.  防御性编程习惯（类型检查、异常捕获）在 Web 开发中同样重要

6\.  从今天起，我们写的功能可以真正被浏览器访问了

```

