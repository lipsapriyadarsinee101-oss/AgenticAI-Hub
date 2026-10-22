FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY agentic_hub ./agentic_hub
RUN pip install --no-cache-dir . && useradd --create-home agent && mkdir runs && chown agent:agent runs
USER agent
ENTRYPOINT ["agentic-hub"]
CMD ["Explain AI agent tools"]

