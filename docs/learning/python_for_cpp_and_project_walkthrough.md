# Python 语法速通与项目讲解

这份笔记按你的基础来写：你会 C++ 算法语法，能理解变量、函数、数组、map、结构体、类、枚举、调用栈、复杂度，但 Python 和后端工程写法还不熟。

## 1. Python 和 C++ 最大的差别

C++ 更像：

```cpp
int x = 3;
vector<string> a;
```

Python 更像：

```python
x = 3
a = []
```

Python 的变量不需要提前声明类型，解释器运行时知道它是什么。

你可以先粗暴理解成：

```text
Python 变量 ≈ auto 很多、语法更短、运行时检查更多
```

## 2. 缩进就是大括号

C++：

```cpp
if (x > 0) {
    cout << x;
}
```

Python：

```python
if x > 0:
    print(x)
```

Python 没有 `{}` 表示代码块，靠缩进表示。

所以这个：

```python
def solve():
    x = 1
    if x > 0:
        print(x)
```

相当于：

```cpp
void solve() {
    int x = 1;
    if (x > 0) {
        cout << x;
    }
}
```

## 3. 函数定义

C++：

```cpp
int add(int a, int b) {
    return a + b;
}
```

Python：

```python
def add(a: int, b: int) -> int:
    return a + b
```

这里：

- `def`：定义函数。
- `a: int`：类型提示，表示希望 a 是 int。
- `-> int`：类型提示，表示返回 int。
- `return`：返回结果。

注意：Python 的类型提示主要给人和工具看，不像 C++ 编译器那样强制。

## 4. list / dict 对应 C++ 什么

Python list：

```python
nums = [1, 2, 3]
nums.append(4)
```

类似 C++：

```cpp
vector<int> nums = {1, 2, 3};
nums.push_back(4);
```

Python dict：

```python
mp = {"python": 1, "fastapi": 2}
print(mp["python"])
```

类似 C++：

```cpp
unordered_map<string, int> mp;
mp["python"] = 1;
mp["fastapi"] = 2;
cout << mp["python"];
```

## 5. for 循环

C++：

```cpp
for (auto x : nums) {
    cout << x;
}
```

Python：

```python
for x in nums:
    print(x)
```

遍历字典：

```python
for key, value in mp.items():
    print(key, value)
```

类似：

```cpp
for (auto [key, value] : mp) {
    cout << key << value;
}
```

## 6. import 是什么

Python：

```python
from fastapi import FastAPI
```

类比 C++：

```cpp
#include <some_header>
using some_namespace::FastAPI;
```

意思是从 `fastapi` 这个包里拿到 `FastAPI` 这个类/对象。

本项目里：

```python
from app.schemas import AnalyzeResumeRequest
from app.service import analyze_resume
```

意思是：

```text
从 app/schemas.py 里导入 AnalyzeResumeRequest
从 app/service.py 里导入 analyze_resume
```

## 7. 类 class

C++：

```cpp
struct User {
    string name;
    int age;
};
```

普通 Python 类可以写：

```python
class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
```

但本项目里主要用的是 Pydantic 的类：

```python
class HealthResponse(BaseModel):
    status: str
    service: str
```

这更像 C++ 的结构体：

```cpp
struct HealthResponse {
    string status;
    string service;
};
```

不过它继承了 `BaseModel`，所以额外获得了：

- 字段校验。
- JSON 转对象。
- 对象转 JSON。
- 自动生成接口文档。

## 8. 继承

Python：

```python
class HealthResponse(BaseModel):
    ...
```

意思是：

```text
HealthResponse 继承 BaseModel
```

类比 C++：

```cpp
struct HealthResponse : BaseModel {
    string status;
    string service;
};
```

你暂时只要知道：

```text
继承 BaseModel 后，这个类就变成了 Pydantic 数据模型。
```

## 9. 装饰器 @app.get 是什么

这是 Python 里比较容易困惑的语法。

本项目里：

```python
@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="career-match-service")
```

`@app.get(...)` 叫装饰器。

你现在可以先不用理解它的底层实现，只要理解它的效果：

```text
把下面这个函数注册成一个接口。
```

也就是：

```text
GET /health -> health()
```

如果用 C++ 伪代码类比：

```cpp
routes[{GET, "/health"}] = health;
```

所以装饰器不是注释，它会真的执行注册逻辑。

## 10. 类型提示 list[str]

Python：

```python
matched_keywords: list[str]
```

意思是：

```text
matched_keywords 是字符串列表
```

类比 C++：

```cpp
vector<string> matched_keywords;
```

## 11. Field 是什么

本项目：

```python
resume_text: str = Field(..., min_length=20, description="Resume text to analyze.")
```

意思是：

```text
resume_text 是字符串
必须传
最少 20 个字符
文档描述是 Resume text to analyze.
```

`...` 在这里表示“必填”。

类比 C++ 不太自然，你可以把它当成：

```text
给这个字段附加校验规则
```

## 12. any(...) 是什么

本项目：

```python
jd_mentions = any(alias in combined_jd for alias in aliases)
```

意思是：

```text
aliases 里面只要有一个 alias 出现在 combined_jd 中，结果就是 True。
```

C++ 类比：

```cpp
bool jd_mentions = false;
for (auto alias : aliases) {
    if (combined_jd.find(alias) != string::npos) {
        jd_mentions = true;
        break;
    }
}
```

## 13. 这个项目的执行链路

项目结构：

```text
career_match_service/
  app/
    main.py
    schemas.py
    service.py
```

三层含义：

```text
main.py
  接口层，负责接 HTTP 请求

schemas.py
  数据结构层，负责定义请求和响应

service.py
  业务逻辑层，负责真正分析简历
```

类比 C++：

```text
schemas.py ≈ struct 定义
service.py ≈ solve()
main.py    ≈ main() 调度输入输出
```

## 14. main.py 讲解

代码：

```python
from fastapi import FastAPI

from app.schemas import AnalyzeResumeRequest, AnalyzeResumeResponse, HealthResponse
from app.service import analyze_resume
```

意思是导入需要用的类和函数。

代码：

```python
app = FastAPI(
    title="CareerMatch Service",
    description="A minimal backend for resume and job-description matching.",
    version="0.1.0",
)
```

意思是创建一个 FastAPI 应用对象。

这个 `app` 就是 uvicorn 启动时找的那个：

```powershell
uvicorn app.main:app --reload --port 8000
```

代码：

```python
@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="career-match-service")
```

意思是：

```text
GET /health
-> 调用 health()
-> 返回 HealthResponse
```

代码：

```python
@app.post("/resume/analyze", response_model=AnalyzeResumeResponse)
def resume_analyze(request: AnalyzeResumeRequest) -> AnalyzeResumeResponse:
    return analyze_resume(request)
```

意思是：

```text
POST /resume/analyze
-> 把 JSON 请求体解析成 AnalyzeResumeRequest
-> 调用 analyze_resume(request)
-> 返回 AnalyzeResumeResponse
```

## 15. schemas.py 讲解

```python
class AnalyzeResumeRequest(BaseModel):
    resume_text: str = Field(..., min_length=20, description="Resume text to analyze.")
    job_description: str = Field(..., min_length=20, description="Target job description.")
    target_role: str = Field(default="大模型应用后端开发实习生")
```

这定义了请求体。

也就是说，你 POST 的 JSON 至少应该有：

```json
{
  "resume_text": "至少 20 字",
  "job_description": "至少 20 字"
}
```

`target_role` 可以不传，不传就默认是：

```text
大模型应用后端开发实习生
```

响应：

```python
class AnalyzeResumeResponse(BaseModel):
    target_role: str
    match_score: int = Field(..., ge=0, le=100)
    matched_keywords: list[str]
    missing_keywords: list[str]
    strengths: list[str]
    suggestions: list[str]
    interview_questions: list[str]
```

意思是返回 JSON 一定长这样：

```json
{
  "target_role": "...",
  "match_score": 65,
  "matched_keywords": [],
  "missing_keywords": [],
  "strengths": [],
  "suggestions": [],
  "interview_questions": []
}
```

其中：

```python
Field(..., ge=0, le=100)
```

表示分数必须在 0 到 100 之间。

## 16. service.py 讲解

先看关键词表：

```python
REQUIRED_KEYWORDS = {
    "python": ["python"],
    "fastapi": ["fastapi", "flask", "django"],
    "llm api": ["llm", "大模型", "openai", "gpt", "glm", "llama", "api"],
    ...
}
```

这像一个 `map<string, vector<string>>`：

```cpp
unordered_map<string, vector<string>> required_keywords;
```

比如：

```text
"llm api"
```

这个技能标签下，有这些可能出现的关键词：

```text
llm、大模型、openai、gpt、glm、llama、api
```

核心分析：

```python
for label, aliases in REQUIRED_KEYWORDS.items():
    jd_mentions = any(alias in combined_jd for alias in aliases)
    resume_mentions = any(alias in combined_resume for alias in aliases)
    if jd_mentions and resume_mentions:
        matched.append(label)
    elif jd_mentions:
        missing.append(label)
```

意思是：

```text
遍历每个岗位需要的技能标签。
如果 JD 提到了这个技能，简历也提到了，则 matched。
如果 JD 提到了这个技能，但简历没提到，则 missing。
```

然后算分：

```python
score = 40 + len(matched) * 8 - len(missing) * 3
```

再根据算法和 Unity 经历加分：

```python
if any(word in combined_resume for word in ["acm", "icpc", "codeforces", "atcoder", "算法"]):
    score += 8
if any(word in combined_resume for word in ["unity", "c#", "eventbus", "commandbus", "json"]):
    score += 8
```

最后限制在 0 到 100：

```python
score = max(0, min(100, score))
```

类比 C++：

```cpp
score = max(0, min(100, score));
```

最后组装响应对象：

```python
return AnalyzeResumeResponse(
    target_role=request.target_role,
    match_score=score,
    matched_keywords=matched,
    missing_keywords=missing,
    strengths=strengths,
    suggestions=suggestions,
    interview_questions=questions,
)
```

这一步就像创建一个结构体并返回。

## 17. 你现在要会读的 Python 语法

先掌握这些就够：

```text
def                  定义函数
class                定义类
from ... import ...  导入
list[str]            字符串数组
dict                 字典/map
for x in xs          遍历
if / elif / else     分支
return               返回
@app.post            装饰器，注册接口
BaseModel            Pydantic 数据模型基类
Field                字段校验规则
```

## 18. 下一步要改哪里

如果你要增强项目：

想新增接口：

```text
改 main.py
```

想改变请求/响应字段：

```text
改 schemas.py
```

想改变分析逻辑：

```text
改 service.py
```

比如 Day 2 要接大模型 API，主要就是改：

```text
service.py
```

把现在的规则分析替换成：

```text
调用大模型 API -> 解析模型返回 -> 组装 AnalyzeResumeResponse
```

