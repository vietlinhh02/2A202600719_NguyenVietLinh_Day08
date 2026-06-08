"""
Task 3 — Convert toàn bộ file trong data/landing/ thành Markdown.

Sử dụng MarkItDown của Microsoft:
    https://github.com/microsoft/markitdown

Cài đặt:
    pip install markitdown

Hướng dẫn:
    1. Scan toàn bộ file trong data/landing/ (PDF, DOCX, JSON)
    2. Convert sang Markdown
    3. Lưu vào data/standardized/ giữ nguyên cấu trúc thư mục
"""

import json
from pathlib import Path

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def _convert_legal_fallback(legal_dir, output_dir):
    """Fallback: extract text from PDFs using binary analysis of fpdf2 output."""
    for filepath in sorted(legal_dir.iterdir()):
        suffix = filepath.suffix.lower()
        if suffix not in (".pdf", ".docx", ".doc"):
            continue
        print(f"      Extracting text from: {filepath.name}")
        try:
            text = _extract_text_from_fpdf2_pdf(filepath)
            if text:
                output_path = output_dir / f"{filepath.stem}.md"
                output_path.write_text(text, encoding="utf-8")
                print(f"        Saved: {output_path.name} ({len(text)} chars)")
            else:
                print(f"        Could not extract text from {filepath.name}")
        except Exception as e:
            print(f"        ERROR: {e}")


def _extract_text_from_fpdf2_pdf(filepath):
    """Extract text from fpdf2-generated PDF by parsing stream objects."""
    content = filepath.read_bytes()
    text_parts = []
    i = 0
    while i < len(content):
        # Find BT (begin text) markers
        bt_idx = content.find(b'BT', i)
        if bt_idx == -1:
            break
        et_idx = content.find(b'ET', bt_idx)
        if et_idx == -1:
            break
        stream = content[bt_idx:et_idx + 2]
        # Extract text between parentheses in Tj or TJ operators
        import re
        texts = re.findall(rb'\(([^)]*)\)\s*Tj', stream)
        for t in texts:
            try:
                decoded = t.decode('latin-1')
                text_parts.append(decoded)
            except Exception:
                pass
        # Handle TJ arrays
        tj_arrays = re.findall(rb'\[(.*?)\]\s*TJ', stream, re.DOTALL)
        for arr in tj_arrays:
            arr_texts = re.findall(rb'\(([^)]*)\)', arr)
            line = ''.join(t.decode('latin-1') for t in arr_texts if t)
            if line.strip():
                text_parts.append(line)
        i = et_idx + 2
    return '\n'.join(text_parts)


def convert_legal_docs():
    """Convert PDF/DOCX files trong data/landing/legal/ sang markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not legal_dir.exists():
        print(f"  No legal directory at {legal_dir}")
        return

    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        for filepath in sorted(legal_dir.iterdir()):
            suffix = filepath.suffix.lower()
            if suffix in (".pdf", ".docx", ".doc"):
                print(f"      Converting: {filepath.name}")
                try:
                    result = md.convert(str(filepath))
                    output_path = output_dir / f"{filepath.stem}.md"
                    output_path.write_text(result.text_content, encoding="utf-8")
                    print(f"        Saved: {output_path.name}")
                except Exception as e:
                    print(f"        ERROR converting {filepath.name}: {e}")
    except ImportError:
        print("      markitdown not available, using basic PDF text extraction")
        _convert_legal_fallback(legal_dir, output_dir)


def convert_news_articles():
    """Convert JSON crawled articles trong data/landing/news/ sang markdown."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not news_dir.exists():
        print(f"  No news directory at {news_dir}")
        return

    for filepath in sorted(news_dir.iterdir()):
        if filepath.suffix.lower() == ".json":
            print(f"      Converting: {filepath.name}")
            data = json.loads(filepath.read_text(encoding="utf-8"))
            output_path = output_dir / f"{filepath.stem}.md"

            header = f"# {data.get('title', 'Unknown')}\n\n"
            header += f"**Source:** {data.get('url', 'N/A')}\n"
            header += f"**Crawled:** {data.get('date_crawled', 'N/A')}\n\n---\n\n"

            content = header + data.get("content_markdown", "")
            output_path.write_text(content, encoding="utf-8")
            print(f"        Saved: {output_path.name}")


def convert_all():
    """Convert toàn bộ files."""
    print("=" * 50)
    print("Task 3: Convert to Markdown (MarkItDown)")
    print("=" * 50)

    print("\n--- Legal Documents ---")
    convert_legal_docs()

    print("\n--- News Articles ---")
    convert_news_articles()

    print("\n✓ Done! Output tại:", OUTPUT_DIR)


if __name__ == "__main__":
    convert_all()
