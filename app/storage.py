import json
import os
import sqlite3
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from app.schemas import (
    AnalysisRecord,
    AnalysisRecordDetail,
    AnalyzeResumeRequest,
    AnalyzeResumeResponse,
    KnowledgeChunk,
    KnowledgeChunkCreate,
)


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "analysis.db"


def is_mysql_enabled() -> bool:
    database_url = os.getenv("DATABASE_URL", "")
    return database_url.startswith("mysql://") or database_url.startswith("mysql+pymysql://")


def mysql_placeholders(count: int) -> str:
    return ", ".join(["%s"] * count)


def sqlite_placeholders(count: int) -> str:
    return ", ".join(["?"] * count)


def get_sqlite_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_mysql_connection() -> Any:
    try:
        import pymysql
    except ImportError as exc:
        raise RuntimeError("MySQL support requires PyMySQL. Run: pip install -r requirements.txt") from exc

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required when MySQL is enabled.")

    parsed = urlparse(database_url.replace("mysql+pymysql://", "mysql://", 1))
    if not parsed.hostname or not parsed.path.strip("/"):
        raise RuntimeError("DATABASE_URL must include host and database name.")

    return pymysql.connect(
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=unquote(parsed.username or ""),
        password=unquote(parsed.password or ""),
        database=parsed.path.lstrip("/"),
        charset="utf8mb4",
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor,
    )


def init_db() -> None:
    if is_mysql_enabled():
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS analysis_records (
                        id BIGINT PRIMARY KEY AUTO_INCREMENT,
                        target_role VARCHAR(128) NOT NULL,
                        resume_text TEXT NOT NULL,
                        job_description TEXT NOT NULL,
                        match_score INT NOT NULL,
                        matched_keywords JSON NOT NULL,
                        missing_keywords JSON NOT NULL,
                        strengths JSON NOT NULL,
                        suggestions JSON NOT NULL,
                        interview_questions JSON NOT NULL,
                        analysis_mode VARCHAR(32) NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_analysis_created_at (created_at),
                        INDEX idx_analysis_score (match_score)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS knowledge_chunks (
                        id BIGINT PRIMARY KEY AUTO_INCREMENT,
                        title VARCHAR(120) NOT NULL,
                        content TEXT NOT NULL,
                        tags JSON NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_knowledge_created_at (created_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
            conn.commit()
        finally:
            conn.close()
        return

    with get_sqlite_connection() as conn:
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_analysis(request: AnalyzeResumeRequest, response: AnalyzeResumeResponse) -> int:
    values = (
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
    )

    columns = """
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
    """

    if is_mysql_enabled():
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"INSERT INTO analysis_records ({columns}) VALUES ({mysql_placeholders(10)})",
                    values,
                )
                record_id = int(cursor.lastrowid)
            conn.commit()
            return record_id
        finally:
            conn.close()

    with get_sqlite_connection() as conn:
        cursor = conn.execute(
            f"INSERT INTO analysis_records ({columns}) VALUES ({sqlite_placeholders(10)})",
            values,
        )
        return int(cursor.lastrowid)


def list_analysis_records(limit: int = 20) -> list[AnalysisRecord]:
    limit = max(1, min(limit, 100))

    if is_mysql_enabled():
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, target_role, match_score, matched_keywords, missing_keywords, created_at
                    FROM analysis_records
                    ORDER BY id DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cursor.fetchall()
        finally:
            conn.close()
    else:
        with get_sqlite_connection() as conn:
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
            created_at=str(row["created_at"]),
        )
        for row in rows
    ]


def get_analysis_record(record_id: int) -> AnalysisRecordDetail | None:
    if is_mysql_enabled():
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM analysis_records WHERE id = %s", (record_id,))
                row = cursor.fetchone()
        finally:
            conn.close()
    else:
        with get_sqlite_connection() as conn:
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
        created_at=str(row["created_at"]),
    )


def save_knowledge_chunk(chunk: KnowledgeChunkCreate) -> int:
    values = (
        chunk.title,
        chunk.content,
        json.dumps(chunk.tags, ensure_ascii=False),
    )

    if is_mysql_enabled():
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO knowledge_chunks (title, content, tags) VALUES (%s, %s, %s)",
                    values,
                )
                chunk_id = int(cursor.lastrowid)
            conn.commit()
            return chunk_id
        finally:
            conn.close()

    with get_sqlite_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO knowledge_chunks (title, content, tags) VALUES (?, ?, ?)",
            values,
        )
        return int(cursor.lastrowid)


def list_knowledge_chunks(limit: int = 50) -> list[KnowledgeChunk]:
    limit = max(1, min(limit, 200))

    if is_mysql_enabled():
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, title, content, tags, created_at
                    FROM knowledge_chunks
                    ORDER BY id DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cursor.fetchall()
        finally:
            conn.close()
    else:
        with get_sqlite_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, title, content, tags, created_at
                FROM knowledge_chunks
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    return [
        KnowledgeChunk(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            tags=json.loads(row["tags"]),
            created_at=str(row["created_at"]),
        )
        for row in rows
    ]
