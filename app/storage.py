import json
import sqlite3
from pathlib import Path

from app.schemas import AnalyzeResumeRequest, AnalyzeResumeResponse, AnalysisRecord, AnalysisRecordDetail


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "analysis.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_role TEXT NOT NULL,
                resume_text TEXT NOT NULL,
                job_description TEXT NOT NULL,
                match_score INTEGER NOT NULL,
                matched_keywords TEXT NOT NULL,
                missing_keywords TEXT NOT NULL,
                strengths TEXT NOT NULL,
                suggestions TEXT NOT NULL,
                interview_questions TEXT NOT NULL,
                analysis_mode TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_analysis(request: AnalyzeResumeRequest, response: AnalyzeResumeResponse) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO analysis_records (
                target_role,
                resume_text,
                job_description,
                match_score,
                matched_keywords,
                missing_keywords,
                strengths,
                suggestions,
                interview_questions,
                analysis_mode
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                response.target_role,
                request.resume_text,
                request.job_description,
                response.match_score,
                json.dumps(response.matched_keywords, ensure_ascii=False),
                json.dumps(response.missing_keywords, ensure_ascii=False),
                json.dumps(response.strengths, ensure_ascii=False),
                json.dumps(response.suggestions, ensure_ascii=False),
                json.dumps(response.interview_questions, ensure_ascii=False),
                response.analysis_mode,
            ),
        )
        return int(cursor.lastrowid)


def list_analysis_records(limit: int = 20) -> list[AnalysisRecord]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, target_role, match_score, matched_keywords, missing_keywords, created_at
            FROM analysis_records
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        AnalysisRecord(
            id=row["id"],
            target_role=row["target_role"],
            match_score=row["match_score"],
            matched_keywords=json.loads(row["matched_keywords"]),
            missing_keywords=json.loads(row["missing_keywords"]),
            created_at=row["created_at"],
        )
        for row in rows
    ]


def get_analysis_record(record_id: int) -> AnalysisRecordDetail | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM analysis_records WHERE id = ?", (record_id,)).fetchone()

    if row is None:
        return None

    return AnalysisRecordDetail(
        id=row["id"],
        target_role=row["target_role"],
        resume_text=row["resume_text"],
        job_description=row["job_description"],
        match_score=row["match_score"],
        matched_keywords=json.loads(row["matched_keywords"]),
        missing_keywords=json.loads(row["missing_keywords"]),
        strengths=json.loads(row["strengths"]),
        suggestions=json.loads(row["suggestions"]),
        interview_questions=json.loads(row["interview_questions"]),
        analysis_mode=row["analysis_mode"],
        created_at=row["created_at"],
    )
