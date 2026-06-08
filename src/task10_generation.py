"""
Task 10 — Generation Có Citation.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from .task9_retrieval_pipeline import retrieve

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

SYSTEM_PROMPT = """Answer the following question comprehensively in Vietnamese.
For every statement of fact or claim, immediately insert a citation in brackets
linking to the specific source (e.g., [Luật Phòng chống ma túy 2021, Điều 3]
or [VnExpress, 2024]).

If the information is not explicitly stated in the provided context or knowledge
base, state 'Tôi không thể xác minh thông tin này từ nguồn hiện có' rather than
guessing.

Rules:
- Only use information from the provided context
- Every factual claim MUST have a citation
- If context is insufficient, say so clearly
- Structure your answer with clear paragraphs"""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Sắp xếp chunks để tránh "lost in the middle" (Liu et al. 2023).

    Input  (by score): [ 0,  1,  2,  3,  4 ]
    Output:            [ 0,  2,  4,  3,  1 ]
    Best → đầu, second-best → cuối, worst → giữa.
    """
    n = len(chunks)
    if n <= 2:
        return chunks

    reordered = []
    # Even indices (0, 2, 4...) — best chunks → front
    for i in range(0, n, 2):
        reordered.append(chunks[i])
    # Odd indices in reverse (n-1 or n-2 down to 1) — worse chunks → back
    start = n - 1 if n % 2 == 0 else n - 2
    for i in range(start, 0, -2):
        reordered.append(chunks[i])

    return reordered


def format_context(chunks: list[dict]) -> str:
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("metadata", {}).get("source", f"Source {i}")
        doc_type = chunk.get("metadata", {}).get("type", "unknown")
        context_parts.append(
            f"[Document {i} | Source: {source} | Type: {doc_type}]\n"
            f"{chunk['content']}\n"
        )
    return "\n---\n".join(context_parts)


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    chunks = retrieve(query, top_k=top_k)
    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    retrieval_source = "hybrid"
    if chunks:
        retrieval_source = chunks[0].get("source", "hybrid")

    user_message = f"""Context:\n{context}\n\n---\n\nQuestion: {query}"""

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-xxx") or len(api_key) < 20:
        return {
            "answer": "API key chưa được cấu hình. Vui lòng đặt OPENAI_API_KEY trong .env để sử dụng tính năng generation.",
            "sources": chunks,
            "retrieval_source": retrieval_source,
        }

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Lỗi khi gọi LLM: {str(e)}"

    return {"answer": answer, "sources": chunks, "retrieval_source": retrieval_source}
