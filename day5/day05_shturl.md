```markdown

\# Day5 学习日志：Requests 网络请求实战



\## 一、今日完成



\-  使用 requests 库调用 Open-Meteo 免费天气 API

\-  封装通用 API 请求工具类 `APIRequest`，统一处理超时、连接异常、HTTP 错误、JSON 解析异常

\-  实现城市搜索函数 `search\_city`，通过 Geocoding API 获取经纬度

\-  实现天气查询函数 `get\_current\_weather`，通过 Forecast API 获取当前天气

\-  将 WMO 天气代码映射为中文描述

\-  编写交互式菜单，支持循环查询多个城市

\-  成功运行并验证：正常查询、城市不存在、网络错误等场景



\## 二、核心概念理解



\### 1. HTTP 请求的本质



程序向服务器发送 HTTP GET 请求，携带 URL 和参数（params），服务器返回 JSON 格式的响应数据。



\-  \*\*URL\*\*：告诉服务器“去哪里拿数据”

\-  \*\*params\*\*：告诉服务器“我要什么条件的数据”

\-  \*\*响应状态码\*\*：200 成功，404 未找到，500 服务器错误



\### 2. requests 库核心用法



```python

response = requests.get(url, params=params, headers=headers, timeout=10)

response.raise\_for\_status()  # 状态码非 2xx 抛异常

data = response.json()       # 解析 JSON

```



\-  `params` 自动拼接 URL 参数，比手动拼字符串更清晰

\-  `timeout` 防止请求卡死

\-  `raise\_for\_status()` 统一处理 4xx/5xx 错误



\### 3. @staticmethod 静态方法



`@staticmethod` 让方法不需要 `self`，可以直接通过类名调用。



\-  \*\*本质\*\*：就是一个普通函数，只是逻辑上属于这个类

\-  \*\*何时用\*\*：方法不需要访问实例属性，只是一个通用工具

\-  \*\*好处\*\*：不需要先创建对象，代码更简洁



\### 4. 分层防御的异常处理



| 层级 | 保护范围 | 异常类型 |

|------|----------|----------|

| 外层 try | 网络连接、HTTP 状态码 | Timeout, ConnectionError, HTTPError |

| 内层 try | JSON 数据解析 | ValueError |



\-  外层确保“能拿到响应”

\-  内层确保“响应内容格式正确”

\-  分层处理的目的是给用户精确的错误提示



\### 5. .get() 方法的安全取值



```python

results = data.get("results")  # 键不存在返回 None，不报错

```



\-  `data\["results"]` 键不存在会崩溃

\-  `data.get("results")` 键不存在返回 None，程序继续运行

\-  配合 `if not results:` 做安全检查，实现防御性编程



\### 6. 数据与表示的分离



API 返回天气代码（数字）而非中文描述，是为了：



\-  \*\*全球通用\*\*：数字是国际标准，与语言无关

\-  \*\*程序友好\*\*：程序逻辑判断数字比判断字符串更可靠

\-  \*\*职责分离\*\*：API 提供者负责气象数据，开发者负责本地化翻译



我们写的 `weather\_map` 字典，就是这个全球系统中为中文用户定制的最后一环。



\## 三、今日遇到的Bug与修复



\### Bug 1：函数调用参数错误

\-  \*\*错误\*\*：`weather = get\_weather\_description(lat, lon)` 传入了两个参数

\-  \*\*原因\*\*：混淆了 `get\_current\_weather` 和 `get\_weather\_description` 的职责

\-  \*\*修复\*\*：先调用 `get\_current\_weather(lat, lon)` 获取天气字典，再从中取出 `weathercode`，传给 `get\_weather\_description`



\### Bug 2：参数拼写错误

\-  \*\*错误\*\*：`"fomat": "json"` 拼错了 `format`

\-  \*\*影响\*\*：Open-Meteo 默认返回 JSON，所以未暴露问题，但严格 API 会报错

\-  \*\*修复\*\*：改为 `"format": "json"`



\### Bug 3：异常类型选择

\-  \*\*原写法\*\*：`except requests.exceptions.ChunkedEncodingError`

\-  \*\*问题\*\*：这个异常是接收数据中断时抛出，不是真正的“断网”

\-  \*\*建议\*\*：增加 `ConnectionError` 覆盖更多网络层错误



\## 四、今日收获



1\.  网络请求的核心流程：构造请求 → 发送 → 检查状态 → 解析响应

2\.  封装工具类能大幅减少重复代码，提高可维护性

3\.  防御性编程：对每一个可能失败的环节都做好兜底处理

4\.  数字编码 + 本地映射表，是构建国际化系统的标准模式

5\.  函数职责要单一清晰，调用链不能混淆

```

