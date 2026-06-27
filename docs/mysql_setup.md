# MySQL Setup

This project uses SQLite by default. MySQL is optional and is enabled by setting `DATABASE_URL`.

## 1. Create Database And User

Run these SQL statements in MySQL:

```sql
CREATE DATABASE career_match CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'career_user'@'localhost' IDENTIFIED BY 'career_password';

GRANT ALL PRIVILEGES ON career_match.* TO 'career_user'@'localhost';

FLUSH PRIVILEGES;
```

## 2. Configure `.env`

Copy `.env.example` to `.env`, then set:

```env
DATABASE_URL=mysql+pymysql://career_user:career_password@127.0.0.1:3306/career_match
```

The format is:

```text
mysql+pymysql://用户名:密码@主机地址:端口/数据库名
```

For local development, `127.0.0.1:3306` usually means "the MySQL server running on this computer".

## 3. Start The Service

```powershell
uvicorn app.main:app --reload --port 8000
```

When the service starts, `init_db()` creates the `analysis_records` table if it does not exist.

## Table Design

The MySQL table stores one row for each analysis request:

```sql
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## Why Store Lists As JSON?

Fields such as `matched_keywords`, `suggestions`, and `interview_questions` are naturally lists.

In C++ terms, you can think of them as `vector<string>`. A relational database row cannot directly store a C++ vector, so this project serializes the list into JSON before saving it, then parses the JSON back into `list[str]` when reading it.

## Why Add Indexes?

- `idx_analysis_created_at`: helps queries that list recent analysis records.
- `idx_analysis_score`: leaves room for future queries such as "find high-score analysis results".

An index is similar to a sorted auxiliary structure. Without it, the database may need to scan many rows; with it, the database can locate relevant rows more quickly.
