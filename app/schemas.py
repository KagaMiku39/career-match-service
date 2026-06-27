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
