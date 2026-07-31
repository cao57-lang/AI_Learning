\# Day15 工程化日志封装 - 开发日志



\## 学习目标

封装独立日志工具模块，实现：

\- 控制台彩色输出 + 文件滚动切割（单文件 5MB，保留 10 个备份）

\- 统一日志格式：时间 | 级别 | 文件名:行号 | 内容

\- 全局 logger 对象，项目各处导入即用，避免重复初始化

\- 接入 FastAPI 演示正常请求与异常捕获埋点



\## 核心知识点回顾



\### 1. logging 四大组件

| 组件 | 作用 | 类比 |

|------|------|------|

| Logger | 日志记录器，决定什么级别以上的日志往下传 | 主编 |

| Handler | 输出目标（控制台、文件等） | 渠道负责人 |

| Formatter | 定义输出格式 | 排版员 |

| Filter | 更精细的过滤（本次未用） | 校对员 |



\### 2. 日志级别从低到高

`DEBUG < INFO < WARNING < ERROR < CRITICAL`

\- Logger 本身设最低级别，各个 Handler 可再独立设置更严格级别，实现分层过滤。



\### 3. 关键配置

\- `RotatingFileHandler`：按文件大小切割，`maxBytes` 触发切割，`backupCount` 保留备份数量。

\- `colorlog.ColoredFormatter`：给控制台日志上色，不同级别不同颜色。

\- 日志格式中 `%(filename)s:%(lineno)d` 精确显示打印日志的代码位置。



\## 踩坑记录



\### 坑1：时间格式占位符写错

\*\*现象\*\*：`DATE\_FORMAT` 初始写成了 `"%Y-%m-%d %H:%m:%s"`，导致分钟和秒显示异常。

\*\*原因\*\*：Python `strftime` 中：

\- `%m` 是月份（01-12）

\- `%M` 才是分钟（00-59）

\- `%s` 不是标准占位符，应使用 `%S`（秒）

\*\*解决\*\*：修正为 `"%Y-%m-%d %H:%M:%S"`，时间恢复正常。



\### 坑2：重复 handler 导致日志重复输出

\*\*现象\*\*：模块多次导入时，同一条日志在控制台和文件中重复出现。

\*\*原因\*\*：每次调用 `setup\_logger` 都会 `addHandler`，而 FastAPI 热重载或模块重复导入会多次执行该函数。

\*\*解决方案\*\*：

```python

if logger.handlers:

&#x20;   return logger

```

首次配置后，logger 对象已持有 handler 列表，后续调用直接返回现有 logger，避免重复添加。



\### 坑3：`import os` 冗余导入

\*\*现象\*\*：代码中导入了 `os` 但从未使用。

\*\*解决\*\*：直接删除 `import os`，保持代码整洁。



\## exc\_info 打印堆栈使用场景

在所有 `try...except` 块中记录错误时，必须使用 `exc\_info=True`：

```python

try:

&#x20;   1 / 0

except ZeroDivisionError as e:

&#x20;   logger.error("发生除零异常", exc\_info=True)

```

作用：将完整的 Traceback 堆栈信息写入日志，是排查生产问题的核心依据。任何数据库异常、网络超时、业务异常等都应这样处理。



\## 生产环境日志级别调整策略

1\. 通过环境变量动态控制：

&#x20;  ```python

&#x20;  LOG\_LEVEL = logging.DEBUG if os.getenv("DEBUG") else logging.INFO

&#x20;  ```

2\. 文件 Handler 通常设为 `INFO` 或 `WARNING`，减少磁盘 I/O。

3\. 控制台在开发阶段全开 `DEBUG`，上线可提升至 `WARNING` 或完全关闭。

4\. 若接入日志收集系统（如 ELK），可考虑只输出到 stdout，由容器采集。



\## 运行验证

\- 启动 FastAPI，访问根路径 `/` → 控制台显示绿色 INFO 日志，`logs/app.log` 同步写入。

\- 访问 `/error` → 红色 ERROR 日志带完整堆栈，文件同样记录。

\- `logs` 目录自动创建，`app.log` 大小超过 5MB 后自动切割成 `app.log.1`, `app.log.2` 等。



\## 收获与总结

\- 工程化日志不仅仅是“把信息打印出来”，而是要有统一格式、分级过滤、持久化存储和异常回溯能力。

\- 防重复 handler 是 logging 配置中最常见的坑，`if logger.handlers:` 是标准解决方案。

\- `exc\_info=True` 必须成为异常处理的标准动作，否则日志失去排查价值。

\- 今天封装的 `logger\_demo.py` 可以直接复用到后续所有 Day 的项目中，真正实现“一次封装，全局使用”。

