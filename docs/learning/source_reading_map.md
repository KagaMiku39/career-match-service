# 源码阅读地图：你需要理解到什么程度

你不需要一开始就能默写整个项目，但需要能按顺序讲清楚请求怎么走。

## 1. 一句话版本

```text
这个项目用 FastAPI 提供简历/JD 分析接口，用 Pydantic 定义请求响应结构，用 service.py 完成规则分析或可选 LLM 调用，用 SQLite 保存分析记录，并提供历史查询接口。
```

## 2. 文件职责

```text
main.py
  接口层，负责 URL + 方法 -> Python 函数。

schemas.py
  数据模型层，负责请求/响应结构和字段校验。

service.py
  业务逻辑层，负责分析简历和岗位 JD。

storage.py
  存储层，负责 SQLite 建表、插入、查询。
```

C++ 类比：

```text
schemas.py = struct 定义
service.py = solve()
storage.py = 文件/数据库读写函数
main.py = main() + 路由分发
```

## 3. POST /resume/analyze 的执行过程

1. 浏览器或 Swagger UI 发送请求：

```text
POST /resume/analyze
```

请求体是 JSON：

```json
{
  "resume_text": "...",
  "job_description": "...",
  "target_role": "大模型应用后端开发实习生",
  "use_llm": false
}
```

2. FastAPI 在 `main.py` 找到：

```python
@app.post("/resume/analyze", response_model=AnalyzeResumeResponse)
def resume_analyze(request: AnalyzeResumeRequest) -> AnalyzeResumeResponse:
```

3. Pydantic 按 `AnalyzeResumeRequest` 校验 JSON。

4. 调用：

```python
response = analyze_resume(request)
```

5. `service.py` 判断：

```python
if request.use_llm and os.getenv("LLM_API_KEY"):
```

如果请求要求用 LLM，并且环境变量里有 API Key，就尝试调用大模型。

否则走本地规则分析。

6. 本地规则分析会遍历：

```python
REQUIRED_KEYWORDS
```

把 JD 需要但简历没有的关键词放进 `missing_keywords`。

7. 算分并生成建议。

8. 回到 `main.py`，保存数据库：

```python
response.record_id = save_analysis(request, response)
```

9. FastAPI 把 `AnalyzeResumeResponse` 转成 JSON 返回。

## 4. GET /analyses 的执行过程

1. 客户端请求：

```text
GET /analyses
```

2. FastAPI 调用：

```python
def list_analyses(limit: int = 20) -> list[AnalysisRecord]:
    return list_analysis_records(limit=limit)
```

3. `storage.py` 执行 SQL：

```sql
SELECT id, target_role, match_score, matched_keywords, missing_keywords, created_at
FROM analysis_records
ORDER BY id DESC
LIMIT ?
```

4. 查询结果被转成 `AnalysisRecord` 列表。

5. 返回 JSON。

## 5. GET /analyses/{record_id} 的执行过程

1. 客户端请求：

```text
GET /analyses/1
```

2. FastAPI 把 URL 里的 `1` 解析成参数：

```python
record_id: int
```

3. 调用：

```python
get_analysis_record(record_id)
```

4. SQL 查询：

```sql
SELECT * FROM analysis_records WHERE id = ?
```

5. 如果找不到：

```python
raise HTTPException(status_code=404, detail="Analysis record not found.")
```

这会返回 HTTP 404。

6. 如果找到，返回详情 JSON。

## 6. 你面试时需要能讲清楚的点

你至少要能讲：

```text
为什么分 main/schemas/service/storage 四层。
Pydantic 做了什么。
SQLite 表里存了什么。
LLM 调用为什么要有 fallback。
为什么 API Key 放环境变量，不写死在代码里。
```

不用一开始就会讲：

```text
FastAPI 内部 ASGI 实现
SQLite B 树内部
HTTP 底层 socket
```

先讲业务链路就够。

