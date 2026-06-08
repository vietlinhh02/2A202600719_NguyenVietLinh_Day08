"""
Task 5 — Semantic Search Module.
"""
import logging

import numpy as np

from .task4_chunking_indexing import get_indexed_chunks, _get_model

logger = logging.getLogger(__name__)


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    chunks = get_indexed_chunks()
    if not chunks:
        logger.debug("No indexed chunks available for semantic search")
        return []

    model = _get_model()
    query_emb = model.encode([query], show_progress_bar=False)[0]

    # Vectorized cosine similarity
    embeddings = np.array([c["embedding"] for c in chunks])
    query_norm = np.linalg.norm(query_emb)
    chunk_norms = np.linalg.norm(embeddings, axis=1)

    # Avoid division by zero
    denominator = np.maximum(query_norm * chunk_norms, 1e-10)
    scores = np.dot(embeddings, query_emb) / denominator

    # Get top_k indices
    if len(scores) <= top_k:
        top_indices = np.argsort(scores)[::-1]
    else:
        top_indices = np.argpartition(scores, -top_k)[-top_k:]
        top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]

    results = []
    for idx in top_indices:
        results.append({
            "content": chunks[idx]["content"],
            "score": float(scores[idx]),
            "metadata": chunks[idx]["metadata"]
        })

    return results
