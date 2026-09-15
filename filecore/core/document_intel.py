"""
FileCore Document Intelligence Engine
Local-only text extraction and summarization for PDF, DOCX, TXT, MD, CSV, JSON, code files.
Clearly labeled as "Processed locally".
"""

import os
from pathlib import Path

SUPPORTED_TEXT_EXTENSIONS = {
    ".txt", ".md", ".py", ".js", ".ts", ".jsx", ".tsx",
    ".json", ".csv", ".yaml", ".yml", ".html", ".css",
    ".xml", ".sql", ".sh", ".bat", ".rs", ".go", ".java", ".c", ".cpp", ".h"
}


def extract_text(file_path: str, extension: str = None) -> str:
    """Extract plain text from a file. Returns empty string on failure."""
    ext = extension or Path(file_path).suffix.lower()

    try:
        # Plain text / code / data files
        if ext in SUPPORTED_TEXT_EXTENSIONS:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(50000)

        # PDF
        if ext == ".pdf":
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                text = "\n".join(page.get_text() for page in doc)
                doc.close()
                return text[:50000]
            except ImportError:
                return ""

        # DOCX
        if ext == ".docx":
            try:
                from docx import Document
                doc = Document(file_path)
                return "\n".join(p.text for p in doc.paragraphs)[:50000]
            except ImportError:
                return ""

    except Exception:
        return ""

    return ""


def summarize_document(file_path: str) -> dict:
    """
    Summarize a document locally.
    Uses extractive summarization (first N sentences) as a fallback
    when no local LLM is available.
    """
    ext = Path(file_path).suffix.lower()
    text = extract_text(file_path, ext)

    if not text.strip():
        return {
            "status": "error",
            "message": "Could not extract text from this file.",
            "summary": None,
            "processed_locally": True
        }

    # Extractive summarization: first 5 sentences
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if len(s.strip()) > 30]
    summary = ". ".join(sentences[:5]) + "." if sentences else text[:500]

    word_count = len(text.split())
    keywords = extract_keywords(text)

    return {
        "status": "success",
        "file": file_path,
        "summary": summary,
        "word_count": word_count,
        "keywords": keywords,
        "processed_locally": True,
        "method": "Extractive (local, no AI model required)"
    }


def extract_keywords(text: str, top_n: int = 10) -> list:
    """Simple frequency-based keyword extraction — fully offline."""
    import re
    from collections import Counter

    STOPWORDS = {
        "the","a","an","and","or","but","in","on","at","to","for","of","with",
        "is","was","are","were","be","been","being","have","has","had","do",
        "does","did","will","would","could","should","may","might","shall",
        "this","that","these","those","it","its","they","them","their","we",
        "our","us","you","your","i","my","me","he","she","his","her","from",
        "by","as","if","so","then","also","but","not","no","any","all","more",
        "than","when","which","who","what","how","where","there","here","can"
    }

    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    filtered = [w for w in words if w not in STOPWORDS]
    counter = Counter(filtered)
    return [word for word, _ in counter.most_common(top_n)]
