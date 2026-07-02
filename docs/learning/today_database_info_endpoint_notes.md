# Today: Add /database/info Endpoint

## 1. 这个接口做什么

新增只读接口：

```text
GET /database/info
```

当前返回：

```json
{
  database: sqlite,
  mysql_enabled: false,
  database_url_configured: false
}
```

## 2. 为什么要做

这个接口用于观察当前后端使用的数据库模式。

项目支持 SQLite 和 MySQL 两种模式：

- SQLite：默认本地演示，不需要额外启动数据库服务。
- MySQL：更接近真实业务环境，通过 DATABASE_URL 开启。

所以 `/database/info` 的价值是：不用看源码、不用猜环境变量，直接请求接口就能知道当前服务连的是哪类数据库。

## 3. 三处代码分别负责什么

### schemas.py

新增：

```python
class DatabaseInfoResponse(BaseModel):
    database: str
    mysql_enabled: bool
    database_url_configured: bool
```

它像 C++ 的返回结构体：

```cpp
struct DatabaseInfoResponse {
    string database;
    bool mysql_enabled;
    bool database_url_configured;
};
```

### storage.py

新增：

```python
def get_database_info() -> DatabaseInfoResponse:
    mysql_enabled = is_mysql_enabled()
    return DatabaseInfoResponse(
        database=mysql if mysql_enabled else sqlite,
        mysql_enabled=mysql_enabled,
        database_url_configured=bool(os.getenv(DATABASE_URL)),
    )
```

核心逻辑：

```text
如果 DATABASE_URL 是 mysql 开头，就认为当前使用 MySQL。
否则默认使用 SQLite。
```

### main.py

新增：

```python
@app.get(/database/info, response_model=DatabaseInfoResponse)
def database_info() -> DatabaseInfoResponse:
    return get_database_info()
```

它注册映射：

```text
GET /database/info -> database_info() -> get_database_info()
```

## 4. 今天遇到的 bug

### 404 Not Found

含义：

```text
FastAPI 没有注册这个路径。
```

这次原因是 storage 函数已经写了，但 main.py 路由没插进去。

### NameError: name 'sqlite' is not defined

含义：

```text
Python 把 sqlite 当变量名了，但这个变量没有定义。
```

原因是少了字符串引号。错误写法：

```python
database=mysql if mysql_enabled else sqlite
```

正确写法：

```python
database=mysql if mysql_enabled else sqlite
```

### SyntaxError: invalid syntax

含义：

```text
Python 代码语法不合法。
```

这次原因是装饰器里路径字符串少了引号：

```python
@app.get(/database/info)
```

正确写法：

```python
@app.get(/database/info)
```

## 5. 面试讲法

我给项目增加了 `/database/info` 接口，用于暴露当前数据库运行模式。项目默认使用 SQLite 方便本地演示，也可以通过 DATABASE_URL 切换到 MySQL。这个接口通过 storage 层判断数据库配置，再由 FastAPI 返回结构化 JSON，方便调试和确认运行环境。
