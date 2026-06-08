"""
Task 8 — PageIndex Vectorless RAG.

Đăng ký tài khoản tại: https://pageindex.ai/
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def upload_documents():
    if not PAGEINDEX_API_KEY or PAGEINDEX_API_KEY in ("", "pi_xxx"):
        print("  PageIndex API key not configured - skipping upload")
        return
    print("  Uploading documents to PageIndex (not implemented)")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    if not PAGEINDEX_API_KEY or PAGEINDEX_API_KEY in ("", "pi_xxx"):
        return []

    return []
