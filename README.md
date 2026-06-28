# CareerMatch Service

A small FastAPI backend for resume and job-description matching.

This project is built as an interview-oriented backend practice project: it first provides a stable rule-based baseline, then keeps an OpenAI-compatible LLM integration path for providers such as Zhipu GLM. The service can run locally with SQLite and can switch to MySQL through configuration.

## Features

- Analyze resume text against a target job description.
- Return match score, matched keywords, missing keywords, strengths, improvement suggestions, and interview questions.
- Persist every analysis record.
- Query recent analysis records and analysis detail by id.
- Store and search knowledge chunks for a mini RAG-style workflow.
- Manage prompt templates and execute a small Dify-inspired LLM workflow.
- Use local rules as a reliable fallback when no LLM API key is configured.
- Optionally call an OpenAI-compatible Chat Completions API.
- Support SQLite by default and MySQL through `DATABASE_URL`.

## Tech Stack

- Python
- FastAPI
- Pydantic
- SQLite / MySQL
- PyMySQL
- OpenAI-compatible Chat Completions API

## Project Structure

```text
app/
  main.py       FastAPI app and route registration
  schemas.py    request and response models
  service.py    resume/JD analysis logic and optional LLM call
  storage.py    SQLite/MySQL persistence layer
docs/
  learning/     learning notes and source walkthroughs
  mysql_setup.md
examples/
  analyze_request.json
requirements.txt
.env.example
.gitignore
```

## Quick Start

```powershell
cd D:\Unity\Experiment\Farm_Final_Integration\career_match_service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open:

```text
http://127.0.0.1:8000/docs
```

## API

### GET `/health`

Check whether the service is running.

### POST `/resume/analyze`

Analyze resume text and job description.

Example request:

```json
{
  "resume_text": "数字媒体技术专业，长期进行 ACM/Codeforces/AtCoder 算法训练，参与 Unity 农场项目开发，负责背包、事件总线、JSON 数据配置和 Bug 修复，并学习 Python FastAPI 大模型应用后端。",
  "job_description": "大模型应用后端开发实习生，要求 Python、数据库、Prompt、LLM API、RAG、Redis、Docker。",
  "target_role": "大模型应用后端开发实习生",
  "use_llm": false
}
```

Example response:

```json
{
  "record_id": 1,
  "target_role": "大模型应用后端开发实习生",
  "match_score": 76,
  "matched_keywords": ["python", "fastapi", "llm api", "prompt", "database"],
  "missing_keywords": ["redis", "rag", "docker"],
  "strengths": ["具备算法训练经历，适合强调问题拆解、复杂度分析和快速学习能力。"],
  "suggestions": ["用 Redis 缓存重复 JD 分析结果，说明缓存 key 和过期时间设计。"],
  "interview_questions": ["如果让你设计一个简历分析的大模型后端接口，你会如何设计请求、响应和异常处理？"],
  "analysis_mode": "rule"
}
```

### GET `/analyses`

Query recent analysis records.

### GET `/analyses/{record_id}`

Query one analysis record detail.

### POST `/knowledge/chunks`

Create a knowledge chunk that can later be retrieved.

### POST `/knowledge/search`

Search related knowledge chunks with a lightweight keyword scorer.

### POST `/rag/answer`

Build an answer from retrieved knowledge chunks. This is a small RAG-style baseline inspired by mainstream LLM application platforms such as Dify.

### POST `/workflow/templates`

Create a prompt template with variables such as `{{resume_text}}` and `{{job_description}}`.

### GET `/workflow/templates`

List prompt templates.

### GET `/workflow/templates/{template_id}`

Get one prompt template detail.

### POST `/workflow/run`

Render a prompt template with input variables, optionally call an OpenAI-compatible LLM provider, and save the execution record.

### GET `/workflow/runs`

List recent workflow execution records.

### GET `/workflow/runs/{run_id}`

Get one workflow execution detail, including rendered prompt, output, input variables, mode, and created time.

## Optional: MySQL

SQLite is used when `DATABASE_URL` is empty. To switch to MySQL, create a `.env` file:

```env
DATABASE_URL=mysql+pymysql://career_user:career_password@127.0.0.1:3306/career_match
```

Then restart the service. See [docs/mysql_setup.md](docs/mysql_setup.md) for the SQL setup and design notes.

## Optional: Zhipu GLM

Add the following configuration to `.env`:

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/chat/completions
LLM_MODEL=glm-5.2
```

Then set `use_llm` to `true` in the `/resume/analyze` request. If the LLM call fails, the service falls back to local rule-based analysis.

## Design Notes

- SQLite is kept as the default because it makes the project easy to run locally.
- MySQL support is added through a storage layer, so the API and service logic do not need to care which database is used.
- Rule-based scoring is used as an explainable baseline and fallback.
- The mini RAG module uses keyword retrieval first, leaving a clear upgrade path to embeddings and vector search.
- The workflow module keeps prompt templates and execution records in the database, making prompt engineering easier to debug and reuse.
- The LLM prompt asks the model to return JSON, making the result easier for the backend to validate and store.
