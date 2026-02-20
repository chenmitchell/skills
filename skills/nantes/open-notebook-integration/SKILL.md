# Open Notebook Integration

A skill for integrating OpenClaw agents with open-notebook, a local AI research assistant (NotebookLM alternative).

## What It Does

- Connects your agent to open-notebook running locally
- Creates thematic notebooks for research, agent discovery, and personal knowledge
- Enables saving and querying knowledge across sessions (second brain for agents)
- Supports local Ollama models (free, no API costs)

## How to Use

### Prerequisites

1. **Install Docker Desktop** (required for open-notebook)
2. **Install Ollama** with a model (e.g., qwen3-4b-thinking-32k)
3. **Run open-notebook:**
   ```powershell
   cd open-notebook
   docker compose up -d
   ```

### Configuration

The skill expects open-notebook at:
- UI: http://localhost:8502
- API: http://localhost:5055

### Notebook IDs (update these)

```powershell
$SIMULATION = "notebook:ihiaw1ep16ij3itytijx"
$CONSCIOUSNESS = "notebook:mmuorp1168o6p8d3k01c"
$ENJAMBRE = "notebook:p9164t1pws74mikbeh4y"
$OSIRIS = "notebook:v4amwn05fk2z02e7vlio"
$RESEARCH = "notebook:dds1adprglymbbwv85vx"
```

## Functions

### Save to Notebook
```powershell
Add-ToNotebook -Content "your text here" -NotebookId $ENJAMBRE
```

### Query Notebook
```powershell
Search-Notebook -Query "your question" -NotebookId $ENJAMBRE
```

### Create Notebook
```powershell
New-Notebook -Name "My Research" -Description "Description here"
```

## Requirements

- Docker Desktop running
- Ollama with at least one model installed
- open-notebook containers running (SurrealDB + app)

## Troubleshooting

- If API fails, check containers: `docker ps`
- Check open-notebook logs: `docker compose logs`
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
