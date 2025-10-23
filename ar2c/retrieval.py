"""Document retrieval for AR²C."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .knowledge_base import Document, KnowledgeBase
from .utils import bm25_score, term_frequencies, tokenize, document_frequency


@dataclass
class RankedDocument:
    document: Document
    score: float

    def to_dict(self) -> dict:
        result = self.document.to_dict()
        result["score"] = self.score
        return result


class BM25Retriever:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self._doc_tokens = kb.tokenised_documents()
        self._doc_tfs = [term_frequencies(tokens) for tokens in self._doc_tokens]
        self._df = document_frequency(self._doc_tokens)
        self._avg_len = sum(len(tokens) for tokens in self._doc_tokens) / max(len(self._doc_tokens), 1)

    def rank(self, query: str, *, top_k: int = 3) -> List[RankedDocument]:
        query_tokens = tokenize(query)
        results: List[RankedDocument] = []
        total_docs = len(self._doc_tokens)
        for doc, tokens, tf in zip(self.kb, self._doc_tokens, self._doc_tfs):
            if not tokens:
                continue
            score = bm25_score(
                query_tokens,
                tf,
                df=self._df,
                avg_doc_len=self._avg_len,
                doc_len=len(tokens),
                total_docs=total_docs,
            )
            if score > 0:
                results.append(RankedDocument(document=doc, score=score))
        results.sort(key=lambda item: item.score, reverse=True)
        return results[:top_k]
