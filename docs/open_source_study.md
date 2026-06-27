# Open Source Study: Dify-Inspired Mini RAG

## Why Dify?

Dify is a mainstream open-source LLM application platform. It is relevant to this internship because it covers common large-model application backend topics: workflow orchestration, RAG pipelines, model provider integration, APIs, and application deployment.

This project does not copy Dify. Instead, it implements a small backend feature inspired by the same product direction: a minimal knowledge-base retrieval API.

## What This Project Implements

The new knowledge module contains four endpoints:

```text
POST /knowledge/chunks
GET  /knowledge/chunks
POST /knowledge/search
POST /rag/answer
```

The simplified RAG flow is:

```text
write knowledge chunk -> retrieve relevant chunks -> assemble references -> generate answer text
```

In this version, retrieval uses keyword scoring instead of vector embeddings. This keeps the first implementation easy to run and easy to explain. A later version can replace keyword scoring with embedding vectors and a vector database.

## How It Maps To Backend Concepts

- `knowledge_chunks` table: stores source text snippets.
- `/knowledge/search`: reads recent chunks and ranks them by query relevance.
- `/rag/answer`: uses retrieved chunks as references and builds an answer.
- SQLite/MySQL compatibility: the same storage layer supports local demo and MySQL deployment.

## How To Explain In An Interview

You can say:

> I studied the direction of open-source LLM application platforms such as Dify. To avoid only reading without output, I added a mini knowledge retrieval module to my FastAPI backend. It stores knowledge chunks in the database, retrieves relevant chunks by query, and uses the retrieved content as context for an answer. The current version uses keyword scoring as a baseline, and the next step is replacing the scorer with embeddings and a vector database.

## Next Improvements

- Add embeddings for each knowledge chunk.
- Store vectors in a vector database or a MySQL-compatible vector extension.
- Let `/rag/answer` call GLM/OpenAI with retrieved context.
- Add Docker Compose for FastAPI + MySQL.
