# Dify-Inspired LLM Workflow API

This module is a small backend practice inspired by mainstream LLM application platforms such as Dify.

It focuses on one common backend workflow:

```text
create prompt template -> render variables -> optionally call LLM -> save workflow run
```

## Endpoints

```text
POST /workflow/templates
GET  /workflow/templates
GET  /workflow/templates/{template_id}
POST /workflow/run
GET  /workflow/runs
GET  /workflow/runs/{run_id}
```

## Why This Fits LLM Backend Development

Large-model applications usually need more than one hard-coded prompt. A backend service often needs to:

- manage prompt templates,
- render user/business variables into a prompt,
- call an LLM provider,
- save execution records for debugging and traceability,
- keep a fallback path when the LLM provider is not configured.

This module implements that minimum loop.

## Request Example

Create a template:

```json
{
  "name": "resume_gap_analyzer",
  "description": "Analyze the gap between a resume and a target LLM backend job.",
  "system_prompt": "You are a strict technical resume reviewer. Return concise and actionable advice.",
  "user_template": "Target role: {{target_role}}\n\nJob description:\n{{job_description}}\n\nResume:\n{{resume_text}}\n\nPlease summarize strengths, missing skills, and next actions.",
  "variables": ["target_role", "job_description", "resume_text"]
}
```

Run the workflow:

```json
{
  "template_id": 1,
  "inputs": {
    "target_role": "大模型应用后端开发实习生",
    "job_description": "需要 Python、数据库、Prompt、LLM API、RAG、Docker。",
    "resume_text": "数字媒体技术专业，ACM 算法训练，Unity 项目经验，正在补 FastAPI、MySQL 和大模型应用后端。"
  },
  "use_llm": false
}
```

When `use_llm` is `false` or `LLM_API_KEY` is missing, the service returns a local rendered prompt preview and stores the run record. When `use_llm` is `true` and the LLM environment variables are configured, it calls the OpenAI-compatible chat completions endpoint.

## Local Run Steps

```powershell
cd D:\Unity\Experiment\Farm_Final_Integration\career_match_service
.\.venv-codex\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

Open:

```text
http://127.0.0.1:8000/docs
```

Suggested manual demo order:

1. `POST /workflow/templates`
2. `GET /workflow/templates`
3. `POST /workflow/run`
4. `GET /workflow/runs`
5. `GET /workflow/runs/{run_id}`

If a required variable is missing, `/workflow/run` returns `400` with a clear error message. If the template id does not exist, it returns `404`.

## Interview Explanation

You can explain it like this:

> I studied the workflow direction of open-source LLM application platforms such as Dify and implemented a minimal workflow backend in my FastAPI project. It supports prompt template creation, variable rendering, optional OpenAI-compatible LLM calls, and execution record persistence. This helped me understand how a backend service wraps prompt engineering into stable APIs instead of writing prompts directly in scattered business code.
