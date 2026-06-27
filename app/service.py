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
