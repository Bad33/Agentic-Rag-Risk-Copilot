# Agentic RAG Risk Copilot (AR²C)

AR²C is a fully offline demo of an agentic retrieval-augmented copilot that helps analyse risk scenarios using only redistributable, self-authored knowledge. The project avoids any hosted APIs or non-open assets so it can run in disconnected environments.

## Features
- Pure-Python pipeline (no external packages required) that performs query profiling, document retrieval, and structured reasoning.
- Local knowledge base stored in `data/knowledge_base.json`, licensed under CC-BY-4.0 for reuse.
- Agentic reporting with severity assessment, recommended actions, and transparent provenance for every answer.
- Command-line interface supporting one-off queries and an interactive shell.

## Quick Start
1. Ensure Python 3.9+ is available.
2. From the repository root, run a query:
   ```bash
   python3 cli.py "How should we respond to a ransomware breach affecting backups?"
   ```
3. Launch the interactive prompt:
   ```bash
   python3 cli.py --interactive
   ```
4. Show the reasoning trace for any answer:
   ```bash
   python3 cli.py --trace "What controls address third-party data handling risk?"
   ```

## Streamlit Web App
- Install dependencies: `pip install -r requirements.txt`
- Launch locally: `streamlit run streamlit_app.py`
- Optional environment variable `AR2C_KB_PATH` can point to an alternate knowledge base JSON file.
- Detailed deployment notes (including Streamlit Community Cloud) live in `docs/streamlit_deployment.md`.

## Knowledge Base
- Location: `data/knowledge_base.json`
- Each entry contains an `id`, `title`, `summary`, `details`, `tags`, `source`, and `license`.
- Content is self-authored and released under CC-BY-4.0. You may replace or extend entries with any open-source material that respects redistribution requirements.

## Project Layout
- `ar2c/` – Core package (agent, retrieval, heuristics, utilities).
- `data/knowledge_base.json` – Offline knowledge base.
- `cli.py` – CLI entry point.
- `docs/architecture.md` – Architectural overview and design notes.

## Extending the Demo
- Add new documents by appending to the JSON file; the loader validates required fields.
- Replace the heuristic agent with your own module and call it from `AgenticRiskCopilot`.
- Swap the retriever by providing a custom class that exposes a `rank(query, top_k)` method.

## Licensing
- Code is distributed under the MIT License (see `LICENSE`).
- Knowledge base content is licensed under CC-BY-4.0 as noted in each entry.
