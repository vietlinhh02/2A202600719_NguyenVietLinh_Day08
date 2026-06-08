"""
Task 9 — Retrieval Pipeline Hoàn Chỉnh.
"""
import logging

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank, rerank_rrf
from .task8_pageindex_vectorless import pageindex_search

logger = logging.getLogger(__name__)

SCORE_THRESHOLD = 0.3
DEFAULT_TOP_K = 5


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    dense = semantic_search(query, top_k=top_k)
    sparse = lexical_search(query, top_k=top_k)

    # Normalize BM25 score về range [0, 1] để so sánh công bằng với cosine
    if sparse:
        max_sparse = max(r["score"] for r in sparse)
        if max_sparse > 0:
            for item in sparse:
                item["score"] = item["score"] / max_sparse

    # Merge bằng RRF
    merged = rerank_rrf([dense, sparse], top_k=top_k * 2)
    for item in merged:
        item["source"] = "hybrid"

    # Rerank kết quả merged
    if use_reranking and len(merged) > 1:
        final_results = rerank(query, merged, top_k=top_k)
    else:
        final_results = merged[:top_k]

    # Fallback nếu kết quả yếu
    if not final_results or final_results[0]["score"] < score_threshold:
        logger.info("Hybrid score below threshold %.3f, trying PageIndex fallback", score_threshold)
        fallback = pageindex_search(query, top_k=top_k)
        if fallback:
            return fallback

    return final_results[:top_k]
