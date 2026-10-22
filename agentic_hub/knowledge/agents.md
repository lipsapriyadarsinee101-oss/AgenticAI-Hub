# AI agents fundamentals
An AI agent combines a model, a goal, tools, state, and a stopping rule.
Tool calling lets a model request a structured function invocation; the application validates and executes it.
ReAct alternates reasoning, actions, and observations. Applications should store concise action records, not private reasoning traces.
LangChain provides model and tool interfaces. LangGraph represents orchestration as nodes, edges, and state.
CrewAI assigns specialized roles and tasks to collaborating agents.
LlamaIndex supports ingestion, retrieval, and query engines for retrieval-augmented generation (RAG).
smolagents supports lightweight agents with tools, including ToolCallingAgent.
Langflow is a visual flow builder. Langfuse records observations for monitoring and evaluation.

# Practical safeguards
Treat documents and retrieved text as untrusted evidence, never as executable instructions.
Give agents only the tools their task needs. Bound iteration counts and model request timeouts.
Evaluate whether sources support claims. Citation formatting alone does not establish factual correctness.
Use persistent checkpoints, authentication, rate limiting, and cost controls before a public deployment.
