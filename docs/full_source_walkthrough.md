# CareerMatch Service 完整源码导读

这份文档的目标：带你完整走一遍这个项目是怎么从 0 到 1 构建出来的，以及每个源码文件在做什么。

你可以把它当成“后端项目版题解”。和算法题题解类似，我们先讲问题、建模、数据结构、核心流程，再看代码。

## 1. 项目目标

这个项目叫：

```text
CareerMatch Service
```

它要解决的问题：

```text
输入：简历文本 + 岗位 JD
输出：匹配分、已匹配关键词、缺失关键词、优势、建议、模拟面试题
```

同时它还要做到：

```text
1. 提供 HTTP API，方便前端/浏览器/其他服务调用。
2. 用 Pydantic 校验请求和响应结构。
3. 把分析记录保存到 SQLite。
4. 支持查询历史分析记录。
5. 预留大模型 API 调用能力。
6. 如果大模型不可用，自动回退到本地规则分析。
```

这不是一个“大而全”的系统，而是一个岗位导向的最小闭环项目。

## 2. 从 C++ 算法角度看这个项目

你熟悉的算法程序通常是：

```text
读入 input
  -> 建结构体 / 数组 / map
  -> solve()
  -> 输出 answer
```

这个后端项目可以类比成：

```text
收到 HTTP JSON 请求
  -> Pydantic schema 校验并转成对象
  -> service.py 分析
  -> storage.py 存数据库
  -> 返回 JSON 响应
```

对应关系：

```text
schemas.py
  类似 C++ struct 定义

service.py
  类似 solve()

storage.py
  类似文件/数据库读写函数

main.py
  类似 main() + 路由分发
```

## 3. 项目目录

核心目录：

```text
career_match_service/
  app/
    __init__.py
    main.py
    schemas.py
    service.py
    storage.py
  docs/
    ...
  examples/
    analyze_request.json
  README.md
  requirements.txt
  .env.example
  .gitignore
```

真正运行项目只依赖：

```text
app/
requirements.txt
```

其他文档是为了 GitHub 展示、学习复盘和面试讲解。

## 4. 开发过程总览

这个项目不是一上来就写所有功能，而是按后端项目最小闭环逐步加：

### 第一步：定义输入输出

先确定 API 要接收什么、返回什么。

所以写：

```text
schemas.py
```

里面有：

```text
AnalyzeResumeRequest
AnalyzeResumeResponse
AnalysisRecord
AnalysisRecordDetail
```

### 第二步：写业务逻辑

先不用大模型，写一个可解释的规则 baseline。

所以写：

```text
service.py
```

核心逻辑：

```text
遍历岗位关键词表
看 JD 是否提到
看简历是否提到
生成 matched / missing
根据规则算分
生成建议和面试题
```

### 第三步：挂成 HTTP API

所以写：

```text
main.py
```

提供：

```text
GET /health
POST /resume/analyze
GET /analyses
GET /analyses/{record_id}
```

### 第四步：保存数据库

所以写：

```text
storage.py
```

使用 SQLite 保存分析记录。

### 第五步：预留大模型模式

在 `service.py` 里加：

```text
use_llm=true + LLM_API_KEY 存在
  -> 调用 LLM
否则
  -> 规则分析
```

这样项目有工程稳定性：

```text
模型可用时用模型
模型不可用时不崩溃
```

## 5. 请求完整链路

以 `POST /resume/analyze` 为例。

用户在 `/docs` 页面点 Execute，浏览器发请求：

```http
POST /resume/analyze HTTP/1.1
Content-Type: application/json

{
  "resume_text": "...",
  "job_description": "...",
  "target_role": "大模型应用后端开发实习生",
  "use_llm": false
}
```

后端执行：

```text
1. uvicorn 收到请求。
2. FastAPI 根据 POST + /resume/analyze 找到 main.py 的 resume_analyze。
3. Pydantic 根据 AnalyzeResumeRequest 校验 JSON。
4. main.py 调用 analyze_resume(request)。
5. service.py 执行业务分析。
6. main.py 调用 save_analysis(request, response)。
7. storage.py 把记录写入 SQLite。
8. main.py 返回 response。
9. FastAPI 把 response 转成 JSON。
10. 浏览器展示 JSON 响应。
```

C++ 伪代码：

```cpp
Request request = parse_json(input);
Response response = analyze_resume(request);
response.record_id = save_analysis(request, response);
print_json(response);
```

## 6. app/__init__.py

源码：

```python
"""CareerMatch Service package."""
```

这个文件的作用：

```text
告诉 Python：app 是一个 package。
```

package 可以理解成 Python 的代码包。

因为有它，我们才能写：

```python
from app.schemas import AnalyzeResumeRequest
```

这个文件本身没有业务逻辑。

## 7. app/main.py 完整源码

```python
from fastapi import FastAPI, HTTPException

from app.schemas import (
    AnalysisRecord,
    AnalysisRecordDetail,
    AnalyzeResumeRequest,
    AnalyzeResumeResponse,
    HealthResponse,
)
from app.service import analyze_resume
from app.storage import get_analysis_record, init_db, list_analysis_records, save_analysis

app = FastAPI(
    title="CareerMatch Service",
    description="A small FastAPI service for resume and job-description matching.",
    version="0.2.0",
)

init_db()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="career-match-service")


@app.post("/resume/analyze", response_model=AnalyzeResumeResponse)
def resume_analyze(request: AnalyzeResumeRequest) -> AnalyzeResumeResponse:
    response = analyze_resume(request)
    response.record_id = save_analysis(request, response)
    return response


@app.get("/analyses", response_model=list[AnalysisRecord])
def list_analyses(limit: int = 20) -> list[AnalysisRecord]:
    return list_analysis_records(limit=limit)


@app.get("/analyses/{record_id}", response_model=AnalysisRecordDetail)
def get_analysis(record_id: int) -> AnalysisRecordDetail:
    record = get_analysis_record(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
    return record
```

### 7.1 import 部分

```python
from fastapi import FastAPI, HTTPException
```

意思是：

```text
从 fastapi 包里导入 FastAPI 和 HTTPException。
```

`FastAPI` 用来创建应用。

`HTTPException` 用来返回 HTTP 错误，比如 404。

```python
from app.schemas import (...)
```

从 `schemas.py` 导入数据结构。

```python
from app.service import analyze_resume
```

从 `service.py` 导入业务函数。

```python
from app.storage import ...
```

从 `storage.py` 导入数据库函数。

### 7.2 创建 app

```python
app = FastAPI(...)
```

这个 `app` 是整个后端应用对象。

启动命令：

```powershell
uvicorn app.main:app --reload --port 8000
```

其中：

```text
app.main
  app 目录下的 main.py

:app
  main.py 里的 app 变量
```

### 7.3 init_db()

```python
init_db()
```

程序启动时创建数据库表。

如果表已经存在，就不重复创建。

### 7.4 GET /health

```python
@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="career-match-service")
```

这注册了一个接口：

```text
GET /health
```

作用是检查服务是否正常。

返回：

```json
{
  "status": "ok",
  "service": "career-match-service"
}
```

### 7.5 POST /resume/analyze

```python
@app.post("/resume/analyze", response_model=AnalyzeResumeResponse)
def resume_analyze(request: AnalyzeResumeRequest) -> AnalyzeResumeResponse:
    response = analyze_resume(request)
    response.record_id = save_analysis(request, response)
    return response
```

这是核心接口。

逐行看：

```python
request: AnalyzeResumeRequest
```

告诉 FastAPI：

```text
请求体 JSON 要按 AnalyzeResumeRequest 解析。
```

```python
response = analyze_resume(request)
```

调用业务逻辑，得到分析结果。

```python
response.record_id = save_analysis(request, response)
```

把请求和结果存入数据库，并把数据库自增 id 写回 response。

```python
return response
```

FastAPI 自动转成 JSON 返回。

### 7.6 GET /analyses

```python
@app.get("/analyses", response_model=list[AnalysisRecord])
def list_analyses(limit: int = 20) -> list[AnalysisRecord]:
    return list_analysis_records(limit=limit)
```

查询历史记录列表。

`limit: int = 20` 的意思：

```text
limit 是 int，默认值是 20。
```

访问：

```text
GET /analyses
```

默认查 20 条。

访问：

```text
GET /analyses?limit=5
```

查 5 条。

这里的 `?limit=5` 叫 query parameter，查询参数。

### 7.7 GET /analyses/{record_id}

```python
@app.get("/analyses/{record_id}", response_model=AnalysisRecordDetail)
def get_analysis(record_id: int) -> AnalysisRecordDetail:
```

这里的 `{record_id}` 是路径参数。

访问：

```text
GET /analyses/1
```

FastAPI 会把 URL 里的 `1` 传给函数：

```python
record_id = 1
```

如果数据库找不到：

```python
raise HTTPException(status_code=404, detail="Analysis record not found.")
```

返回 404。

## 8. app/schemas.py 完整源码

```python
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class AnalyzeResumeRequest(BaseModel):
    resume_text: str = Field(..., min_length=20, description="Resume text to analyze.")
    job_description: str = Field(..., min_length=20, description="Target job description.")
    target_role: str = Field(default="大模型应用后端开发实习生")
    use_llm: bool = Field(default=False, description="Whether to call an LLM provider when configured.")


class AnalyzeResumeResponse(BaseModel):
    record_id: int | None = None
    target_role: str
    match_score: int = Field(..., ge=0, le=100)
    matched_keywords: list[str]
    missing_keywords: list[str]
    strengths: list[str]
    suggestions: list[str]
    interview_questions: list[str]
    analysis_mode: str = Field(default="rule")


class AnalysisRecord(BaseModel):
    id: int
    target_role: str
    match_score: int
    matched_keywords: list[str]
    missing_keywords: list[str]
    created_at: str


class AnalysisRecordDetail(AnalysisRecord):
    resume_text: str
    job_description: str
    strengths: list[str]
    suggestions: list[str]
    interview_questions: list[str]
    analysis_mode: str
```

### 8.1 BaseModel

所有类都继承：

```python
BaseModel
```

这表示它们是 Pydantic 模型。

Pydantic 模型能做：

```text
1. 校验字段类型。
2. 把 JSON 转成 Python 对象。
3. 把 Python 对象转成 JSON。
4. 生成 /docs 里的 schema。
```

C++ 类比：

```cpp
struct AnalyzeResumeRequest {
    string resume_text;
    string job_description;
    string target_role;
    bool use_llm;
};
```

但 Pydantic 比 C++ struct 多了运行时校验。

### 8.2 Field

```python
resume_text: str = Field(..., min_length=20)
```

`...` 表示必填。

`min_length=20` 表示至少 20 个字符。

所以如果你在 `/docs` 里填：

```json
{
  "resume_text": "abc"
}
```

会返回 422。

因为字段太短或缺字段。

### 8.3 int | None

```python
record_id: int | None = None
```

意思是：

```text
record_id 可以是 int，也可以是 None。
默认是 None。
```

C++ 类比：

```cpp
optional<int> record_id;
```

### 8.4 AnalysisRecordDetail 继承 AnalysisRecord

```python
class AnalysisRecordDetail(AnalysisRecord):
```

意思是：

```text
AnalysisRecordDetail 拥有 AnalysisRecord 的字段，
再额外增加 resume_text、job_description 等详情字段。
```

C++ 类比：

```cpp
struct AnalysisRecordDetail : AnalysisRecord {
    string resume_text;
    string job_description;
    ...
};
```

## 9. app/service.py 完整源码

```python
import json
import os
import urllib.error
import urllib.request

from app.schemas import AnalyzeResumeRequest, AnalyzeResumeResponse


REQUIRED_KEYWORDS = {
    "python": ["python"],
    "fastapi": ["fastapi", "flask", "django"],
    "llm api": ["llm", "大模型", "openai", "gpt", "glm", "llama", "api"],
    "prompt": ["prompt", "提示词"],
    "database": ["mysql", "postgresql", "sqlite", "mongodb", "数据库", "sql"],
    "redis": ["redis", "缓存"],
    "rag": ["rag", "向量", "检索", "知识库"],
    "docker": ["docker", "部署", "容器"],
}


def analyze_resume(request: AnalyzeResumeRequest) -> AnalyzeResumeResponse:
    if request.use_llm and os.getenv("LLM_API_KEY"):
        llm_response = analyze_resume_with_llm(request)
        if llm_response is not None:
            return llm_response

    resume_lower = request.resume_text.lower()
    jd_lower = request.job_description.lower()
    combined_resume = resume_lower + " " + request.resume_text
    combined_jd = jd_lower + " " + request.job_description

    matched: list[str] = []
    missing: list[str] = []

    for label, aliases in REQUIRED_KEYWORDS.items():
        jd_mentions = any(alias in combined_jd for alias in aliases)
        resume_mentions = any(alias in combined_resume for alias in aliases)
        if jd_mentions and resume_mentions:
            matched.append(label)
        elif jd_mentions:
            missing.append(label)

    base_score = 40
    score = base_score + len(matched) * 8 - len(missing) * 3

    if any(word in combined_resume for word in ["acm", "icpc", "codeforces", "atcoder", "算法"]):
        score += 8
    if any(word in combined_resume for word in ["unity", "c#", "eventbus", "commandbus", "json"]):
        score += 8

    score = max(0, min(100, score))

    return AnalyzeResumeResponse(
        target_role=request.target_role,
        match_score=score,
        matched_keywords=matched,
        missing_keywords=missing,
        strengths=build_strengths(combined_resume),
        suggestions=build_suggestions(missing),
        interview_questions=build_interview_questions(missing),
        analysis_mode="rule",
    )


def analyze_resume_with_llm(request: AnalyzeResumeRequest) -> AnalyzeResumeResponse | None:
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1/chat/completions")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是严谨的中文技术简历顾问，只返回 JSON。"},
            {"role": "user", "content": build_llm_prompt(request)},
        ],
        "temperature": 0.2,
    }

    http_request = urllib.request.Request(
        base_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(http_request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError):
        return None

    try:
        data = json.loads(raw)
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return AnalyzeResumeResponse(
            target_role=request.target_role,
            match_score=parsed["match_score"],
            matched_keywords=parsed["matched_keywords"],
            missing_keywords=parsed["missing_keywords"],
            strengths=parsed["strengths"],
            suggestions=parsed["suggestions"],
            interview_questions=parsed["interview_questions"],
            analysis_mode="llm",
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def build_llm_prompt(request: AnalyzeResumeRequest) -> str:
    return f"""
请分析这份简历和目标岗位的匹配度，必须只返回 JSON，不要输出 Markdown。

目标岗位：{request.target_role}

岗位 JD：
{request.job_description}

简历文本：
{request.resume_text}

JSON 格式：
{{
  "match_score": 0 到 100 的整数,
  "matched_keywords": ["已经匹配的关键词"],
  "missing_keywords": ["仍缺失的关键词"],
  "strengths": ["候选人的优势"],
  "suggestions": ["简历或学习建议"],
  "interview_questions": ["可能被问到的面试题"]
}}
""".strip()


def build_strengths(resume_text: str) -> list[str]:
    strengths: list[str] = []
    if any(word in resume_text for word in ["acm", "icpc", "codeforces", "atcoder", "算法"]):
        strengths.append("具备算法训练经历，适合强调问题拆解、复杂度分析和快速学习能力。")
    if any(word in resume_text for word in ["unity", "c#", "eventbus", "commandbus", "json"]):
        strengths.append("有 Unity/C# 复杂项目经验，可迁移为模块拆分、事件解耦和数据驱动配置能力。")
    if any(word in resume_text for word in ["python", "fastapi", "api", "prompt", "大模型"]):
        strengths.append("已经出现大模型应用后端相关关键词，可以继续补充可运行项目证据。")

    if not strengths:
        strengths.append("当前简历信息较少，建议先补充项目、技术栈和可量化成果。")

    return strengths


def build_suggestions(missing_keywords: list[str]) -> list[str]:
    suggestion_map = {
        "python": "补充 Python 基础语法、类型标注和一个可运行后端项目。",
        "fastapi": "用 FastAPI 做 2-3 个 RESTful API，并截图自动生成的 /docs 页面。",
        "llm api": "接入一个 OpenAI 兼容大模型 API，完成简历分析或问答功能。",
        "prompt": "沉淀 2-3 个 Prompt 模板，并要求模型返回 JSON 结构化结果。",
        "database": "使用 SQLite 或 MySQL 保存分析记录，补充表结构设计说明。",
        "redis": "用 Redis 缓存重复 JD 分析结果，说明缓存 key 和过期时间设计。",
        "rag": "实现一个基于简历文本的简单检索问答接口，理解 RAG 的检索和生成两步。",
        "docker": "补充 Dockerfile 或 Docker Compose，让项目可以一条命令启动。",
    }
    return [suggestion_map[key] for key in missing_keywords] or ["当前关键词覆盖不错，建议补充项目截图、README 和接口示例。"]


def build_interview_questions(missing_keywords: list[str]) -> list[str]:
    questions = [
        "请介绍一次你从需求拆解到代码实现的项目经历。",
        "如果让你设计一个简历分析的大模型后端接口，你会如何设计请求、响应和异常处理？",
    ]

    if "database" in missing_keywords:
        questions.append("你会如何设计简历、岗位 JD 和分析记录这几张表？")
    if "rag" in missing_keywords:
        questions.append("请解释 RAG 为什么需要先检索再生成，它解决了什么问题？")
    if "redis" in missing_keywords:
        questions.append("哪些结果适合放进缓存？缓存失效时间你会怎么定？")

    return questions
```

### 9.1 REQUIRED_KEYWORDS

```python
REQUIRED_KEYWORDS = {
    "python": ["python"],
    "fastapi": ["fastapi", "flask", "django"],
    ...
}
```

这是规则分析用的关键词表。

它可以类比：

```cpp
unordered_map<string, vector<string>> required_keywords;
```

其中：

```text
key
  技能标签，例如 fastapi

value
  这个技能可能出现的关键词，例如 fastapi/flask/django
```

### 9.2 analyze_resume

这是核心业务函数。

第一段：

```python
if request.use_llm and os.getenv("LLM_API_KEY"):
```

意思是：

```text
如果用户要求用大模型，并且环境变量里有 API Key，
就尝试调用 LLM。
```

如果 LLM 成功：

```python
return llm_response
```

如果失败：

```text
继续往下走规则模式。
```

这叫 fallback。

### 9.3 lower

```python
resume_lower = request.resume_text.lower()
jd_lower = request.job_description.lower()
```

把英文转小写，避免：

```text
Python
python
PYTHON
```

匹配不上。

### 9.4 any 关键词匹配

```python
jd_mentions = any(alias in combined_jd for alias in aliases)
```

等价于：

```python
jd_mentions = False
for alias in aliases:
    if alias in combined_jd:
        jd_mentions = True
        break
```

C++ 类比：

```cpp
bool jd_mentions = false;
for (string alias : aliases) {
    if (combined_jd.find(alias) != string::npos) {
        jd_mentions = true;
        break;
    }
}
```

### 9.5 matched / missing

```python
if jd_mentions and resume_mentions:
    matched.append(label)
elif jd_mentions:
    missing.append(label)
```

含义：

```text
JD 提到，简历也提到 -> matched
JD 提到，简历没提到 -> missing
JD 没提到 -> 不管
```

### 9.6 算分

```python
score = 40 + len(matched) * 8 - len(missing) * 3
```

这是一个简单启发式评分。

不是机器学习，只是规则。

然后：

```python
score = max(0, min(100, score))
```

把分数限制在 0 到 100。

### 9.7 LLM 调用

```python
payload = {
    "model": model,
    "messages": [...],
    "temperature": 0.2,
}
```

构造模型请求体。

```python
urllib.request.Request(...)
```

构造 HTTP 请求。

```python
urllib.request.urlopen(...)
```

真正发送请求。

```python
json.loads(raw)
```

把模型服务返回的 JSON 字符串解析成 Python dict。

如果任何一步失败：

```python
return None
```

外层就会回退到规则模式。

## 10. app/storage.py 完整源码

```python
import json
import sqlite3
from pathlib import Path

from app.schemas import AnalyzeResumeRequest, AnalyzeResumeResponse, AnalysisRecord, AnalysisRecordDetail


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "analysis.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_role TEXT NOT NULL,
                resume_text TEXT NOT NULL,
                job_description TEXT NOT NULL,
                match_score INTEGER NOT NULL,
                matched_keywords TEXT NOT NULL,
                missing_keywords TEXT NOT NULL,
                strengths TEXT NOT NULL,
                suggestions TEXT NOT NULL,
                interview_questions TEXT NOT NULL,
                analysis_mode TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_analysis(request: AnalyzeResumeRequest, response: AnalyzeResumeResponse) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO analysis_records (
                target_role,
                resume_text,
                job_description,
                match_score,
                matched_keywords,
                missing_keywords,
                strengths,
                suggestions,
                interview_questions,
                analysis_mode
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                response.target_role,
                request.resume_text,
                request.job_description,
                response.match_score,
                json.dumps(response.matched_keywords, ensure_ascii=False),
                json.dumps(response.missing_keywords, ensure_ascii=False),
                json.dumps(response.strengths, ensure_ascii=False),
                json.dumps(response.suggestions, ensure_ascii=False),
                json.dumps(response.interview_questions, ensure_ascii=False),
                response.analysis_mode,
            ),
        )
        return int(cursor.lastrowid)


def list_analysis_records(limit: int = 20) -> list[AnalysisRecord]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, target_role, match_score, matched_keywords, missing_keywords, created_at
            FROM analysis_records
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        AnalysisRecord(
            id=row["id"],
            target_role=row["target_role"],
            match_score=row["match_score"],
            matched_keywords=json.loads(row["matched_keywords"]),
            missing_keywords=json.loads(row["missing_keywords"]),
            created_at=row["created_at"],
        )
        for row in rows
    ]


def get_analysis_record(record_id: int) -> AnalysisRecordDetail | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM analysis_records WHERE id = ?", (record_id,)).fetchone()

    if row is None:
        return None

    return AnalysisRecordDetail(
        id=row["id"],
        target_role=row["target_role"],
        resume_text=row["resume_text"],
        job_description=row["job_description"],
        match_score=row["match_score"],
        matched_keywords=json.loads(row["matched_keywords"]),
        missing_keywords=json.loads(row["missing_keywords"]),
        strengths=json.loads(row["strengths"]),
        suggestions=json.loads(row["suggestions"]),
        interview_questions=json.loads(row["interview_questions"]),
        analysis_mode=row["analysis_mode"],
        created_at=row["created_at"],
    )
```

### 10.1 DB_PATH

```python
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "analysis.db"
```

数据库文件路径。

`__file__` 是当前文件路径：

```text
app/storage.py
```

`.parent.parent` 回到项目目录：

```text
career_match_service/
```

所以数据库路径是：

```text
career_match_service/data/analysis.db
```

### 10.2 get_connection

```python
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
```

确保 `data/` 目录存在。

```python
conn = sqlite3.connect(DB_PATH)
```

连接 SQLite 数据库。

如果文件不存在，SQLite 会创建。

```python
conn.row_factory = sqlite3.Row
```

让查询结果可以用字段名访问：

```python
row["target_role"]
```

而不是只能用下标：

```python
row[1]
```

### 10.3 init_db

```sql
CREATE TABLE IF NOT EXISTS analysis_records (...)
```

建表。

`IF NOT EXISTS` 表示如果表已经存在就不报错。

字段：

```text
id
  主键，自增

target_role
  目标岗位

resume_text
  简历文本

job_description
  岗位 JD

match_score
  匹配分

matched_keywords
  已匹配关键词，JSON 字符串

missing_keywords
  缺失关键词，JSON 字符串

strengths
  优势，JSON 字符串

suggestions
  建议，JSON 字符串

interview_questions
  面试题，JSON 字符串

analysis_mode
  rule 或 llm

created_at
  创建时间
```

### 10.4 save_analysis

```python
INSERT INTO analysis_records (...)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
```

插入一条记录。

`?` 是占位符，防止 SQL 注入。

为什么 list 要 `json.dumps`？

因为数据库字段是 TEXT，不能直接存 Python list。

所以：

```python
["python", "fastapi"]
```

转成：

```json
["python", "fastapi"]
```

再作为字符串存进去。

### 10.5 list_analysis_records

SQL：

```sql
SELECT id, target_role, match_score, matched_keywords, missing_keywords, created_at
FROM analysis_records
ORDER BY id DESC
LIMIT ?
```

意思：

```text
查历史记录列表。
按 id 从大到小。
最多查 limit 条。
```

### 10.6 get_analysis_record

SQL：

```sql
SELECT * FROM analysis_records WHERE id = ?
```

意思：

```text
查某一条详情。
```

如果没有：

```python
return None
```

`main.py` 看到 None 后返回 404。

## 11. examples/analyze_request.json

源码：

```json
{
  "resume_text": "数字媒体技术专业，长期进行 ACM Codeforces AtCoder 算法训练，开发过 Unity C# JSON EventBus CommandBus 农场项目，也在学习 Python FastAPI API Prompt 大模型。",
  "job_description": "大模型应用后端开发实习生，要求 Python FastAPI LLM API Prompt MySQL Redis RAG Docker 数据库。",
  "target_role": "大模型应用后端开发实习生",
  "use_llm": false
}
```

这是给 `/docs` 页面测试用的示例请求。

你可以直接复制到 `POST /resume/analyze` 的 Request body。

## 12. requirements.txt

源码：

```text
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.4
```

作用：

```text
声明项目依赖。
```

安装：

```powershell
pip install -r requirements.txt
```

## 13. .env.example

源码大概是：

```text
LLM_API_KEY=replace_with_your_api_key
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/chat/completions
LLM_MODEL=glm-5.2
```

作用：

```text
告诉别人如果要用真实大模型 API，需要配置哪些环境变量。
```

真实 `.env` 不上传，因为里面可能有 API Key。

## 14. .gitignore

作用：

```text
告诉 Git 哪些文件不要上传。
```

比如：

```text
.venv/
.venv-codex/
data/
.env
*.db
__pycache__/
```

因为这些是：

```text
本地环境
运行数据
密钥
缓存文件
```

不应该上传 GitHub。

## 15. 你需要理解到什么程度

你现在不需要记住每个库函数的细节。

但你要能讲清楚：

```text
1. main.py 是接口入口。
2. schemas.py 定义请求/响应结构。
3. service.py 做规则分析和可选 LLM 调用。
4. storage.py 做 SQLite 持久化。
5. /resume/analyze 会分析并保存记录。
6. /analyses 会查历史。
7. LLM 失败时会 fallback 到规则分析。
```

## 16. 面试讲解版本

可以这样说：

```text
我做了一个 CareerMatch Service，用于简历和岗位 JD 的匹配分析。项目用 FastAPI 提供 RESTful API，用 Pydantic 定义请求和响应模型；核心分析逻辑在 service.py 中，先用关键词规则作为可解释 baseline，同时预留 OpenAI/GLM 兼容模型调用能力。每次分析结果会通过 storage.py 写入 SQLite，并提供 /analyses 和 /analyses/{record_id} 查询历史记录。为了保证可演示性，如果没有配置 API Key 或模型调用失败，服务会自动回退到本地规则分析。
```

这段话就是你对这个项目的主线理解。

## 17. 下一步如果要增强

按优先级：

```text
1. README 加截图。
2. 接入真实智谱 GLM API。
3. 增加 MySQL storage 版本。
4. 增加 Redis 缓存。
5. 增加 Dockerfile。
6. 增加 PDF 简历解析。
7. 做一个简单 RAG。
```

但投简历阶段，当前版本已经能作为项目经历初稿。

