# Visual development with Langflow

Langflow is an external visual editor, not embedded into the CLI.
This repository includes an API client and a reproducible build recipe, not an unverified
flow export. You must build and save the flow before the client can run it.

1. Install Langflow using its [official instructions](https://docs.langflow.org/get-started-installation).
   Keep it in a separate environment to avoid dependency conflicts.
2. Create a flow from the Basic Prompting template.
3. Configure a supported model provider. For local models, use an Ollama model component
   and the same model tag as your Ollama installation.
4. Connect Chat Input to a Prompt with a question variable, the Prompt to the model,
   and the model to Chat Output. Configure the prompt to preserve provided source filenames,
   identify unsupported claims, and return a research brief.
5. Test the flow in the Playground. Use a tiny evidence snippet with a filename citation.
6. Open API access, copy its flow ID and base URL, and create an API key if required.

PowerShell:

```powershell
$env:LANGFLOW_URL = "http://localhost:7860"
$env:LANGFLOW_FLOW_ID = "paste-your-flow-id"
$env:LANGFLOW_API_KEY = "paste-your-api-key"
agentic-hub "Explain tool calling" --mode langflow
```

The raw response is saved as langflow.json because output structures depend on your components.

To make the visual stage part of the combined pipeline:

```powershell
agentic-hub "Compare research assistant architectures" --mode all --with-langflow
```

The final report is passed to your flow for further processing. The pre-flow report remains
report.md; the flow's response is a separate artifact. Export the tested flow from Langflow
and version its JSON in your own repository after removing secrets.

