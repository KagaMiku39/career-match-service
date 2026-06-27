# 后端基础详解：从 C++ 算法视角理解这个项目

这份笔记专门按你现在的基础来讲：你有 C++ 语法、算法、逻辑能力，但操作系统、计算机网络、Python、JSON、后端框架都还不熟。

先给一个总类比：

```text
C++ 刷题程序：
标准输入 cin
  -> main / solve
  -> 标准输出 cout

后端程序：
HTTP 请求
  -> 路由函数
  -> 业务逻辑函数
  -> HTTP JSON 响应
```

你暂时可以把“后端”理解成一种长期运行的 `solve()`，它不是从 `cin` 读数据，而是从网络请求里读数据。

## 1. API 不是抽象类

你说“API 像抽象类”，这个感觉有一点像，但不完全对。

在 C++ 里，抽象类强调：

```cpp
struct Interface {
    virtual void run() = 0;
};
```

它是代码内部的约定：谁继承它，谁就要实现 `run()`。

后端 API 更像是“对外暴露的函数调用入口”。

比如我们项目里有：

```text
POST /resume/analyze
```

它的意思是：

```text
外部的人可以通过这个地址调用简历分析功能。
```

所以 API 可以理解成：

```text
一个可以被外部调用的功能入口 + 它的输入输出约定
```

它和抽象类相似的地方：

- 都是在定义“别人怎么用我”。
- 都强调输入、输出、约定。

不同的地方：

- 抽象类是程序内部代码级别的约定。
- 后端 API 是网络级别的约定，调用者可能是浏览器、前端、手机 App、另一个后端服务。

## 2. URL 是地址，但不是文件路径

URL 当然是地址。

比如：

```text
http://127.0.0.1:8000/docs
```

可以拆成：

```text
http://        协议
127.0.0.1      主机地址，也就是你自己的电脑
8000           端口
/docs          路径
```

容易误解的是最后的 `/docs`。

它看起来像一个没有后缀的文件：

```text
docs
```

但在后端里，它不一定对应真实文件。

在传统静态网站里：

```text
/a.html
```

可能真的对应服务器上的一个 `a.html` 文件。

但在 FastAPI 里：

```text
/docs
```

通常不是文件，而是“路径标识”。服务器程序看到这个路径后，动态生成一个网页返回给浏览器。

所以：

```text
URL 是地址。
URL 后面的路径不一定是文件。
它可能只是服务器程序用来判断“该执行哪个逻辑”的字符串。
```

## 3. 路由不是一个程序，而是一张映射表

你问“难道路由是一个程序吗？”

更准确地说：路由是一种映射规则。

比如：

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

它表达的是：

```text
如果有人访问 GET /health
就调用 health 这个函数
```

再比如：

```python
@app.post("/resume/analyze")
def resume_analyze(request):
    return analyze_resume(request)
```

它表达的是：

```text
如果有人访问 POST /resume/analyze
就调用 resume_analyze 这个函数
```

所以路由可以类比成：

```cpp
if (path == "/health") {
    health();
} else if (path == "/resume/analyze") {
    resume_analyze();
}
```

FastAPI 帮你维护了这张 `path -> function` 的映射表。

## 4. POST 和 GET 不是包里的程序

你说“POST 这些是不是某个包里面的程序”，这个理解要修正一下。

GET、POST 不是 Python 包里的函数，也不是程序。

它们是 HTTP 协议规定的“请求方法”。

可以把它们理解成请求的动作类型：

```text
GET   我要读取/查询
POST  我要提交一份数据给你处理
PUT   我要整体更新
PATCH 我要局部更新
DELETE 我要删除
```

它们更像枚举值：

```cpp
enum HttpMethod {
    GET,
    POST,
    PUT,
    DELETE
};
```

区别是，HTTP 里它们以字符串形式出现在网络请求里。

例如浏览器/客户端发来的原始意思大概是：

```text
GET /docs HTTP/1.1
```

或者：

```text
POST /resume/analyze HTTP/1.1
Content-Type: application/json

{"resume_text": "...", "job_description": "..."}
```

FastAPI 看到 GET/POST，再结合路径，决定调用哪个函数。

## 5. 端口不是“用空间换更短编码”

你对端口数字有个感觉：“是不是用空间换更小的编码长度？”

不太是。

端口不是压缩编码。端口是一个 0 到 65535 之间的数字，用来区分同一台机器上的不同网络服务。

先看地址：

```text
127.0.0.1
```

这只能定位到“你的这台电脑”。

但一台电脑上可能同时运行很多服务：

```text
浏览器调试服务
Unity 相关服务
FastAPI 后端
MySQL 数据库
Redis 缓存
```

光知道“这台电脑”还不够，还要知道“找哪个服务”。

于是有端口：

```text
127.0.0.1:8000  -> 你的 FastAPI 服务
127.0.0.1:3306  -> MySQL 常用端口
127.0.0.1:6379  -> Redis 常用端口
```

可以类比成：

```text
IP 地址 = 学校地址
端口 = 学校里的窗口编号/教室编号
```

不是为了压缩长度，而是为了在同一台机器上区分不同服务。

从操作系统角度更底层一点说：

```text
某个进程监听 8000 端口。
当网络请求到达 127.0.0.1:8000 时，操作系统把这份数据交给监听 8000 端口的进程。
```

这里的进程就是 uvicorn 启动的那个 Python 后端服务。

## 6. 127.0.0.1 是什么

`127.0.0.1` 是本机回环地址。

你可以理解成：

```text
发给 127.0.0.1 的网络请求，不出你的电脑，直接绕回本机。
```

所以你现在打开：

```text
http://127.0.0.1:8000/docs
```

不是访问互联网上某台服务器，而是在访问你自己电脑上正在运行的 FastAPI 服务。

## 7. 包可以类比 namespace，但不完全一样

你说“包像程序集合，是打包好的 namespace”，这个类比可以用。

Python 包大概可以理解为：

```text
一组可以 import 的代码文件/模块
```

比如：

```python
from fastapi import FastAPI
```

意思是：

```text
从 fastapi 这个包里导入 FastAPI 这个类/对象
```

类比 C++：

```cpp
#include <vector>
using std::vector;
```

但 Python 包通常还包含：

- 多个 `.py` 文件。
- 子目录。
- 版本号。
- 依赖关系。
- 可安装信息。

所以它比 C++ 的 namespace 更偏“可安装的一组代码库”。

## 8. requirements.txt 是依赖清单

这个文件：

```text
requirements.txt
```

里面写：

```text
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.4
```

意思是：

```text
这个项目需要安装这些 Python 包。
```

你执行：

```powershell
pip install -r requirements.txt
```

就是让 pip 按这个清单把依赖下载并安装进虚拟环境。

## 9. 虚拟环境是什么

虚拟环境就是当前项目专用的 Python 运行小房间。

如果没有虚拟环境，所有项目都往全局 Python 里装包，会很容易乱。

比如：

```text
项目 A 需要 pydantic 2.10
项目 B 需要 pydantic 1.10
```

如果都装全局，版本会打架。

所以我们给这个项目建：

```text
.venv-codex
```

以后这个项目用自己的 Python、自己的 pip、自己的依赖。

你截图里的：

```text
(.venv-codex)
```

说明当前 PowerShell 已经进入这个虚拟环境了。

## 10. uvicorn 是什么

FastAPI 是你写后端逻辑用的框架。

uvicorn 是把这个后端服务真正跑起来的服务器程序。

你输入：

```powershell
uvicorn app.main:app --reload --port 8000
```

意思是：

```text
用 uvicorn 启动 app/main.py 里的 app 对象。
监听 8000 端口。
代码变化时自动重启。
```

拆开：

```text
uvicorn        启动服务的命令
app.main:app   app/main.py 里的 app 变量
--reload       开发模式，代码变了自动重启
--port 8000    使用 8000 端口
```

`app.main:app` 的第一个 `app` 是目录：

```text
app/
```

`main` 是文件：

```text
main.py
```

最后的 `app` 是代码里的变量：

```python
app = FastAPI(...)
```

## 11. /docs 是怎么来的

你没有写 `/docs` 这个接口，但它出现了。

这是 FastAPI 自动提供的接口文档页面。

它的原理是：

1. FastAPI 扫描你写过的路由。
2. 发现你有 `/health` 和 `/resume/analyze`。
3. 再读取你的请求/响应模型，也就是 Pydantic schema。
4. 自动生成 OpenAPI 描述文件。
5. 用 Swagger UI 把这些描述渲染成网页。

所以浏览器访问：

```text
GET /docs
```

FastAPI 返回一个接口测试网页。

这个网页又会请求：

```text
GET /openapi.json
```

所以你终端里看到：

```text
GET /docs HTTP/1.1 200 OK
GET /openapi.json HTTP/1.1 200 OK
```

这完全正常。

`/openapi.json` 是机器可读的接口说明书。

`/docs` 是人类可看的接口测试页面。

## 12. 200 OK 是什么

你终端里看到：

```text
200 OK
```

这是 HTTP 状态码。

可以类比成程序返回状态：

```text
200  成功
404  找不到路径
422  请求数据格式不对
500  服务器内部错误
```

所以截图里的：

```text
GET /docs HTTP/1.1 200 OK
GET /openapi.json HTTP/1.1 200 OK
```

说明浏览器成功拿到了文档页面和接口说明。

## 13. JSON 不是类，但可以像 struct

你说“JSON 大概知道是个类”，可以稍微修正一下。

JSON 不是类。

JSON 是一种数据格式。

它用文本表达数据：

```json
{
  "target_role": "大模型应用后端开发实习生",
  "match_score": 65,
  "missing_keywords": ["redis", "rag", "docker"]
}
```

你可以类比成 C++ 结构体的数据实例：

```cpp
struct AnalyzeResumeResponse {
    string target_role;
    int match_score;
    vector<string> missing_keywords;
};

AnalyzeResumeResponse res = {
    "大模型应用后端开发实习生",
    65,
    {"redis", "rag", "docker"}
};
```

区别是：

- C++ struct 是代码里的类型。
- JSON 是网络上传输的文本数据。

Pydantic 的 schema 才更像 C++ struct。

## 14. schema 是什么

schema 就是数据结构约定。

我们项目里：

```python
class AnalyzeResumeRequest(BaseModel):
    resume_text: str
    job_description: str
    target_role: str
```

这就规定了请求体应该长什么样。

类比 C++：

```cpp
struct AnalyzeResumeRequest {
    string resume_text;
    string job_description;
    string target_role;
};
```

FastAPI + Pydantic 会根据这个 schema 自动做校验。

如果你少传字段，或者类型不对，它会自动返回错误。

## 15. service 是什么

你说得对：这里的 service 感觉就是一个方法更小一层。

更准确地说，service 是业务逻辑层。

当前项目结构：

```text
app/main.py      负责接口入口
app/schemas.py   负责数据结构
app/service.py   负责业务逻辑
```

`main.py` 里：

```python
@app.post("/resume/analyze")
def resume_analyze(request):
    return analyze_resume(request)
```

它只是接请求。

真正做分析的是：

```python
def analyze_resume(request):
    ...
```

这在：

```text
app/service.py
```

类比 C++：

```cpp
int main() {
    read_input();
    solve();
    print_output();
}
```

这里：

```text
main.py 的路由函数 ≈ read_input + print_output 的入口
service.py 的 analyze_resume ≈ solve
schemas.py 的模型 ≈ struct
```

## 16. 这个项目到底怎么实现的

项目目录：

```text
ai_resume_backend/
  app/
    __init__.py
    main.py
    schemas.py
    service.py
  requirements.txt
  README.md
```

### main.py

负责创建 FastAPI 应用，并声明接口。

核心代码：

```python
app = FastAPI(...)
```

这创建了一个后端应用对象。

然后：

```python
@app.get("/health")
def health():
    return HealthResponse(status="ok", service="ai-resume-backend")
```

表示：

```text
GET /health -> 调用 health()
```

再然后：

```python
@app.post("/resume/analyze")
def resume_analyze(request: AnalyzeResumeRequest):
    return analyze_resume(request)
```

表示：

```text
POST /resume/analyze -> 调用 resume_analyze()
```

### schemas.py

负责定义输入输出的数据结构。

请求结构：

```python
class AnalyzeResumeRequest(BaseModel):
    resume_text: str
    job_description: str
    target_role: str
```

响应结构：

```python
class AnalyzeResumeResponse(BaseModel):
    target_role: str
    match_score: int
    matched_keywords: list[str]
    missing_keywords: list[str]
    strengths: list[str]
    suggestions: list[str]
    interview_questions: list[str]
```

这就像你定义两个 struct：

```cpp
struct Request { ... };
struct Response { ... };
```

### service.py

负责业务逻辑。

它先定义岗位关键词：

```python
REQUIRED_KEYWORDS = {
    "python": ["python"],
    "fastapi": ["fastapi", "flask", "django"],
    "llm api": ["llm", "大模型", "openai", "gpt", "glm", "llama", "api"],
    ...
}
```

然后分析：

```python
for label, aliases in REQUIRED_KEYWORDS.items():
    jd_mentions = any(alias in combined_jd for alias in aliases)
    resume_mentions = any(alias in combined_resume for alias in aliases)
```

意思是：

```text
对每个技能关键词：
  如果 JD 里提到了，简历里也提到了 -> matched
  如果 JD 里提到了，简历里没提到 -> missing
```

类比 C++：

```cpp
for (auto [label, aliases] : required_keywords) {
    bool jd_mentions = contains_any(jd, aliases);
    bool resume_mentions = contains_any(resume, aliases);

    if (jd_mentions && resume_mentions) matched.push_back(label);
    else if (jd_mentions) missing.push_back(label);
}
```

然后算分：

```python
score = 40 + len(matched) * 8 - len(missing) * 3
```

再根据是否有 ACM/Unity 关键词加分。

最后返回一个结构化结果。

## 17. 点击 /docs 页面时发生了什么

你截图里浏览器打开了：

```text
http://127.0.0.1:8000/docs
```

发生的事：

1. 浏览器向 `127.0.0.1:8000` 发送请求。
2. 操作系统发现 8000 端口由 uvicorn 进程监听。
3. 操作系统把请求交给 uvicorn。
4. uvicorn 把请求交给 FastAPI。
5. FastAPI 发现路径是 `/docs`。
6. FastAPI 返回 Swagger UI 文档网页。
7. 浏览器渲染页面。
8. 页面再请求 `/openapi.json` 拿接口结构。
9. 终端打印两行 `200 OK`。

这就是你截图里的日志。

## 18. 点击 POST /resume/analyze 时会发生什么

当你在 `/docs` 里点开 `POST /resume/analyze`，填 JSON，再点 Execute：

1. Swagger UI 在浏览器里构造一个 POST 请求。
2. 请求发给 `http://127.0.0.1:8000/resume/analyze`。
3. 请求体是你填的 JSON。
4. FastAPI 找到 `resume_analyze()`。
5. Pydantic 把 JSON 转成 `AnalyzeResumeRequest` 对象。
6. 如果字段不对，直接返回 422。
7. 如果字段正确，调用 `analyze_resume(request)`。
8. `service.py` 分析关键词、算分、生成建议。
9. 返回 `AnalyzeResumeResponse`。
10. FastAPI 把它转成 JSON。
11. 浏览器显示结果。

## 19. 你现在需要形成的正确心智模型

不要先想“框架很复杂”。

先想这三层：

```text
接口层 main.py
  负责：谁来调用我、路径是什么、GET 还是 POST

数据层 schemas.py
  负责：输入输出长什么样、字段类型是什么

业务层 service.py
  负责：拿到输入后怎么计算结果
```

类比 C++：

```text
struct Request / Response  -> schemas.py
solve()                    -> service.py
main() 输入输出调度         -> main.py
```

## 20. 你现在不用立刻学的东西

你现在不需要立刻深挖：

- TCP 三次握手。
- 操作系统进程调度。
- epoll / IOCP。
- HTTP/2。
- ASGI 内部实现。
- Swagger UI 前端源码。

这些以后可以学。

现在要先掌握：

```text
URL + 方法 + JSON 请求体
-> 路由函数
-> Pydantic 模型
-> service 业务逻辑
-> JSON 响应
```

这条链路就是后端入门的主线。

## 21. 你可以怎么向面试官解释

可以这样说：

我用 FastAPI 做了一个简历与岗位 JD 匹配分析后端。项目里把接口层、数据模型和业务逻辑分开：`main.py` 负责声明 RESTful API，`schemas.py` 用 Pydantic 定义请求和响应结构，`service.py` 实现关键词匹配、短板分析和面试题生成逻辑。服务通过 uvicorn 启动在本地 8000 端口，并由 FastAPI 自动生成 `/docs` 接口文档，方便测试和展示。

这段话不夸张，但已经像一个后端项目经历。

