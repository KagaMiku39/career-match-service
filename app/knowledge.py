import re

from app.schemas import (
    KnowledgeChunk,
    KnowledgeChunkCreate,
    KnowledgeSearchHit,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    RagAnswerRequest,
    RagAnswerResponse,
)
from app.storage import list_knowledge_chunks, save_knowledge_chunk


def create_knowledge_chunk(chunk: KnowledgeChunkCreate) -> KnowledgeChunk:
    chunk_id = save_knowledge_chunk(chunk)
    saved = list_knowledge_chunks(limit=1)[0]
    if saved.id == chunk_id:
        return saved
    return KnowledgeChunk(
        id=chunk_id,
        title=chunk.title,
        content=chunk.content,
        tags=chunk.tags,
        created_at="",
    )


def search_knowledge(request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    chunks = list_knowledge_chunks(limit=200)
    hits = rank_chunks(request.query, chunks)[: request.top_k]
    return KnowledgeSearchResponse(query=request.query, hits=hits)


def answer_with_retrieval(request: RagAnswerRequest) -> RagAnswerResponse:
    search_result = search_knowledge(
        KnowledgeSearchRequest(query=request.question, top_k=request.top_k)
    )

    if not search_result.hits:
        return RagAnswerResponse(
            question=request.question,
            answer="知识库中还没有检索到足够相关的资料片段，建议先通过 /knowledge/chunks 写入项目说明、岗位 JD 或学习笔记。",
            references=[],
        )

    reference_text = "\n".join(
        f"{index + 1}. {hit.title}: {hit.content}"
        for index, hit in enumerate(search_result.hits)
    )
    answer = (
        "根据当前知识库中最相关的资料，可以这样回答：\n"
        f"{reference_text}\n\n"
        "这一步是一个简化 RAG 流程：先检索相关资料，再把资料作为回答依据。"
    )
    return RagAnswerResponse(
        question=request.question,
        answer=answer,
        references=search_result.hits,
    )


def rank_chunks(query: str, chunks: list[KnowledgeChunk]) -> list[KnowledgeSearchHit]:
    query_terms = tokenize(query)
    scored: list[KnowledgeSearchHit] = []

    for chunk in chunks:
        haystack = " ".join([chunk.title, chunk.content, " ".join(chunk.tags)]).lower()
        score = 0
        for term in query_terms:
            if term in haystack:
                score += 1
                if term in chunk.title.lower():
                    score += 2
                if term in [tag.lower() for tag in chunk.tags]:
                    score += 2

        if score > 0:
            scored.append(
                KnowledgeSearchHit(
                    id=chunk.id,
                    title=chunk.title,
                    content=chunk.content,
                    tags=chunk.tags,
                    created_at=chunk.created_at,
                    score=score,
                )
            )

    return sorted(scored, key=lambda hit: (hit.score, hit.id), reverse=True)


def tokenize(text: str) -> list[str]:
    lower = text.lower()
    ascii_terms = re.findall(r"[a-z0-9_#+.-]+", lower)
    chinese_terms = re.findall(r"[\u4e00-\u9fff]{2,}", lower)
    terms = ascii_terms + chinese_terms
    return list(dict.fromkeys(term for term in terms if len(term) >= 2))
