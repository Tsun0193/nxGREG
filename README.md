# CTC Knowledge Graph Tooling

Transform Markdown documentation into a navigable Neo4j knowledge graph enriched with context-aware provenance. This project parses project documentation, extracts structured entities, and can optionally use an LLM to generate Cypher statements for Mermaid diagrams.

## Table of Contents
- [Core Capabilities](#core-capabilities)
- [Architecture](#architecture)
- [Project Layout](#project-layout)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Setup](#setup)
- [Usage](#usage)
  - [Resetting and Rebuilding the Graph](#resetting-and-rebuilding-the-graph)
  - [Understanding the Outputs](#understanding-the-outputs)
- [Prompting Strategy](#prompting-strategy)
- [Developing](#developing)
  - [Running Static Checks](#running-static-checks)
  - [Testing Changes](#testing-changes)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Core Capabilities
- **Rule-Based Parsing** – Regex-driven extraction of tables, Mermaid diagrams, and narrative sections into graph nodes and relationships.
- **LLM Augmentation** – Builds prompts that combine Mermaid diagrams with their parent section hierarchy to request descriptive Cypher statements (no generic `FLOW_TO` edges).
- **Source Provenance** – Automatically emits `FROM_TABLE`, `FROM_GRAPH`, and `FROM_CHUNK` relationships so every generated entity can be traced back to the originating markdown content.
- **Neo4j Loader** – Applies idempotent Cypher to create/update nodes, enforce unique `uid`s, and persist relationships in Neo4j.

## Architecture
```
├── data            # Input resolution helpers (README selection)
├── parsing         # Markdown → GraphData parser with provenance annotations
├── pipelines       # Rule-based and LLM-driven ETL flows
├── prompts         # Prompt templates (Mermaid → Cypher & summaries)
├── loading         # Neo4j loader and constraint management
├── clients         # External service clients (OpenAI-compatible LLM)
├── utils           # Progress reporting utilities
├── core            # Graph container data structures
└── reset.py        # Entry point for wiping & rebuilding the graph
```

### Data Flow
1. **Read Source** – Determine the markdown document (default `ctc-data-translated/readme-en.md`).
2. **Parse** – `KnowledgeGraphParser` extracts entities, relationships, and provenance sources.
3. **(Optional) LLM** – `run_llm_pipeline` composes prompts and queries the LLM for Cypher blocks.
4. **Persist** – `Neo4jLoader` truncates or merges graph elements into the target Neo4j instance.

## Project Layout
| Path | Description |
| --- | --- |
| `core/graph.py` | `GraphData`, `GraphNode`, and `GraphRelationship` containers. |
| `parsing/parser.py` | Main Markdown parser with provenance (`FROM_*`) edges. |
| `pipelines/rule_based.py` | Rule-driven pipeline for deterministic parsing and optional loading. |
| `pipelines/llm.py` | Hybrid pipeline (rule-based + LLM prompt orchestration). |
| `prompts/templates.py` | Mermaid → Cypher and summary prompt builders. |
| `loading/loader.py` | Neo4j driver wrapper for applying graph updates. |
| `reset.py` | CLI that wipes the graph and optionally rebuilds via selected pipeline. |

## Getting Started

### Prerequisites
- Python ≥ 3.12
- Neo4j database (local or remote) reachable with Bolt protocol
- Optional: [uv](https://github.com/astral-sh/uv) or `pip` for dependency management

### Environment Variables
| Variable | Description |
| --- | --- |
| `NEO4J_URL` | Neo4j Bolt URI (e.g., `bolt://localhost:7687`). |
| `NEO4J_USERNAME` | Neo4j username. |
| `NEO4J_PASSWORD` | Neo4j password. |
| `CTC_README_PATH` *(optional)* | Override the default README path. |
| `NXCHAT_API` & `NXCHAT_API_KEY` *(optional)* | Required when using the LLM pipeline. |

### Setup
Install dependencies:

```bash
# With uv (preferred)
uv sync

# Or with pip
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt  # or use pyproject/uv.lock
```

## Usage

### Resetting and Rebuilding the Graph
`reset.py` wipes the Neo4j database (subject to the configured connection) and optionally rebuilds it from documentation.

```bash
python reset.py --rebuild \
  --method rule \
  --readme path/to/document.md
```

Options:
- `--rebuild` – After wiping, run the selected pipeline to repopulate the graph.
- `--method {rule,llm}` – Choose between the deterministic parser and the hybrid LLM pipeline (default: `rule`).
- `--readme` – Explicit path to the Markdown source (falls back to `CTC_README_PATH` or the default).

### Understanding the Outputs
- **Nodes** carry canonical labels (`Entity`, `FormField`, `ErrorNode`, etc.) and a generated `uid`.
- **Provenance** nodes live under the `Source` label, with subtype labels (`GraphSource`, `TableSource`, `ChunkSource`).
- **Relationships** include:
  - Domain semantics (`HAS_FIELD`, `ENTITY_RELATION`, `ERROR_FLOW`, ...).
  - Provenance edges (`FROM_TABLE`, `FROM_GRAPH`, `FROM_CHUNK`) pointing from each source to derived nodes.

Use these edges to retrieve original documentation fragments or regenerate context for downstream LLM calls.

## Prompting Strategy
When Mermaid diagrams are present, `pipelines/llm.py` builds prompts like:
- Section hierarchy > Diagram (to avoid ambiguous flow names).
- Explicit instructions to avoid generic `FLOW_TO` relationships.
- Request for Cypher blocks enclosed in triple backticks for easy execution.

When no diagrams are found, the pipeline falls back to the summary template to produce structured Markdown highlights.

## Developing

### Running Static Checks
```bash
python -m compileall clients core data loading parsing pipelines prompts utils
```
Tailor with `ruff`, `mypy`, or your preferred tooling as needed.

### Testing Changes
- **Neo4j integration** – Point to a disposable database before running `reset.py --rebuild`.
- **Parser validation** – Add small Markdown fixtures and inspect the resulting `GraphData` before loading.
- **LLM dry runs** – Stub `clients/llm_client.py::generate_response` when you do not have API credentials.

## Troubleshooting
| Symptom | Resolution |
| --- | --- |
| `RuntimeError: NXCHAT_API ... must be set` | Export `NXCHAT_API` & `NXCHAT_API_KEY` or use `--method rule`. |
| `README file not found` | Supply `--readme` or set `CTC_README_PATH`. |
| `neo4j Python driver is not installed` | `pip install neo4j`. |
| Missing provenance edges | Ensure parser sections include Markdown headings/tables/diagrams; provenance is inferred from structure. |

## Contributing
1. Fork/clone the repository.
2. Create a feature branch.
3. Run static checks and ensure `reset.py --rebuild` passes against a test database.
4. Submit a pull request with clear context and screenshots/queries if applicable.

## License
This project currently has no declared license. Add one to clarify reuse permissions.
