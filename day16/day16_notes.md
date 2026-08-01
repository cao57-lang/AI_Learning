\# Day16 请求上下文追踪 TraceId - 学习笔记



\## 学习目标

\- 为每个 HTTP 请求自动生成全局唯一 TraceId

\- 将 TraceId 自动注入日志，实现请求链路追踪

\- 统一在 JSON 响应体中返回 TraceId，方便前后端联调

\- 理解 `contextvars` 在异步环境中的上下文隔离原理



\## 核心知识点



\### 1. contextvars — 异步安全的“便签纸”

\- `ContextVar` 是 Python 3.7+ 标准库提供的上下文变量，每个异步任务（如一个 HTTP 请求）拥有独立的副本。

\- 通过 `trace\_id\_var.set(value)` 写入，`trace\_id\_var.get()` 读取，不会在多请求间串数据。

\- `default="-"` 保证非请求上下文（如 uvicorn 启动日志）不报错。



\### 2. logging.Filter — 日志记录的动态增强器

\- 自定义 `TraceIdFilter` 重写 `filter(record)` 方法。

\- 从当前上下文中取出 TraceId，通过 `record.trace\_id = ...` 动态注入到日志记录对象。

\- 必须返回 `True`，否则日志会被丢弃。

\- 通过 `handler.addFilter()` 注册，所有经过该 Handler 的日志都会自动带上 `trace\_id`。



\### 3. FastAPI 全局依赖注入

\- `FastAPI(dependencies=\[Depends(set\_trace\_id)])` 让所有路由自动执行依赖函数。

\- 依赖函数接收 `Request` 参数，生成 UUID 并写入 `contextvars` 和 `request.state`。

\- `request.state` 是每个请求的临时存储空间，用于在中间件中获取 TraceId。



\### 4. 中间件 — 拦截响应统一注入 trace\_id

\- 继承 `BaseHTTPMiddleware`，重写 `dispatch` 方法。

\- `await call\_next(request)` 触发后续所有中间件、路由匹配、视图函数，最终返回响应。

\- 对成功的 JSON 响应，读取原始 body，解析为 dict，添加 `trace\_id` 字段，再重构 `JSONResponse`。

\- 必须移除旧响应头中的 `content-length`、`transfer-encoding`、`content-encoding`，让新响应自动计算。



\## 实现步骤

1\. \*\*升级日志模块\*\*：定义 `TraceIdFilter`，将其添加到文件和控制台 Handler，日志格式增加 `%(trace\_id)s`。

2\. \*\*编写全局依赖\*\*：生成 TraceId 并设置 `contextvars` 和 `request.state`。

3\. \*\*编写中间件\*\*：拦截 2xx JSON 响应，注入 `trace\_id`，处理响应头冲突。

4\. \*\*创建 FastAPI 应用\*\*：挂载全局依赖和中间件，添加测试接口。

5\. \*\*异常处理\*\*：在手动返回 500 等错误时，通过 `trace\_id\_var.get()` 显式添加 TraceId。



\## 踩坑记录



\### 坑1：`setFormatter(logging.DEBUG)` 误写

\- \*\*现象\*\*：误将 `setLevel` 写成 `setFormatter`，导致传入整数而非 Formatter 对象。

\- \*\*修复\*\*：正确使用 `console\_handler.setLevel(logging.DEBUG)`。



\### 坑2：`trace\_id\_var()` 调用错误

\- \*\*现象\*\*：直接 `trace\_id\_var()` 调用，缺少 `.get()` 方法。

\- \*\*修复\*\*：改为 `trace\_id\_var.get()`。



\### 坑3：`Content-Length` 不匹配导致 `LocalProtocolError`

\- \*\*现象\*\*：中间件注入 trace\_id 后，响应体变长，但旧 `Content-Length` 头未更新，触发 `h11.\_util.LocalProtocolError: Too much data for declared Content-Length`。

\- \*\*原因\*\*：新 `JSONResponse` 使用了旧的 `Content-Length`，实际发送数据大于声明长度。

\- \*\*修复\*\*：在构造新响应前，用 `headers.pop("content-length", None)` 移除长度头，同时移除 `transfer-encoding` 和 `content-encoding`，让框架自动计算正确的 `Content-Length`。



\## 测试验证

\- 访问 `/`、`/login?username=test`，返回 JSON 均包含 `trace\_id` 字段。

\- 日志文件与控制台输出均正确显示 `trace\_id` 列，值随请求变化。

\- 访问 `/error`，返回 500 JSON 包含 `trace\_id`，日志记录完整异常堆栈。

\- 并发刷新多个页面，日志中 TraceId 各不相同，无串数据。



\## 收获与总结

\- 工程化日志不仅是格式化输出，更要支持链路追踪，便于线上问题排查。

\- `contextvars` 是异步框架中传递请求上下文的关键技术。

\- 自定义 `logging.Filter` 可以无侵入地为所有日志注入动态信息。

\- 中间件修改响应体时，务必处理与内容描述相关的 HTTP 头，避免协议错误。

\- 全局依赖 + 中间件的组合实现了对业务代码零侵入的 TraceId 注入。

