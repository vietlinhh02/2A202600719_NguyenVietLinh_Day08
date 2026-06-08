"""
Task 6 — Lexical Search Module (BM25).

BM25 formula: score(q,d) = Σ IDF(qi) * (tf*(k1+1)) / (tf + k1*(1-b+b*|d|/avgdl))
k1=1.5 (term saturation), b=0.75 (length normalization)
"""
import logging
import math
import re
from pathlib import Path

logger = logging.getLogger(__name__)

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"

CORPUS: list[dict] = []
_bm25_data: dict = {}

# Unicode-aware pattern: matches Vietnamese letters, ASCII letters, digits
_WORD_RE = re.compile(r"[\wàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ]+", re.UNICODE)


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _WORD_RE.findall(text) if len(t) > 1]


def _load_corpus():
    global CORPUS
    if CORPUS:
        return
    if not STANDARDIZED_DIR.exists():
        return
    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        doc_type = "legal" if "legal" in str(md_file) else "news"
        CORPUS.append({
            "content": content,
            "metadata": {"source": md_file.name, "type": doc_type}
        })
    logger.info("Loaded %d documents into BM25 corpus", len(CORPUS))


class SimpleBM25:
    def __init__(self, corpus_docs: list[dict], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs = corpus_docs
        self.tokenized = [_tokenize(d["content"]) for d in corpus_docs]
        self.doc_len = [len(t) for t in self.tokenized]
        self.avgdl = sum(self.doc_len) / max(len(self.doc_len), 1)
        self.N = len(self.tokenized)
        self._df: dict[str, int] = {}
        # Precompute TF maps per doc: doc_idx -> {term: tf}
        self._tf_maps: list[dict[str, int]] = []
        self._build_index()

    def _build_index(self):
        for tokens in self.tokenized:
            tf_map: dict[str, int] = {}
            for t in tokens:
                tf_map[t] = tf_map.get(t, 0) + 1
            self._tf_maps.append(tf_map)
            seen = set(tf_map.keys())
            for t in seen:
                self._df[t] = self._df.get(t, 0) + 1

    def _idf(self, term: str) -> float:
        n = self._df.get(term, 0)
        return math.log((self.N - n + 0.5) / (n + 0.5) + 1.0)

    def get_scores(self, query_tokens: list[str]) -> list[float]:
        idf_cache = {qt: self._idf(qt) for qt in set(query_tokens)}
        scores = []
        for i in range(self.N):
            score = 0.0
            tf_map = self._tf_maps[i]
            doc_len = self.doc_len[i]
            for qt in query_tokens:
                tf = tf_map.get(qt, 0)
                if tf == 0:
                    continue
                idf = idf_cache[qt]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / max(self.avgdl, 1))
                score += idf * numerator / denominator
            scores.append(score)
        return scores


def _get_bm25():
    global _bm25_data
    _load_corpus()
    if "bm25" not in _bm25_data:
        _bm25_data["bm25"] = SimpleBM25(CORPUS)
    return _bm25_data["bm25"]


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    _load_corpus()
    if not CORPUS:
        return []

    bm25 = _get_bm25()
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    scores = bm25.get_scores(query_tokens)

    results = []
    for i, score in enumerate(scores):
        if score > 0:
            results.append({
                "content": CORPUS[i]["content"],
                "score": float(score),
                "metadata": CORPUS[i]["metadata"]
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
