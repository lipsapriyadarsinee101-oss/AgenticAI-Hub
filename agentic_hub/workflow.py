"""Research workflow and durable per-run artifacts."""

import json
from pathlib import Path
from typing import TypedDict
from uuid import uuid4

from . import adapters
from .observability import Recorder
from .tools import DEFAULT_KNOWLEDGE, search_knowledge


class State(TypedDict, total=False):
    question: str
    evidence: str
    report: str
    review: str
    langflow: str


def validate_question(question: str) -> str:
    question = question.strip()
    if not question or len(question) > 4000:
        raise ValueError("Question must contain 1 to 4000 characters")
    return question


def quality_check(report: str, knowledge: Path) -> dict:
    import re
    known = {p.name for p in knowledge.glob("*.md") if not p.is_symlink()}
    citations = set(re.findall(r"\[([^\[\]\n]+\.md)\]", report))
    return {"has_local_citation": bool(citations & known),
            "unknown_citations": sorted(citations - known),
            "report_nonempty": bool(report.strip()),
            "note": "Structural checks only; factual correctness requires human review."}


def run(question: str, mode: str = "demo", knowledge: Path = DEFAULT_KNOWLEDGE,
        output: Path = Path("runs"), trace: bool = False, with_langflow: bool = False) -> Path:
    question = validate_question(question)
    if mode not in {"demo", "graph", "rag", "crew", "smol", "langflow", "all"}:
        raise ValueError("Unknown mode")
    knowledge = knowledge.resolve()
    if not knowledge.is_dir():
        raise ValueError("Knowledge directory does not exist")
    if with_langflow and mode != "all":
        raise ValueError("--with-langflow is only supported with --mode all")
    run_dir = output / uuid4().hex
    run_dir.mkdir(parents=True)
    state: State = {"question": question}
    recorder = Recorder(run_dir / "events.jsonl", trace)

    def retrieve(s):
        with recorder.stage("retrieve"):
            return {"evidence": search_knowledge(s["question"], knowledge)}

    def rag(s):
        with recorder.stage("llamaindex-agentic-rag"):
            return {"evidence": adapters.llama_rag(s["question"], knowledge)}

    def research(s):
        with recorder.stage("langchain-tool-calling"):
            return {"report": adapters.langchain_research(s["question"], knowledge, s.get("evidence", ""))}

    def crew(s):
        with recorder.stage("crewai-analysis-and-editing"):
            return {"report": adapters.crew_review(s["question"], s.get("report") or s["evidence"])}

    def smol(s):
        with recorder.stage("smolagents-source-review"):
            return {"report": adapters.smol_review(s["question"], s.get("report") or s["evidence"], knowledge)}

    try:
        with recorder.stage("workflow"):
            if mode == "demo":
                state.update(retrieve(state))
                with recorder.stage("deterministic-demo-report"):
                    state["report"] = (f"# Research brief: {question}\n\n"
                        "**Offline demonstration — no AI model or live framework was called.**\n\n"
                        f"## Retrieved evidence\n\n{state['evidence']}\n\n"
                        "## Next steps\n\nValidate the evidence with a human, then run a live mode "
                        "to generate an AI-written analysis. No current web research was performed.\n")
            elif mode in {"graph", "all"}:
                from langgraph.graph import END, START, StateGraph
                graph = StateGraph(State)
                graph.add_node("retrieve", rag if mode == "all" else retrieve)
                graph.add_node("research", research)
                graph.add_edge(START, "retrieve")
                graph.add_edge("retrieve", "research")
                if mode == "all":
                    graph.add_node("crew", crew)
                    graph.add_node("smol", smol)
                    graph.add_edge("research", "crew")
                    graph.add_edge("crew", "smol")
                    graph.add_edge("smol", END)
                else:
                    graph.add_edge("research", END)
                state = graph.compile().invoke(state, config={"recursion_limit": 12})
                if with_langflow:
                    with recorder.stage("langflow"):
                        state["langflow"] = adapters.langflow_run(state["report"])
            elif mode == "langflow":
                with recorder.stage("langflow"):
                    state["langflow"] = adapters.langflow_run(question)
                    state["report"] = "# Langflow response\n\nSee langflow.json for the full flow response."
            else:
                state.update(retrieve(state))
                if mode == "rag":
                    state["report"] = rag(state)["evidence"]
                elif mode == "crew":
                    state.update(crew(state))
                else:
                    state.update(smol(state))
            checks = quality_check(state["report"], knowledge)
            (run_dir / "report.md").write_text(state["report"], encoding="utf-8")
            if "langflow" in state:
                (run_dir / "langflow.json").write_text(state["langflow"], encoding="utf-8")
            (run_dir / "result.json").write_text(json.dumps({"mode": mode, "state": state,
                "checks": checks, "status": "completed"}, indent=2, ensure_ascii=False), encoding="utf-8")
    except BaseException as exc:
        (run_dir / "failure.json").write_text(json.dumps({"status": "failed", "mode": mode,
            "error_type": type(exc).__name__}), encoding="utf-8")
        raise
    finally:
        recorder.close()
    return run_dir
