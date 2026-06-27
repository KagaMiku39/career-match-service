from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from app.schemas import (
    AnalysisRecord,
    AnalysisRecordDetail,
    AnalyzeResumeRequest,
    AnalyzeResumeResponse,
    HealthResponse,
    KnowledgeChunk,
    KnowledgeChunkCreate,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    RagAnswerRequest,
    RagAnswerResponse,
)
from app.knowledge import create_knowledge_chunk, answer_with_retrieval, search_knowledge
from app.service import analyze_resume
from app.storage import get_analysis_record, init_db, list_analysis_records, list_knowledge_chunks, save_analysis

load_dotenv()

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


@app.post("/knowledge/chunks", response_model=KnowledgeChunk)
def create_chunk(chunk: KnowledgeChunkCreate) -> KnowledgeChunk:
    return create_knowledge_chunk(chunk)


@app.get("/knowledge/chunks", response_model=list[KnowledgeChunk])
def list_chunks(limit: int = 50) -> list[KnowledgeChunk]:
    return list_knowledge_chunks(limit=limit)


@app.post("/knowledge/search", response_model=KnowledgeSearchResponse)
def search_chunks(request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    return search_knowledge(request)


@app.post("/rag/answer", response_model=RagAnswerResponse)
def rag_answer(request: RagAnswerRequest) -> RagAnswerResponse:
    return answer_with_retrieval(request)
