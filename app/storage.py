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
    DatabaseInfoResponse,
    KnowledgeChunk,
    KnowledgeChunkCreate,
    PromptTemplate,
    PromptTemplateCreate,
    StatsResponse,
    WorkflowRunRecord,
    WorkflowRunResponse,
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
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS prompt_templates (
                        id BIGINT PRIMARY KEY AUTO_INCREMENT,
                        name VARCHAR(120) NOT NULL,
                        description VARCHAR(300) NOT NULL,
                        system_prompt TEXT NOT NULL,
                        user_template TEXT NOT NULL,
                        variables JSON NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_prompt_template_created_at (created_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS workflow_runs (
                        id BIGINT PRIMARY KEY AUTO_INCREMENT,
                        template_id BIGINT NOT NULL,
                        inputs JSON NOT NULL,
                        rendered_prompt TEXT NOT NULL,
                        output TEXT NOT NULL,
                        mode VARCHAR(32) NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_workflow_template_id (template_id),
                        INDEX idx_workflow_created_at (created_at)
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS prompt_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                system_prompt TEXT NOT NULL,
                user_template TEXT NOT NULL,
                variables TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS workflow_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                inputs TEXT NOT NULL,
                rendered_prompt TEXT NOT NULL,
                output TEXT NOT NULL,
                mode TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def count_table_rows(table_name: str) -> int:
    sql = f"SELECT COUNT(*) AS count FROM {table_name}"

    if is_mysql_enabled():
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()
                return int(row["count"])
        finally:
            conn.close()

    with get_sqlite_connection() as conn:
        row = conn.execute(sql).fetchone()
        return int(row["count"])


def get_stats() -> StatsResponse:
    return StatsResponse(
        analysis_count=count_table_rows("analysis_records"),
        knowledge_chunk_count=count_table_rows("knowledge_chunks"),
        prompt_template_count=count_table_rows("prompt_templates"),
        workflow_run_count=count_table_rows("workflow_runs"),
    )


def get_database_info() -> DatabaseInfoResponse:
    mysql_enabled = is_mysql_enabled()
    return DatabaseInfoResponse(
        database="mysql" if mysql_enabled else "sqlite",
        mysql_enabled=mysql_enabled,
        database_url_configured=bool(os.getenv("DATABASE_URL")),
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


def save_prompt_template(template: PromptTemplateCreate) -> int:
    values = (
        template.name,
        template.description,
        template.system_prompt,
        template.user_template,
        json.dumps(template.variables, ensure_ascii=False),
    )

    if is_mysql_enabled():
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO prompt_templates
                    (name, description, system_prompt, user_template, variables)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    values,
                )
                template_id = int(cursor.lastrowid)
            conn.commit()
            return template_id
        finally:
            conn.close()

    with get_sqlite_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO prompt_templates
            (name, description, system_prompt, user_template, variables)
            VALUES (?, ?, ?, ?, ?)
            """,
            values,
        )
        return int(cursor.lastrowid)


def list_prompt_templates(limit: int = 50) -> list[PromptTemplate]:
    limit = max(1, min(limit, 100))

    if is_mysql_enabled():
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, description, system_prompt, user_template, variables, created_at
                    FROM prompt_templates
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
                SELECT id, name, description, system_prompt, user_template, variables, created_at
                FROM prompt_templates
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    return [row_to_prompt_template(row) for row in rows]


def get_prompt_template(template_id: int) -> PromptTemplate | None:
    if is_mysql_enabled():
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM prompt_templates WHERE id = %s", (template_id,))
                row = cursor.fetchone()
        finally:
            conn.close()
    else:
        with get_sqlite_connection() as conn:
            row = conn.execute("SELECT * FROM prompt_templates WHERE id = ?", (template_id,)).fetchone()

    if row is None:
        return None
    return row_to_prompt_template(row)


def save_workflow_run(
    template_id: int,
    inputs: dict[str, str],
    rendered_prompt: str,
    output: str,
    mode: str,
) -> WorkflowRunResponse:
    values = (
        template_id,
        json.dumps(inputs, ensure_ascii=False),
        rendered_prompt,
        output,
        mode,
    )

    if is_mysql_enabled():
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO workflow_runs
                    (template_id, inputs, rendered_prompt, output, mode)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    values,
                )
                run_id = int(cursor.lastrowid)
                cursor.execute("SELECT created_at FROM workflow_runs WHERE id = %s", (run_id,))
                created_at = str(cursor.fetchone()["created_at"])
            conn.commit()
        finally:
            conn.close()
    else:
        with get_sqlite_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO workflow_runs
                (template_id, inputs, rendered_prompt, output, mode)
                VALUES (?, ?, ?, ?, ?)
                """,
                values,
            )
            run_id = int(cursor.lastrowid)
            row = conn.execute("SELECT created_at FROM workflow_runs WHERE id = ?", (run_id,)).fetchone()
            created_at = str(row["created_at"])

    return WorkflowRunResponse(
        run_id=run_id,
        template_id=template_id,
        rendered_prompt=rendered_prompt,
        output=output,
        mode=mode,
        created_at=created_at,
    )


def list_workflow_runs(limit: int = 50) -> list[WorkflowRunRecord]:
    limit = max(1, min(limit, 100))

    if is_mysql_enabled():
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, template_id, inputs, rendered_prompt, output, mode, created_at
                    FROM workflow_runs
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
                SELECT id, template_id, inputs, rendered_prompt, output, mode, created_at
                FROM workflow_runs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    return [row_to_workflow_run(row) for row in rows]


def get_workflow_run(run_id: int) -> WorkflowRunRecord | None:
    if is_mysql_enabled():
        conn = get_mysql_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM workflow_runs WHERE id = %s", (run_id,))
                row = cursor.fetchone()
        finally:
            conn.close()
    else:
        with get_sqlite_connection() as conn:
            row = conn.execute("SELECT * FROM workflow_runs WHERE id = ?", (run_id,)).fetchone()

    if row is None:
        return None
    return row_to_workflow_run(row)


def row_to_prompt_template(row: Any) -> PromptTemplate:
    return PromptTemplate(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        system_prompt=row["system_prompt"],
        user_template=row["user_template"],
        variables=json.loads(row["variables"]),
        created_at=str(row["created_at"]),
    )


def row_to_workflow_run(row: Any) -> WorkflowRunRecord:
    return WorkflowRunRecord(
        run_id=row["id"],
        template_id=row["template_id"],
        inputs=json.loads(row["inputs"]),
        rendered_prompt=row["rendered_prompt"],
        output=row["output"],
        mode=row["mode"],
        created_at=str(row["created_at"]),
    )

