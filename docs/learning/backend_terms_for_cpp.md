# 从 C++/算法视角理解后端词汇

你现在的基础是 C++ 语法、算法逻辑和刷题经验，所以先不要把后端想成很玄的东西。后端本质也是程序：

```text
读入输入 -> 处理逻辑 -> 输出结果
```

只不过刷题的输入输出来自标准输入和标准输出，后端的输入输出来自网络请求和 JSON 响应。

## 1. 后端

后端就是运行在服务器上的程序。

刷题里：

```cpp
int main() {
    cin >> n;
    solve();
    cout << ans;
}
```

后端里：

```python
@app.post("/resume/analyze")
def resume_analyze(request):
    result = analyze_resume(request)
    return result
```

区别是：

- C++ 程序通常跑一次就结束。
- 后端程序一直运行，等待别人来请求。

## 2. 服务器

服务器可以先理解成“一直开着的电脑 + 一直运行的程序”。

你现在本地启动的：

```text
http://127.0.0.1:8000
```

就是你电脑上的本地服务器。

`127.0.0.1` 表示“我自己这台电脑”，也叫 localhost。

## 3. 客户端

客户端就是发请求的一方。

可能是：

- 浏览器
- 前端网页
- Apifox/Postman
- 另一个后端服务
- Python 脚本

你打开 `/docs` 页面测试接口时，浏览器就是客户端。

## 4. HTTP

HTTP 是客户端和后端说话的协议。

你可以把它想成网络版的输入输出格式。

刷题平台规定：

```text
第一行 n m
接下来 m 行边
```

HTTP 规定：

```text
请求方法 + URL + 请求头 + 请求体
```

比如：

```text
POST /resume/analyze
Content-Type: application/json

{"resume_text": "...", "job_description": "..."}
```

## 5. URL

URL 是接口地址。

比如：

```text
http://127.0.0.1:8000/resume/analyze
```

可以拆成：

- `http://`：使用 HTTP 协议。
- `127.0.0.1`：服务器地址，本机。
- `8000`：端口。
- `/resume/analyze`：具体接口路径。

## 6. 端口

端口可以理解成一台电脑上的“服务窗口编号”。

同一台电脑可以同时跑很多服务：

- 8000：你的 FastAPI 后端。
- 3306：MySQL 常用端口。
- 6379：Redis 常用端口。

你现在启动的是：

```powershell
uvicorn app.main:app --reload --port 8000
```

意思是：把这个后端服务挂在 8000 号窗口。

## 7. API

API 就是别人调用你程序功能的入口。

刷题时，别人不能直接调用你的 `solve()`。但在后端里，我们会主动暴露一些“可调用函数”。

比如：

```text
GET /health
POST /resume/analyze
```

这两个就是 API。

## 8. 接口

在这个阶段，接口和 API 可以先当成一个意思。

一个接口通常要说清楚：

- 请求方法：GET 还是 POST。
- 请求路径：比如 `/resume/analyze`。
- 请求参数：需要传什么。
- 返回结果：会返回什么 JSON。

## 9. GET

GET 通常表示“查询”。

比如：

```text
GET /health
```

它没有复杂输入，只是问后端：你活着吗？

返回：

```json
{"status": "ok"}
```

## 10. POST

POST 通常表示“提交一份数据，让后端处理”。

比如：

```text
POST /resume/analyze
```

你提交：

```json
{
  "resume_text": "我的简历...",
  "job_description": "岗位描述..."
}
```

后端返回：

```json
{
  "match_score": 65,
  "suggestions": ["补充 FastAPI 项目"]
}
```

## 11. JSON

JSON 是前后端传数据最常用的格式。

它很像 C++ 里的结构体初始化，也像 Python 字典。

JSON：

```json
{
  "name": "KagaMiku39",
  "score": 65,
  "skills": ["C++", "Python", "Unity"]
}
```

对应 C++ 可以粗略想成：

```cpp
struct User {
    string name;
    int score;
    vector<string> skills;
};
```

## 12. 请求体

请求体就是客户端发给后端的主要数据。

对于这个项目：

```json
{
  "resume_text": "简历文本",
  "job_description": "岗位 JD"
}
```

这就是请求体。

它相当于刷题里的输入数据。

## 13. 响应

响应就是后端返回给客户端的数据。

对于这个项目：

```json
{
  "match_score": 65,
  "matched_keywords": ["python", "prompt"],
  "missing_keywords": ["redis", "rag"]
}
```

这就相当于刷题里的输出。

## 14. 路由

路由就是“URL 到函数的映射”。

代码：

```python
@app.post("/resume/analyze")
def resume_analyze(request):
    return analyze_resume(request)
```

意思是：

```text
如果有人 POST /resume/analyze
就执行 resume_analyze 这个函数
```

这有点像你根据题目编号选择运行哪个 `solve_xxx()`。

## 15. FastAPI

FastAPI 是 Python 的后端框架。

框架就是别人写好的基础设施，帮你处理重复工作。

FastAPI 帮你做：

- 接收 HTTP 请求。
- 根据路由找到函数。
- 校验参数。
- 返回 JSON。
- 自动生成接口文档 `/docs`。

你只需要写业务逻辑。

## 16. uvicorn

uvicorn 是启动 FastAPI 的服务器程序。

FastAPI 更像“你写的应用逻辑”，uvicorn 更像“真正把它跑起来并监听端口的人”。

启动命令：

```powershell
uvicorn app.main:app --reload --port 8000
```

拆开看：

- `uvicorn`：用 uvicorn 启动服务。
- `app.main:app`：找到 `app/main.py` 里的 `app` 对象。
- `--reload`：代码改了自动重启，开发时方便。
- `--port 8000`：监听 8000 端口。

## 17. Pydantic

Pydantic 是数据校验工具。

比如我们规定请求必须长这样：

```python
class AnalyzeResumeRequest(BaseModel):
    resume_text: str
    job_description: str
```

如果客户端少传了 `resume_text`，或者类型不对，FastAPI 会自动报错。

你可以把它理解为：

```cpp
struct AnalyzeResumeRequest {
    string resume_text;
    string job_description;
};
```

但 Pydantic 还能在运行时检查字段是否合法。

## 18. schema

schema 就是数据结构定义。

在 C++ 里你用 `struct` 定义数据结构。

在这个项目里，我们用 Pydantic 类定义请求和响应结构。

文件：

```text
app/schemas.py
```

里面的：

```python
class AnalyzeResumeRequest(BaseModel):
    ...
```

就是 schema。

## 19. service

service 是业务逻辑层。

你可以理解成刷题里的 `solve()`。

文件：

```text
app/service.py
```

里面的：

```python
def analyze_resume(request):
    ...
```

是真正分析简历和岗位 JD 的地方。

## 20. 虚拟环境

虚拟环境就是这个项目专用的 Python 依赖目录。

为什么需要它？

因为不同项目需要的包版本可能不同。

比如：

- 项目 A 需要 FastAPI 0.115。
- 项目 B 需要 FastAPI 0.100。

如果都装到全局 Python，容易互相影响。

虚拟环境就是给项目单独开一个“小房间”。

本项目使用：

```text
.venv-codex
```

## 21. pip

pip 是 Python 的包管理工具。

类似：

- C++ 的 vcpkg/conan，粗略类比。
- Node.js 的 npm。

命令：

```powershell
pip install -r requirements.txt
```

意思是：根据 `requirements.txt` 里的列表安装依赖。

## 22. requirements.txt

这是 Python 项目的依赖清单。

本项目：

```text
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.4
```

意思是项目需要这些包和版本。

## 23. ModuleNotFoundError

这是 Python 的“找不到模块”错误。

类似 C++ 编译时：

```text
fatal error: xxx.h: No such file or directory
```

你看到的：

```text
ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'
```

意思是 Python 想加载 `pydantic_core` 的底层模块，但没找到匹配的二进制文件。

这通常是环境问题，不是你接口代码的问题。

## 24. 今天最小理解

你现在只要记住这张图：

```text
客户端
  |
  | POST JSON
  v
FastAPI 路由
  |
  | Pydantic 校验
  v
service 业务逻辑
  |
  | Python 对象
  v
JSON 响应
```

这就是后端最小闭环。

等你理解这条链路之后，再学数据库、Redis、RAG、LLM API，就不会感觉所有词都同时砸过来。

