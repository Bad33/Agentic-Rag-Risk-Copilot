"""Core agent logic for the Agentic RAG Risk Copilot."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .knowledge_base import KnowledgeBase
from .retrieval import BM25Retriever, RankedDocument
from .rules import profile_query, recommended_actions


@dataclass
class AgentOutput:
    query: str
    severity: str
    domains: List[str]
    keywords: List[str]
    retrieved: List[RankedDocument]
    risk_summary: str
    actions: List[str]
    reasoning_trace: List[str]
    report: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "query": self.query,
            "severity": self.severity,
            "domains": list(self.domains),
            "keywords": list(self.keywords),
            "risk_summary": self.risk_summary,
            "actions": list(self.actions),
            "reasoning_trace": list(self.reasoning_trace),
            "retrieved": [item.to_dict() for item in self.retrieved],
            "report": self.report,
        }


class AgenticRiskCopilot:
    def __init__(self, kb: KnowledgeBase, retriever: Optional[BM25Retriever] = None):
        self.kb = kb
        self.retriever = retriever or BM25Retriever(kb)

    def analyse(self, query: str, *, top_k: int = 3) -> AgentOutput:
        trace: List[str] = []
        profile = profile_query(query)
        trace.append(
            f"Profiled query -> domains: {profile.domain_candidates}, severity: {profile.severity}, keywords: {profile.keywords}"
        )

        ranked = self.retriever.rank(query, top_k=top_k)
        if ranked:
            trace.append(f"Retriever returned {len(ranked)} documents with BM25 > 0.")
        else:
            trace.append("Retriever returned no documents with positive BM25 score.")

        risk_summary = self._compose_risk_summary(profile.severity, profile.domain_candidates, ranked)
        trace.append(f"Composed risk summary based on heuristics and {len(ranked)} retrieved docs.")

        doc_ids = [item.document.id for item in ranked]
        actions = recommended_actions(profile.domain_candidates, doc_ids)
        trace.append(f"Generated {len(actions)} recommended actions.")

        report = self._render_report(query, risk_summary, actions, ranked, profile)
        trace.append("Assembled final structured report.")

        return AgentOutput(
            query=query,
            severity=profile.severity,
            domains=profile.domain_candidates,
            keywords=profile.keywords,
            retrieved=ranked,
            risk_summary=risk_summary,
            actions=actions,
            reasoning_trace=trace,
            report=report,
        )

    def _compose_risk_summary(
        self, severity: str, domains: List[str], ranked_docs: List[RankedDocument]
    ) -> str:
        if not domains:
            domains = ["governance"]
        primary_domain = domains[0]
        doc_highlights = []
        for item in ranked_docs:
            doc = item.document
            doc_highlights.append(f"{doc.title}: {doc.summary}")
        if doc_highlights:
            highlight_text = " ".join(doc_highlights)
        else:
            highlight_text = (
                "No specific knowledge base entries matched, so apply baseline governance and control checks."
            )
        return (
            f"The query reflects a {severity.upper()} priority {primary_domain} risk scenario. "
            f"Focus areas: {highlight_text}"
        )

    def _render_report(
        self,
        query: str,
        risk_summary: str,
        actions: List[str],
        ranked_docs: List[RankedDocument],
        profile,
    ) -> str:
        lines = [
            "=== Agentic RAG Risk Copilot Report ===",
            f"Query: {query}",
            "",
            f"Detected domains: {', '.join(profile.domain_candidates)}",
            f"Estimated severity: {profile.severity}",
            f"Key terms: {', '.join(profile.keywords) if profile.keywords else 'n/a'}",
            "",
            "Risk Summary:",
            f"  {risk_summary}",
            "",
            "Recommended Actions:",
        ]
        if actions:
            for action in actions:
                lines.append(f"  - {action}")
        else:
            lines.append("  - No specific actions generated.")

        lines.append("")
        lines.append("Supporting Knowledge Base Entries:")
        if ranked_docs:
            for item in ranked_docs:
                doc = item.document
                lines.append(f"  - {doc.title} (score={item.score:.2f}, id={doc.id})")
        else:
            lines.append("  - None")
        return "\n".join(lines)
