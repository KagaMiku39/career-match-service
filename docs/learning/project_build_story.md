# 这个项目是怎么做出来的

目标：做一个能写进简历的大模型应用后端最小项目。

它现在不是完整商业系统，但已经覆盖了岗位 JD 里的几个关键词：

- FastAPI 后端 API
- Pydantic 请求/响应校验
- Prompt/LLM 调用骨架
- SQLite 数据库存储
- 接口文档 `/docs`
- 可演示的项目 README

## 1. 先定输入输出

后端项目不要一上来写一堆逻辑，先问：

```text
这个接口要吃什么？
这个接口要吐什么？
```

所以我们先写 `schemas.py`。

请求：

```python
class AnalyzeResumeRequest(BaseModel):
    resume_text: str
    job_description: str
    target_role: str
    use_llm: bool
```

意思是：

```text
客户端要提交简历文本、岗位 JD、目标岗位，以及是否尝试调用大模型。
```

响应：

```python
class AnalyzeResumeResponse(BaseModel):
    record_id: int | None
    target_role: str
    match_score: int
    matched_keywords: list[str]
    missing_keywords: list[str]
    strengths: list[str]
    suggestions: list[str]
    interview_questions: list[str]
    analysis_mode: str
```

意思是：

```text
后端要返回匹配分、已匹配关键词、缺失关键词、优势、建议、面试题、分析模式。
```

C++ 类比：

```text
schemas.py 就是先定义 Request / Response 两个 struct。
```

## 2. 再写业务逻辑

业务逻辑放在 `service.py`。

目前有两条路径：

```text
有 LLM_API_KEY 且 use_llm=true
  -> 尝试调用大模型

否则
  -> 使用本地规则分析
```

规则分析的核心很简单：

```text
遍历岗位关键词表：
  如果 JD 提到，简历也提到 -> matched
  如果 JD 提到，简历没提到 -> missing
```

然后根据匹配情况算分：

```python
score = 40 + len(matched) * 8 - len(missing) * 3
```

再根据 ACM/Unity 经历加分。

C++ 类比：

```text
service.py 就是 solve()。
```

## 3. 把业务逻辑挂成 API

接口入口在 `main.py`。

健康检查：

```python
@app.get("/health")
def health():
    ...
```

简历分析：

```python
@app.post("/resume/analyze")
def resume_analyze(request: AnalyzeResumeRequest):
    response = analyze_resume(request)
    response.record_id = save_analysis(request, response)
    return response
```

这一步做了三件事：

1. 接收 HTTP 请求。
2. 调用 `service.py` 的分析逻辑。
3. 把结果存入数据库并返回。

## 4. 加数据库保存记录

数据库逻辑放在 `storage.py`。

我们用的是 Python 自带的 `sqlite3`，所以不需要额外安装数据库服务。

启动时：

```python
init_db()
```

会创建表：

```sql
CREATE TABLE IF NOT EXISTS analysis_records (...)
```

每次调用分析接口：

```python
save_analysis(request, response)
```

会把这次分析保存到：

```text
data/analysis.db
```

## 5. 加查询历史接口

新增两个接口：

```text
GET /analyses
GET /analyses/{record_id}
```

第一个查历史列表。

第二个查某一条完整详情。

这让项目从“只会即时返回结果”变成了：

```text
能处理请求
能产生结果
能保存数据
能查询历史
```

这就更像一个后端应用，而不只是一个函数 demo。

## 6. 为什么先做规则，再做 LLM

真正的大模型调用需要 API key、网络和模型返回稳定性。

如果一开始就全靠模型，项目很容易因为 key、网络、额度、格式问题跑不起来。

所以我们先保留规则模式：

```text
没有 LLM_API_KEY 也能跑
```

再加可选 LLM 模式：

```text
配置 LLM_API_KEY 后可以尝试真实调用大模型
```

这在工程上更稳。

## 7. 今天可以写进简历的项目描述

项目名：AI 简历与岗位匹配分析后端系统

技术栈：Python、FastAPI、Pydantic、SQLite、OpenAI 兼容 API、JSON

项目描述：

基于 FastAPI 实现面向求职场景的简历/JD 匹配分析后端，支持提交简历文本和岗位描述，返回匹配分、优势、短板建议和模拟面试题，并将分析记录持久化到 SQLite，提供历史查询接口。

可以写的 bullet：

- 基于 FastAPI 设计并实现 `/resume/analyze`、`/analyses`、`/analyses/{record_id}` 等 RESTful API，完成简历/JD 分析与历史记录查询。
- 使用 Pydantic 定义请求和响应模型，实现字段校验、结构化 JSON 输出和自动接口文档生成。
- 使用 SQLite 存储分析记录，设计分析结果表，保存匹配分、关键词、建议和面试题等结构化数据。
- 设计 OpenAI 兼容大模型调用骨架，支持通过环境变量配置模型 API，并在未配置 API key 时自动回退到本地规则分析，保证服务可演示性。

