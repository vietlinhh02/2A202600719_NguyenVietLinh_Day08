"""
Task 4 — Chunking & Indexing vào Vector Store.
"""
import logging
import pickle
from pathlib import Path

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
INDEX_FILE = Path(__file__).parent.parent / "data" / "index.pkl"

# =============================================================================
# CONFIGURATION
# =============================================================================

# Vì sao chọn CHUNK_SIZE=800: Đủ dài để chứa ngữ cảnh đầy đủ (vài điều luật/đoạn báo),
#   nhưng không quá dài để tránh diluting embedding quality.
CHUNK_SIZE = 800

# Vì sao chọn CHUNK_OVERLAP=100: Đảm bảo không mất thông tin ở ranh giới chunk.
CHUNK_OVERLAP = 100

CHUNKING_METHOD = "recursive"

# Vì sao chọn all-MiniLM-L6-v2: Nhẹ (384 dim), nhanh, phổ biến.
#   Dùng làm fallback vì bge-m3 cần download 2GB+ qua mạng.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

VECTOR_STORE = "inmemory"

_embed_model = None
_indexed_chunks: list[dict] = []


def _get_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embed_model


def _recursive_split(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    Splits text on separators in order: paragraphs → lines → sentences → words → chars.
    Builds chunks of size ≤ chunk_size with overlap between consecutive chunks.
    """
    separators = ["\n\n", "\n", ". ", " ", ""]
    splits = [text]

    for sep in separators:
        new_splits = []
        for s in splits:
            if len(s) <= chunk_size:
                new_splits.append(s)
            else:
                parts = s.split(sep)
                current = ""
                for part in parts:
                    combined = current + (sep if current else "") + part
                    if len(combined) > chunk_size:
                        if current.strip():
                            new_splits.append(current.rstrip())
                        # Start next chunk with overlap from end of previous
                        start_overlap = max(0, len(current) - overlap)
                        current = current[start_overlap:]
                        if len(current) + len(sep) + len(part) > chunk_size * 2:
                            # Force-split extremely large segments
                            if current.rstrip():
                                new_splits.append(current.rstrip())
                            current = part
                        else:
                            current = current + sep + part if current else part
                    else:
                        current = combined
                if current.strip():
                    new_splits.append(current.rstrip())
        splits = new_splits

    return [s for s in splits if len(s.strip()) >= 50]


def load_documents() -> list[dict]:
    documents = []
    if not STANDARDIZED_DIR.exists():
        return documents
    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        doc_type = "legal" if "legal" in str(md_file) else "news"
        documents.append({
            "content": content,
            "metadata": {"source": md_file.name, "type": doc_type}
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    chunks = []
    for doc in documents:
        splits = _recursive_split(doc["content"], CHUNK_SIZE, CHUNK_OVERLAP)
        for i, chunk_text in enumerate(splits):
            chunks.append({
                "content": chunk_text,
                "metadata": {**doc["metadata"], "chunk_index": i}
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    if not chunks:
        return chunks
    model = _get_model()
    texts = [c["content"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=False)
    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb.tolist()
    return chunks


def index_to_vectorstore(chunks: list[dict]):
    global _indexed_chunks
    _indexed_chunks = chunks
    _save_index()


def get_indexed_chunks() -> list[dict]:
    global _indexed_chunks
    if not _indexed_chunks:
        _load_index()
    return _indexed_chunks


def _save_index():
    if _indexed_chunks:
        data = {
            "chunks": _indexed_chunks,
            "model": EMBEDDING_MODEL,
            "dim": EMBEDDING_DIM,
        }
        INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(INDEX_FILE, "wb") as f:
            pickle.dump(data, f)


def _load_index():
    global _indexed_chunks
    if INDEX_FILE.exists():
        try:
            with open(INDEX_FILE, "rb") as f:
                data = pickle.load(f)
            _indexed_chunks = data.get("chunks", [])
            logger.info("Loaded %d chunks from %s", len(_indexed_chunks), INDEX_FILE)
        except (pickle.UnpicklingError, EOFError, FileNotFoundError, PermissionError) as e:
            logger.warning("Failed to load index from %s: %s", INDEX_FILE, e)
            _indexed_chunks = []


def run_pipeline():
    """Chạy toàn bộ pipeline: load → chunk → embed → index."""
    print("=" * 50)
    print("Task 4: Chunking & Indexing")
    print(f"  Chunking: {CHUNKING_METHOD} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    print(f"  Embedding: {EMBEDDING_MODEL} (dim={EMBEDDING_DIM})")
    print(f"  Vector Store: {VECTOR_STORE}")
    print("=" * 50)

    docs = load_documents()
    print(f"\n✓ Loaded {len(docs)} documents")

    chunks = chunk_documents(docs)
    print(f"✓ Created {len(chunks)} chunks")

    chunks = embed_chunks(chunks)
    print(f"✓ Embedded {len(chunks)} chunks")

    index_to_vectorstore(chunks)
    print("✓ Indexed to vector store")


if __name__ == "__main__":
    run_pipeline()
