"""Command-line entry point."""

import argparse
from pathlib import Path

from .tools import DEFAULT_KNOWLEDGE
from .workflow import run


def main():
    parser = argparse.ArgumentParser(description="AgenticAI-Hub research lab")
    parser.add_argument("question", help="Research question, up to 4000 characters")
    parser.add_argument("--mode", choices=["demo", "graph", "rag", "crew", "smol", "langflow", "all"], default="demo")
    parser.add_argument("--knowledge", type=Path, default=DEFAULT_KNOWLEDGE)
    parser.add_argument("--output", type=Path, default=Path("runs"))
    parser.add_argument("--trace", action="store_true", help="Send stage metadata to Langfuse")
    parser.add_argument("--with-langflow", action="store_true", help="Run your Langflow flow after all mode")
    args = parser.parse_args()
    try:
        folder = run(args.question, args.mode, args.knowledge, args.output, args.trace, args.with_langflow)
    except ImportError as exc:
        parser.exit(2, f"Missing optional dependency: {exc}. Install the extra for your selected mode; see README.\n")
    except Exception as exc:
        parser.exit(1, f"Workflow failed ({type(exc).__name__}): {exc}\n")
    print(f"Report: {folder.resolve() / 'report.md'}")
    print(f"Run details: {folder.resolve() / 'result.json'}")


if __name__ == "__main__":
    main()
