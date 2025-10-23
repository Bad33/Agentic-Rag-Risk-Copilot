"""Command-line entry point for the Agentic RAG Risk Copilot demo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from ar2c import AgenticRiskCopilot, KnowledgeBase


def default_kb_path() -> Path:
    project_root = Path(__file__).resolve().parent
    return project_root / "data" / "knowledge_base.json"


def load_copilot(kb_path: Optional[Path] = None) -> AgenticRiskCopilot:
    kb_path = kb_path or default_kb_path()
    kb = KnowledgeBase.from_file(kb_path)
    return AgenticRiskCopilot(kb)


def run_query(agent: AgenticRiskCopilot, query: str, *, top_k: int, show_trace: bool = False) -> int:
    output = agent.analyse(query, top_k=top_k)
    print(output.report)
    if show_trace:
        print("\nReasoning Trace:")
        for step in output.reasoning_trace:
            print(f"  - {step}")
    return 0


def interactive_loop(agent: AgenticRiskCopilot, *, top_k: int, show_trace: bool = False) -> int:
    print("Agentic RAG Risk Copilot (offline demo)")
    print("Type 'exit' or 'quit' to leave.\n")
    while True:
        try:
            query = input("Question> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if query.lower() in {"exit", "quit"}:
            return 0
        if not query:
            continue
        run_query(agent, query, top_k=top_k, show_trace=show_trace)
        print()


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Agentic RAG Risk Copilot (offline demo)")
    parser.add_argument("query", nargs="*", help="Risk-focused question to analyse.")
    parser.add_argument("--kb", type=Path, help="Path to a JSON knowledge base file.")
    parser.add_argument("--top-k", type=int, default=3, help="Number of documents to retrieve (default: 3).")
    parser.add_argument("--trace", action="store_true", help="Print the agent reasoning trace.")
    parser.add_argument(
        "--interactive", action="store_true", help="Launch interactive prompt even if a query is provided."
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    try:
        agent = load_copilot(args.kb)
    except FileNotFoundError:
        print("Knowledge base file not found. Provide --kb pointing to a valid JSON file.", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to load knowledge base: {exc}", file=sys.stderr)
        return 1

    if args.interactive or not args.query:
        if args.query and not args.interactive:
            print("Ignoring positional query because --interactive was requested.")
        return interactive_loop(agent, top_k=args.top_k, show_trace=args.trace)

    query = " ".join(args.query)
    return run_query(agent, query, top_k=args.top_k, show_trace=args.trace)


if __name__ == "__main__":
    raise SystemExit(main())
