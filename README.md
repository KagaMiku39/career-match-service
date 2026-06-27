# CareerMatch Service

一个面向求职场景的简历与岗位 JD 匹配分析后端服务。

这个项目的目标不是做一个“全靠模型黑盒输出”的玩具 demo，而是先用可解释的规则分析跑通后端链路，再预留 GLM/OpenAI 兼容大模型接口。这样即使没有 API Key，服务也能稳定演示；有 API Key 时，可以切换到大模型分析模式。

## 功能

- 提供简历/JD 匹配分析接口，返回匹配分、优势、短板建议和模拟面试题。
- 使用 SQLite 保存每次分析记录。
- 提供历史记录列表和详情查询接口。
- 支持通过环境变量配置 OpenAI 兼容大模型 API，例如智谱 GLM。
- 未配置模型 API 或模型调用失败时，自动回退到本地规则分析。

## 技术栈

- Python
- FastAPI
- Pydantic
- SQLite
- OpenAI-compatible Chat Completions API

## 项目结构

```text
app/
  main.py       API 入口，声明路由
  schemas.py    请求和响应模型
  service.py    简历/JD 分析逻辑和可选 LLM 调用
  storage.py    SQLite 建表、插入、查询
docs/
  learning/     学习笔记和源码阅读记录
requirements.txt
.env.example
.gitignore
```

## 启动

建议使用 Python 3.12。

```powershell
cd D:\Unity\Experiment\Farm_Final_Integration\career_match_service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

浏览器打开：

```text
http://127.0.0.1:8000/docs
```

## API

### GET /health

检查服务是否正常运行。

### POST /resume/analyze

提交简历文本和岗位描述，返回匹配分析结果。

请求示例：

```json
{
  "resume_text": "数字媒体技术专业，长期进行 ACM 训练，开发过 Unity 农场项目，也在学习 Python FastAPI Prompt 大模型 API。",
  "job_description": "大模型应用后端开发实习生，要求 Python、数据库、Prompt、LLM API、RAG、Redis、Docker。",
  "target_role": "大模型应用后端开发实习生",
  "use_llm": false
}
```

响应示例：

```json
{
  "record_id": 1,
  "target_role": "大模型应用后端开发实习生",
  "match_score": 76,
  "matched_keywords": ["python", "fastapi", "llm api", "prompt"],
  "missing_keywords": ["database", "redis", "rag", "docker"],
  "strengths": ["具备算法训练经历，适合强调问题拆解、复杂度分析和快速学习能力。"],
  "suggestions": ["使用 SQLite 或 MySQL 保存分析记录，补充表结构设计说明。"],
  "interview_questions": ["如果让你设计一个简历分析的大模型后端接口，你会如何设计请求、响应和异常处理？"],
  "analysis_mode": "rule"
}
```

### GET /analyses

查询最近的分析记录。

### GET /analyses/{record_id}

查询某条分析记录详情。

## 可选：配置智谱 GLM

复制 `.env.example` 里的配置，或在 PowerShell 中设置环境变量：

```powershell
$env:LLM_API_KEY="your_api_key"
$env:LLM_BASE_URL="https://open.bigmodel.cn/api/paas/v4/chat/completions"
$env:LLM_MODEL="glm-5.2"
```

然后请求 `/resume/analyze` 时设置：

```json
{
  "use_llm": true
}
```

如果模型调用失败，服务会自动回退到规则分析模式。

## 设计取舍

- 第一版使用 SQLite，是为了快速验证持久化流程；后续可以迁移到 MySQL。
- 规则分析不是为了替代大模型，而是作为可解释 baseline 和模型失败时的 fallback。
- Prompt 要求模型返回 JSON，方便后端解析并转成固定响应结构。

更多设计记录见 [docs/design_notes.md](docs/design_notes.md)。

