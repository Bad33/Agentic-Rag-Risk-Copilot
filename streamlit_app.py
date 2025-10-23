"""Streamlit interface for the Agentic RAG Risk Copilot demo."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import streamlit as st

from ar2c import AgenticRiskCopilot, KnowledgeBase


@st.cache_resource(show_spinner=False)
def load_agent(kb_path: Optional[str] = None) -> AgenticRiskCopilot:
    kb_env = os.environ.get("AR2C_KB_PATH")
    kb_path = kb_path or kb_env or str(default_kb_path())
    kb = KnowledgeBase.from_file(kb_path)
    return AgenticRiskCopilot(kb)


def default_kb_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "knowledge_base.json"


def render_sidebar(agent: AgenticRiskCopilot) -> None:
    st.sidebar.header("Knowledge Base")
    st.sidebar.write(f"{len(agent.kb)} entries available.")
    for doc in agent.kb:
        with st.sidebar.expander(doc.title):
            st.caption(f"ID: `{doc.id}` • License: {doc.license}")
            st.write(doc.summary)
            st.markdown("**Tags:** " + ", ".join(doc.tags))
            st.markdown("**Details**")
            st.write(doc.details)
            st.caption(doc.source)


def run_query(agent: AgenticRiskCopilot, query: str, *, top_k: int, show_trace: bool):
    with st.spinner("Analysing risk scenario..."):
        output = agent.analyse(query, top_k=top_k)
    st.subheader("Risk Summary")
    st.write(output.risk_summary)

    st.subheader("Recommended Actions")
    for action in output.actions:
        st.markdown(f"- {action}")

    st.subheader("Supporting Knowledge")
    if output.retrieved:
        for item in output.retrieved:
            doc = item.document
            with st.expander(f"{doc.title} (score {item.score:.2f})", expanded=False):
                st.caption(f"ID: `{doc.id}` • License: {doc.license}")
                st.write(doc.summary)
                st.markdown("**Details**")
                st.write(doc.details)
                st.markdown("**Tags:** " + ", ".join(doc.tags))
                st.caption(doc.source)
    else:
        st.info("No supporting documents returned by the retriever.")

    st.subheader("Signal Insights")
    cols = st.columns(3)
    cols[0].metric("Estimated Severity", output.severity.title())
    cols[1].metric("Detected Domains", ", ".join(output.domains) or "n/a")
    cols[2].metric("Key Terms", ", ".join(output.keywords) or "n/a")

    if show_trace:
        st.subheader("Reasoning Trace")
        for step in output.reasoning_trace:
            st.markdown(f"- {step}")


def main() -> None:
    st.set_page_config(
        page_title="Agentic RAG Risk Copilot (AR²C)",
        page_icon="🛡️",
        layout="wide",
    )
    st.title("Agentic RAG Risk Copilot (AR²C)")
    st.write(
        "Offline-friendly risk analysis powered by local, redistributable knowledge. "
        "Ask a question about cyber, privacy, or operational risk and receive structured guidance."
    )

    agent = load_agent()
    render_sidebar(agent)

    with st.form("risk_query"):
        query = st.text_area(
            "Risk Question",
            placeholder="Example: How should we respond to a ransomware breach affecting backups?",
            height=120,
        )
        top_k = st.slider("Knowledge base documents to reference", min_value=1, max_value=6, value=3)
        show_trace = st.checkbox("Show reasoning trace", value=False)
        submitted = st.form_submit_button("Analyse")

    if submitted:
        if not query.strip():
            st.warning("Please provide a risk-focused question to analyse.")
        else:
            run_query(agent, query.strip(), top_k=top_k, show_trace=show_trace)

    st.divider()
    st.caption(
        "Knowledge base entries are self-authored and distributed under CC-BY-4.0. "
        "Source code is available in this repository under the MIT License."
    )


if __name__ == "__main__":
    main()
