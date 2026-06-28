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


class KnowledgeChunkCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=120)
    content: str = Field(..., min_length=20)
    tags: list[str] = Field(default_factory=list)


class KnowledgeChunk(BaseModel):
    id: int
    title: str
    content: str
    tags: list[str]
    created_at: str


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(default=3, ge=1, le=10)


class KnowledgeSearchHit(KnowledgeChunk):
    score: int


class KnowledgeSearchResponse(BaseModel):
    query: str
    hits: list[KnowledgeSearchHit]


class RagAnswerRequest(BaseModel):
    question: str = Field(..., min_length=2)
    top_k: int = Field(default=3, ge=1, le=10)


class RagAnswerResponse(BaseModel):
    question: str
    answer: str
    references: list[KnowledgeSearchHit]


class PromptTemplateCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: str = Field(default="", max_length=300)
    system_prompt: str = Field(default="You are a helpful assistant.")
    user_template: str = Field(..., min_length=10)
    variables: list[str] = Field(default_factory=list)


class PromptTemplate(BaseModel):
    id: int
    name: str
    description: str
    system_prompt: str
    user_template: str
    variables: list[str]
    created_at: str


class WorkflowRunRequest(BaseModel):
    template_id: int
    inputs: dict[str, str] = Field(default_factory=dict)
    use_llm: bool = Field(default=False)


class WorkflowRunResponse(BaseModel):
    run_id: int
    template_id: int
    rendered_prompt: str
    output: str
    mode: str
    created_at: str


class WorkflowRunRecord(WorkflowRunResponse):
    inputs: dict[str, str]
