# Day 1 后端入门笔记

## 今天到底要做什么

今天只做一件事：把一个 HTTP 接口跑起来。

你可以把它想象成：

```text
用户/前端/Apifox
    |
    |  HTTP POST /resume/analyze
    v
FastAPI 路由
    |
    |  Pydantic 校验请求体
    v
业务函数 analyze_resume
    |
    |  生成匹配分、建议、面试题
    v
JSON 响应
```

这就是后端的最小闭环。

## 为什么先不急着接大模型

因为大模型 API 本质上也是一个外部 HTTP 服务。

如果你连自己的接口还没有跑通，直接接大模型会同时遇到很多问题：

- 请求体怎么设计？
- 返回值怎么定义？
- 报错怎么处理？
- 模型返回不是 JSON 怎么办？
- 调用慢怎么办？

所以 Day 1 先用规则模拟分析逻辑。Day 2 再把规则函数替换为 LLM API 调用。

## FastAPI 在干什么

FastAPI 主要做三件事：

1. 路由：把 `/resume/analyze` 这个 URL 映射到一个 Python 函数。
2. 校验：根据 Pydantic 模型检查请求数据。
3. 序列化：把返回的 Python 对象转成 JSON。

代码例子：

```python
@app.post("/resume/analyze", response_model=AnalyzeResumeResponse)
def resume_analyze(request: AnalyzeResumeRequest) -> AnalyzeResumeResponse:
    return analyze_resume(request)
```

意思是：

- 这是一个 POST 接口。
- 路径是 `/resume/analyze`。
- 请求体必须符合 `AnalyzeResumeRequest`。
- 响应必须符合 `AnalyzeResumeResponse`。
- 真正的业务逻辑交给 `analyze_resume`。

## Pydantic 在干什么

Pydantic 相当于“数据门卫”。

比如：

```python
class AnalyzeResumeRequest(BaseModel):
    resume_text: str = Field(..., min_length=20)
    job_description: str = Field(..., min_length=20)
```

这表示：

- `resume_text` 必须是字符串。
- `resume_text` 至少 20 个字符。
- `job_description` 也一样。

如果请求不符合要求，FastAPI 会自动返回 422 错误。你不用手写一堆 `if`。

## GET 和 POST 的区别

- GET：通常用来查询，比如 `/health`。
- POST：通常用来提交数据，比如提交简历文本和岗位 JD。

所以：

- `/health` 用 GET。
- `/resume/analyze` 用 POST。

## 为什么返回 JSON

JSON 是前后端交流最常见的数据格式。

Python 字典：

```python
{"status": "ok"}
```

返回给客户端会变成 JSON：

```json
{
  "status": "ok"
}
```

浏览器、前端、Apifox、其他服务都能读懂。

## 今天你能写进简历的内容

如果你把这个项目跑通，可以写：

- 基于 FastAPI 实现简历分析后端最小原型，设计健康检查、简历/JD 匹配分析等 RESTful API。
- 使用 Pydantic 定义请求与响应模型，实现参数校验和结构化 JSON 输出。
- 根据岗位 JD 关键词生成匹配度、短板建议和模拟面试题，为后续接入大模型 API 做接口层准备。

