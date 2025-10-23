# Agentic RAG Risk Copilot (AR²C) Architecture

## Objectives
- Provide an entirely offline, open-source demo of an agentic retrieval-augmented generation (RAG) copilot focused on risk analysis.
- Use only redistributable, self-authored knowledge base entries stored locally in the repository.
- Avoid dependencies on closed models or hosted APIs while keeping the code portable and easy to run.

## High-Level Flow
1. **Query Understanding**  
   Lightweight rule-based classification extracts the risk domain and urgency from the question. This provides context for retrieval and later recommendations.
2. **Document Retrieval**  
   A pure-Python BM25-inspired scorer ranks the local knowledge base documents. No external embeddings or third-party services are required.
3. **Agentic Reasoning**  
   The agent combines query insights with retrieved evidence to produce structured analysis: situation summary, key risks, mitigations, and provenance.
4. **Reporting**  
   The CLI demo prints a compact report and exposes the referenced knowledge base entries for transparency.

## Directory Layout
- `ar2c/` – Python package with the core logic.
  - `agent.py` – Orchestrates the agentic pipeline.
  - `retrieval.py` – Implements BM25-style scoring over the local documents.
  - `knowledge_base.py` – Loads and validates the curated knowledge base.
  - `rules.py` – Contains domain/risk heuristics used during query understanding.
  - `utils.py` – Shared helpers (tokenisation, scoring utilities, formatting).
- `data/knowledge_base.json` – Open, self-authored risk governance entries.
- `cli.py` – End-user entry point for the offline demo.
- `docs/` – Architectural notes (this document).

## Technology Choices
- **Python Standard Library** only. This avoids package installation and maintains full offline capability.
- **JSON knowledge base** for human readability and easy extension.
- **Heuristic agent** instead of a heavy local LLM to keep the demo lightweight while still showing agentic, multi-step reasoning.

## Extensibility
- Additional documents can be appended to the JSON file; a basic schema check ensures required fields are present.
- Richer retrieval or scoring can be swapped in by implementing the `RankerProtocol` defined in `retrieval.py`.
- The agent provides clearly separated stages so a future contributor can replace heuristics with local LLM calls if desired (still offline if weights are shipped).

## Streamlit Demo (Planned)
- Single-page layout with a text input for the risk question, severity/domain insights, and recommended actions rendered as cards.
- A results sidebar lists retrieved knowledge base entries with expandable details so users can inspect provenance.
- Uses Streamlit caching to keep the knowledge base and agent instance warm between interactions.
