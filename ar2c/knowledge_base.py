"""Local knowledge base loader for AR²C."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .utils import tokenize


@dataclass
class Document:
    id: str
    title: str
    summary: str
    details: str
    tags: List[str]
    source: str
    license: str

    @property
    def full_text(self) -> str:
        return "\n".join([self.title, self.summary, self.details, ", ".join(self.tags)])

    def to_dict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "details": self.details,
            "tags": list(self.tags),
            "source": self.source,
            "license": self.license,
        }


class KnowledgeBase:
    def __init__(self, documents: Iterable[Document]):
        self._documents: List[Document] = list(documents)
        if not self._documents:
            raise ValueError("Knowledge base must contain at least one document.")
        self._index_by_id: Dict[str, Document] = {doc.id: doc for doc in self._documents}
        if len(self._index_by_id) != len(self._documents):
            raise ValueError("Duplicate document IDs detected in knowledge base.")

    def __iter__(self):
        return iter(self._documents)

    def __len__(self) -> int:
        return len(self._documents)

    def get(self, doc_id: str) -> Optional[Document]:
        return self._index_by_id.get(doc_id)

    @staticmethod
    def from_file(path: str | Path) -> "KnowledgeBase":
        with Path(path).open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        documents = []
        for entry in payload:
            KnowledgeBase._validate_entry(entry)
            documents.append(
                Document(
                    id=entry["id"],
                    title=entry["title"],
                    summary=entry["summary"],
                    details=entry["details"],
                    tags=list(entry["tags"]),
                    source=entry["source"],
                    license=entry["license"],
                )
            )
        return KnowledgeBase(documents)

    @staticmethod
    def _validate_entry(entry: Dict[str, object]) -> None:
        required = {"id", "title", "summary", "details", "tags", "source", "license"}
        missing = required - entry.keys()
        if missing:
            raise ValueError(f"Knowledge base entry missing fields: {missing}")
        if not isinstance(entry["tags"], list):
            raise ValueError("Knowledge base entry 'tags' must be a list.")

    def tokenised_documents(self) -> List[List[str]]:
        return [tokenize(doc.full_text) for doc in self._documents]
