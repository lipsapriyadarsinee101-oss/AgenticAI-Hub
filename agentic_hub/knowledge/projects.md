# Real-world project ideas
Research briefs: retrieve evidence, compare approaches, and write a report with source references.
Support assistant: retrieve product documentation, draft answers, and escalate uncertain cases to people.
Document analyst: compare policy documents and flag contradictions with source locations.
Engineering triage: summarize an issue, retrieve related documentation, and propose a reviewed plan.

# This project's scope
AgenticAI-Hub implements a research brief workflow using a local Markdown knowledge base.
The demo is deterministic and does not use a language model, embeddings, web search, or live frameworks.
Live graph mode uses LangChain tool calling inside a LangGraph workflow.
All mode chains LlamaIndex retrieval, LangChain research, a CrewAI analyst/editor pair,
a smolagents review, and optionally a previously created Langflow flow.
