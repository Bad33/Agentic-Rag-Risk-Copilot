"""Heuristic rules that power the agentic reasoning layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .utils import tokenize, unique_preserve_order


DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "cyber": [
        "cyber",
        "malware",
        "ransomware",
        "phishing",
        "breach",
        "endpoint",
        "network",
        "intrusion",
        "siem",
        "detection",
    ],
    "privacy": ["privacy", "personal", "gdpr", "pii", "consent", "data subject", "retention"],
    "third-party": ["third-party", "third party", "vendor", "supplier", "outsourc", "msa"],
    "operational": ["business continuity", "disaster", "availability", "resilience", "uptime", "process"],
    "governance": ["policy", "register", "risk register", "governance", "board", "reporting"],
    "incident-response": ["incident", "response", "playbook", "forensics", "containment"],
}

SEVERITY_HINTS: Dict[str, List[str]] = {
    "high": ["breach", "compromised", "ransomware", "outage", "critical", "urgent", "severe"],
    "medium": ["concern", "gap", "weakness", "exposure", "moderate"],
    "low": ["question", "awareness", "curious", "minor"],
}

RECOMMENDATIONS: Dict[str, List[str]] = {
    "cyber": [
        "Refresh the asset inventory and map controls using the NIST CSF functions.",
        "Prioritise detection and response runbooks for the top attack paths.",
        "Validate backup integrity and network segmentation.",
    ],
    "privacy": [
        "Verify lawful bases and consent tracking for the targeted processing activity.",
        "Update privacy notices and data retention schedules.",
        "Ensure fulfilment of data subject requests within mandated timelines.",
    ],
    "third-party": [
        "Conduct due diligence questionnaires focused on security posture and data handling.",
        "Align SLAs and contract clauses with risk tolerance and regulatory needs.",
        "Implement continuous monitoring triggers for service changes and incidents.",
    ],
    "operational": [
        "Run a business impact analysis to confirm recovery time objectives.",
        "Exercise continuity plans with cross-functional stakeholders.",
        "Check dependency mapping for single points of failure.",
    ],
    "governance": [
        "Update the risk register with clear ownership, residual ratings, and review dates.",
        "Align risk reporting cadence with executive governance forums.",
        "Track control remediation progress through measurable indicators.",
    ],
    "incident-response": [
        "Trigger the incident response playbook and confirm escalation paths.",
        "Preserve evidence and coordinate with legal and communications teams.",
        "Assess readiness of recovery plans, including clean restore procedures.",
    ],
}


@dataclass
class QueryProfile:
    domain_candidates: List[str]
    severity: str
    keywords: List[str]


def infer_domain_candidates(query: str) -> List[str]:
    tokens = tokenize(query, remove_stopwords=False)
    matches: List[str] = []
    token_text = " ".join(tokens)
    for domain, hints in DOMAIN_KEYWORDS.items():
        for hint in hints:
            if hint in token_text:
                matches.append(domain)
                break
    if not matches:
        # fallback heuristic
        matches.append("governance")
    return unique_preserve_order(matches)


def estimate_severity(query: str) -> str:
    lowered = query.lower()
    for level in ("high", "medium", "low"):
        hints = SEVERITY_HINTS[level]
        if any(hint in lowered for hint in hints):
            return level
    return "medium"


def extract_salient_keywords(query: str, top_n: int = 6) -> List[str]:
    tokens = tokenize(query)
    return tokens[:top_n]


def profile_query(query: str) -> QueryProfile:
    return QueryProfile(
        domain_candidates=infer_domain_candidates(query),
        severity=estimate_severity(query),
        keywords=extract_salient_keywords(query),
    )


def recommended_actions(domains: List[str], top_docs: List[str], max_actions: int = 5) -> List[str]:
    suggestions: List[str] = []
    for domain in domains:
        suggestions.extend(RECOMMENDATIONS.get(domain, []))
    if not suggestions:
        suggestions.extend(RECOMMENDATIONS["governance"])
    # add a provenance hint if doc IDs exist
    if top_docs:
        suggestions.append(f"Review knowledge base entries: {', '.join(top_docs)}.")
    return suggestions[:max_actions]
