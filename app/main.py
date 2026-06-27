from fastapi import FastAPI, HTTPException

from app.schemas import (
    AnalysisRecord,
    AnalysisRecordDetail,
    AnalyzeResumeRequest,
    AnalyzeResumeResponse,
    HealthResponse,
)
from app.service import analyze_resume
from app.storage import get_analysis_record, init_db, list_analysis_records, save_analysis

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
