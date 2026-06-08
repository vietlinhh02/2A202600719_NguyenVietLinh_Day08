"""
Task 7 — Reranking Module.

RRF (Reciprocal Rank Fusion): gộp kết quả từ nhiều ranker.
Công thức: score(d) = Σ 1/(k + rank_r(d))
"""
import hashlib
import math


def _content_key(item: dict) -> str:
    """Tạo key duy nhất từ content + metadata, tránh hash collision."""
    raw = item.get("content", "") + str(item.get("metadata", {}).get("chunk_index", ""))
    return hashlib.md5(raw.encode()).hexdigest()


def rerank_cross_encoder(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """Placeholder: pass-through khi chưa có Jina API key."""
    return candidates[:top_k]


def rerank_rrf(ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60) -> list[dict]:
    if not ranked_lists:
        return []

    rrf_scores: dict[str, float] = {}
    content_map: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            key = _content_key(item)
            rrf_scores[key] = rrf_scores.get(key, 0) + 1.0 / (k + rank)
            if key not in content_map:
                content_map[key] = item

    sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    results = []
    for content_key, score in sorted_items[:top_k]:
        item = dict(content_map[content_key])
        item["score"] = score
        results.append(item)

    return results


def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
    method: str = "rrf",
) -> list[dict]:
    if method == "cross_encoder":
        return rerank_cross_encoder(query, candidates, top_k)
    elif method == "rrf":
        # RRF với single list: rerank dựa trên rank gốc + diversity
        return _rerank_with_diversity(candidates, top_k)
    elif method == "mmr":
        return candidates[:top_k]
    else:
        raise ValueError(f"Unknown rerank method: {method}")


def _rerank_with_diversity(candidates: list[dict], top_k: int) -> list[dict]:
    """Rerank single list: ưu tiên relevance, phạt trùng lặp nội dung."""
    if len(candidates) <= top_k:
        return candidates

    selected = [candidates[0]]
    for cand in candidates[1:]:
        if len(selected) >= top_k:
            break
        max_overlap = 0
        cand_words = set(cand["content"].lower().split())
        for sel in selected:
            sel_words = set(sel["content"].lower().split())
            if sel_words:
                overlap = len(cand_words & sel_words) / len(sel_words)
                max_overlap = max(max_overlap, overlap)
        alpha = 0.7
        diversity_score = cand.get("score", 0) * alpha - max_overlap * (1 - alpha)
        if diversity_score > 0 or len(selected) < 2:
            selected.append(cand)

    if len(selected) < top_k:
        for cand in candidates[len(selected):]:
            if len(selected) >= top_k:
                break
            if cand not in selected:
                selected.append(cand)

    return selected
