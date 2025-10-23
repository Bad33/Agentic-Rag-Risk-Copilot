"""
Utility helpers for the AR²C project.

This module intentionally stays dependency-free so the demo can run in
fully offline environments.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Sequence

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9']+")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "will",
    "with",
}


def normalize_text(text: str) -> str:
    return text.lower().strip()


def tokenize(text: str, *, remove_stopwords: bool = True) -> List[str]:
    tokens = [token.lower() for token in TOKEN_PATTERN.findall(text.lower())]
    if remove_stopwords:
        tokens = [tok for tok in tokens if tok not in STOPWORDS]
    return tokens


def term_frequencies(tokens: Sequence[str]) -> Counter:
    return Counter(tokens)


def document_frequency(
    documents: Iterable[Sequence[str]],
) -> Dict[str, int]:
    df: Dict[str, int] = defaultdict(int)
    for tokens in documents:
        for token in set(tokens):
            df[token] += 1
    return dict(df)


def bm25_score(
    query_tokens: Sequence[str],
    doc_tf: Counter,
    *,
    df: Dict[str, int],
    avg_doc_len: float,
    doc_len: int,
    total_docs: int,
    k1: float = 1.5,
    b: float = 0.75,
) -> float:
    score = 0.0
    for token in query_tokens:
        if token not in doc_tf:
            continue
        idf = math.log(1 + (total_docs - df.get(token, 0) + 0.5) / (df.get(token, 0) + 0.5))
        tf = doc_tf[token]
        denom = tf + k1 * (1 - b + b * doc_len / (avg_doc_len or 1.0))
        score += idf * (tf * (k1 + 1) / denom)
    return score


def unique_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def chunk_text(text: str, *, limit: int = 600) -> List[str]:
    """Split long text into approximate chunks without external libs."""
    words = text.split()
    chunks: List[str] = []
    current: List[str] = []
    for word in words:
        current.append(word)
        if len(current) >= limit:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks
