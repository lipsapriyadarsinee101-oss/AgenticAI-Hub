# AgenticAI-Hub

A local-first research assistant and hands-on agentic AI learning project.

Ask a question, retrieve local evidence, generate a brief, review it with specialist agents,
and save a report with execution logs. Start offline, then enable the frameworks individually.

**Status:** runnable starter project. Offline behavior is tested. Live integrations require
optional packages, Ollama models, and service configuration; they have not been verified
against running models or external services in this build. This is not a hardened public service.

## Quick start (no API key)

Python 3.11–3.13:

```powershell
git clone https://github.com/lipsapriyadarsinee101-oss/AgenticAI-Hub.git
cd AgenticAI-Hub
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
agentic-hub "How do AI agents use tools?"
```

On macOS/Linux, activate with `source .venv/bin/activate`.
Without installation, run `python -m agentic_hub.cli "How do AI agents use tools?"`
from this directory.

Each run writes `runs/<unique-id>/report.md`, `result.json`, and `events.jsonl`.
The demo uses deterministic keyword retrieval. It **does not call an LLM or simulate successful
framework execution**.

## Framework map

| Topic | Implementation | Command mode |
|---|---|---|
| Agent fundamentals | Goals, tools, state, stopping limits; learning guide | demo |
| LangChain + ReAct/tool calling | Model/tool/observation loop using create_agent | graph |
| LangGraph | Typed state and explicit retrieval/research nodes | graph, all |
| CrewAI | Evidence analyst and research editor, sequential tasks | crew, all |
| LlamaIndex agentic RAG | Ollama embeddings, vector index, query tool, ReActAgent | rag, all |
| Hugging Face smolagents | ToolCallingAgent with a local evidence lookup tool | smol, all |
| Langflow visual development | Build a visual flow; call it through its real REST API | langflow |
| Langfuse observability | Optional stage observations, local timings always available | --trace |
| Production workflow basics | Bounded tools, failures, logs, tests, container and CI | all modes |

The live LangChain loop lets the model choose tools; it does not expose private reasoning.
CrewAI agents receive evidence from earlier stages. They are roles with separate tasks,
not autonomous processes with unrestricted access.

## Local AI setup

Install [Ollama](https://ollama.com), start its service, and download a tool-capable model
and an embedding model. Defaults below are configurable; model suitability and hardware vary.

```powershell
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
$env:OLLAMA_HOST = "http://localhost:11434"
$env:OLLAMA_MODEL = "qwen2.5:7b"
$env:OLLAMA_EMBED_MODEL = "nomic-embed-text"
```

Install only the extras you need:

```powershell
python -m pip install -e ".[graph]"
agentic-hub "Compare agent frameworks" --mode graph

python -m pip install -e ".[rag]"
agentic-hub "What safeguards should agents use?" --mode rag

python -m pip install -e ".[crew]"
agentic-hub "Plan a support assistant" --mode crew

python -m pip install -e ".[smol]"
agentic-hub "Verify agent framework capabilities" --mode smol
```

To combine the frameworks:

```powershell
python -m pip install -e ".[graph,rag,crew,smol,tracing]"
agentic-hub "Compare frameworks for a document research assistant" --mode all
```

All mode uses **LangGraph → LlamaIndex RAG → LangChain research → CrewAI editing →
smolagents review**. Add `--with-langflow` after creating a Langflow flow.
Add `--trace` after configuring Langfuse to include both remaining tools.

The dependency ranges are compatibility targets, not a resolved lockfile. Create and commit
a lockfile after validating your chosen environment. If frameworks have conflicting requirements,
run their modes in separate virtual environments. Langflow should run in its own environment.

## Your documents

Place UTF-8 Markdown files in a directory and pass `--knowledge ./my-docs`.
Search reads at most 100 top-level .md files, each no larger than 200 KB; symlinks are skipped.
There is no web search, arbitrary URL fetch, shell tool, or automatic PDF ingestion.
The included knowledge files are introductory samples, not an authoritative research corpus.
Live RAG builds an in-memory index each run; production use should persist and version it.

## Langflow and Langfuse

See [Langflow visual setup](docs/LANGFLOW.md) and
[configuration and operations](docs/OPERATIONS.md).
`.env.example` documents settings. Export environment variables yourself; the app does not
automatically load a .env file.

```powershell
$env:LANGFUSE_PUBLIC_KEY = "your-public-key"
$env:LANGFUSE_SECRET_KEY = "your-secret-key"
$env:LANGFUSE_BASE_URL = "https://cloud.langfuse.com"
agentic-hub "Explain agent tools" --mode graph --trace
```

Our Langfuse spans contain stage names and timing rather than prompts or report content.
Local result files contain the question, evidence and output; protect them accordingly.

## Learn and extend

Follow [the learning path](docs/LEARNING_PATH.md).
The same workflow can become a support copilot, document comparison assistant, or engineering
triage tool by replacing the knowledge base and extending tools with explicit permissions.

## Tests

```powershell
python -m unittest discover -s tests -v
```

CI runs offline tests and builds a package on Python 3.11, 3.12, and 3.13.
Live modes require manual integration checks described in the operations guide.
Citation checks validate filename references only; they do not establish factual correctness.

## Container

```sh
docker build -t agenticai-hub .
docker run --rm -v agentic-runs:/app/runs agenticai-hub "Explain agent tools"
```

The container defaults to the dependency-free demo. Install optional extras in a derivative
image for live modes and configure access to your Ollama host.

## Official implementation references

- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangGraph graph API](https://reference.langchain.com/python/langgraph/graph)
- [CrewAI quickstart](https://docs.crewai.com/en/quickstart)
- [LlamaIndex ReAct with query engines](https://developers.llamaindex.ai/python/examples/agent/react_agent_with_query_engine/)
- [smolagents](https://huggingface.co/docs/smolagents/index)
- [Langflow run API](https://docs.langflow.org/api-flows-run)
- [Langfuse instrumentation](https://langfuse.com/docs/observability/sdk/instrumentation)

