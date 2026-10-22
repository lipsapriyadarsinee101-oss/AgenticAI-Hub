# Agentic AI learning path

## 1. Fundamentals
Run demo mode. Inspect result.json and events.jsonl. Identify the goal, tools,
state, output, and stopping condition. Explain why deterministic retrieval is not an AI agent.

## 2. Tool calling and ReAct
Read tools.py and adapters.langchain_research. Run graph mode with a tool-capable model.
Ask a question that requires local evidence, then a calculation. Compare the final answers.
The model decides whether to call a tool; verify actual behavior in your local debugging setup.

## 3. LangGraph
Read workflow.State and the graph builder. Draw the state transitions.
Add a quality gate with a bounded retry counter before END. Preserve failure artifacts.
The current graph is linear and does not include persistent checkpoints or a retry loop.

## 4. CrewAI
Run crew mode. Compare the analyst task and editor task.
Change only one agent goal and evaluate whether citations survive the edit.

## 5. Agentic RAG with LlamaIndex
Add two Markdown documents that disagree. Run rag mode.
Inspect whether the output names the disagreement and sources.
The ReAct agent can choose the query-engine tool; the tool performs vector retrieval.

## 6. Hugging Face smolagents
Run smol mode. Verify a draft against local evidence.
This project uses ToolCallingAgent; code execution is deliberately not available.

## 7. Langflow
Build and test the visual flow in LANGFLOW.md. Save an export after removing secrets.
Compare its response with a direct CLI report.

## 8. Langfuse
Enable --trace and inspect stage latency and errors. Our spans are stage-level;
automatic token accounting and framework-native instrumentation are extension work.

## 9. Production engineering
Read OPERATIONS.md. Add a persistent index, a durable job queue, authentication,
request quotas, a model budget, and evidence-based evaluations before deploying publicly.

## 10. Real-world exercises
- Support copilot: replace sample documents with approved support articles.
- Policy analyst: compare two policy versions and cite changes.
- Engineering triage: retrieve engineering documentation and draft a human-reviewed plan.

Evaluate answer support and uncertainty, not just whether the workflow completed.

