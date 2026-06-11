# Simple RAG Pipeline

> A beginner-friendly, hands-on RAG (Retrieval Augmented Generation) system you can clone, run, and modify in under 10 minutes.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![LanceDB](https://img.shields.io/badge/vector--db-LanceDB-orange)](https://lancedb.github.io/lancedb/)

![rag-image](./rag-design-basic.png)

## What This Project Is

This project teaches you how a RAG system works from the inside by giving you a clean, modular implementation you can read and run locally. It deliberately avoids heavy frameworks so every step — indexing, retrieval, re-ranking, generation, evaluation — is visible in plain Python.

**Good for:** learning RAG fundamentals, adapting components to your own data, using as a starter template.  
**Not for:** production deployments (see [Alternatives](#-alternatives) for that).

## What It Does

- **Index Documents** — process PDFs into semantic chunks using [Docling](https://github.com/DS4SD/docling)
- **Store & Retrieve** — embed chunks and run similarity search with [LanceDB](https://lancedb.github.io/lancedb/) (local, no server needed)
- **Re-rank** — improve retrieval precision using [Cohere's rerank-v3.5](https://cohere.com/rerank)
- **Generate Responses** — answer questions using OpenAI (swappable via `src/util/invoke_ai.py`)
- **Evaluate** — score response quality against expected answers with LLM-as-judge

## Architecture

```
main.py  ──►  RAGPipeline
                ├── Indexer         (Docling → chunks)
                ├── Datastore       (LanceDB embeddings)
                ├── Retriever       (search + Cohere rerank)
                ├── ResponseGenerator (OpenAI LLM)
                └── Evaluator       (LLM-as-judge scoring)
```

Each component implements an abstract interface (`src/interface/`), making it straightforward to swap any piece — e.g. replace OpenAI with Ollama, or LanceDB with Chroma.

## Quickstart

```bash
# 1. Clone and create a virtual environment
git clone https://github.com/pixegami/simple-rag-pipeline.git
cd simple-rag-pipeline
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API keys  (OpenAI + Cohere shown; see Installation for Anthropic/Ollama)
export OPENAI_API_KEY="sk-..."
export CO_API_KEY="..."          # Cohere — free tier works fine

# 4. Run the full pipeline (reset → index → evaluate)
python main.py run
```

That's it. The pipeline indexes the hotel PDF in `sample_data/source/` and evaluates with `sample_data/eval/sample_questions.json`.

**No OpenAI account?** Run fully locally with Ollama:

```bash
# After installing Ollama and pulling a model:
ollama pull llama3.2
export LLM_PROVIDER=ollama
export CO_API_KEY="..."
python main.py run
```

## Installation

### Prerequisites

- Python 3.10+
- A [Cohere API key](https://cohere.com/) (free tier works) for re-ranking
- An LLM provider — pick one:

| Provider | Env var needed | Free? |
|---|---|---|
| OpenAI (default) | `OPENAI_API_KEY` | No |
| Anthropic Claude | `ANTHROPIC_API_KEY` | No |
| Ollama (local) | none | Yes — [install Ollama](https://ollama.com) |

### Set Up

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

```bash
# Cohere (required for re-ranking)
export CO_API_KEY="your_cohere_api_key"

# LLM provider — choose one:
export LLM_PROVIDER=openai       # default
export OPENAI_API_KEY="sk-..."

# -- or --
export LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# -- or (no API key needed) --
export LLM_PROVIDER=ollama       # runs against http://localhost:11434
```

Optional overrides:

```bash
export OPENAI_MODEL=gpt-4o-mini        # default: o4-mini
export ANTHROPIC_MODEL=claude-haiku-4-5-20251001  # default: claude-sonnet-4-6
export OLLAMA_MODEL=mistral            # default: llama3.2
export OLLAMA_BASE_URL=http://localhost:11434      # default
```

For fish shell, replace `export X=Y` with `set -x X Y`.

## Usage

Default paths are set in `main.py`:

```python
DEFAULT_SOURCE_PATH = "sample_data/source/"
DEFAULT_EVAL_PATH = "sample_data/eval/sample_questions.json"
```

### Run the full pipeline

Reset the datastore, index documents, and evaluate all sample questions:

```bash
python main.py run
```

### Reset the database

```bash
python main.py reset
```

### Add documents

```bash
python main.py add -p "sample_data/source/"       # directory
python main.py add -p "path/to/my_doc.pdf"        # single file
```

### Query interactively

```bash
python main.py query "What is the opening year of The Lagoon Breeze Hotel?"
```

### Evaluate against a question set

```bash
python main.py evaluate -f "sample_data/eval/sample_questions.json"
```

The eval JSON format is:

```json
[
  { "question": "...", "answer": "..." }
]
```

## Project Structure

```
simple-rag-pipeline/
├── main.py                    # CLI entry point
├── create_parser.py           # Argument parser
├── requirements.txt
├── sample_data/
│   ├── source/                # Drop your PDFs here
│   └── eval/                  # JSON question/answer pairs
└── src/
    ├── rag_pipeline.py        # Pipeline orchestrator
    ├── impl/                  # Concrete implementations
    │   ├── datastore.py       # LanceDB vector store
    │   ├── indexer.py         # Docling PDF chunker
    │   ├── retriever.py       # Search + Cohere rerank
    │   ├── response_generator.py
    │   └── evaluator.py
    ├── interface/             # Abstract base classes
    └── util/
        ├── invoke_ai.py       # Swap your LLM here
        └── extract_xml.py
```

## Swapping Components

The abstract interfaces in `src/interface/` are designed to be replaced:

| Want to change? | How |
|---|---|
| LLM provider (OpenAI / Claude / Ollama) | Set `LLM_PROVIDER` env var — no code change needed |
| LLM model name | Set `OPENAI_MODEL` / `ANTHROPIC_MODEL` / `OLLAMA_MODEL` |
| Vector store (LanceDB → Chroma / Qdrant) | Edit `src/impl/datastore.py` |
| Document parser (Docling → Unstructured) | Edit `src/impl/indexer.py` |
| Re-ranker (Cohere → cross-encoder) | Edit `src/impl/retriever.py` |
| Evaluator logic | Edit `src/impl/evaluator.py` |

## 🚀 Roadmap & Future Releases

Planned improvements to help learners go deeper:

### ✅ v1.1 — Multi-LLM Support ([#1](https://github.com/sevasek/simple-rag-pipeline/issues/1))
~~Add a `LLM_PROVIDER` environment variable~~ — **Done.** Set `LLM_PROVIDER` to `openai` (default), `anthropic`, or `ollama` to switch LLM backends with no code changes. Ollama lets you run the full pipeline locally with no API key.

### v1.2 — Gradio / Streamlit Chat UI ([#2](https://github.com/sevasek/simple-rag-pipeline/issues/2))
A minimal web interface on top of the existing `process_query` method, so learners who aren't comfortable with the CLI can still experiment. No new pipeline code needed — just a thin UI wrapper with a chat history panel and a document upload button.

### v1.3 — Chunking Strategy Benchmark ([#3](https://github.com/sevasek/simple-rag-pipeline/issues/3))
A `python main.py benchmark` command that runs the same eval set using three chunking strategies (fixed-size 512 tokens, sentence-level, Docling hybrid) and prints a side-by-side accuracy table. Teaches learners the single biggest lever in RAG quality with zero configuration required.

## 🔗 Alternatives

If you need something more production-ready:

| Project | Best for |
|---|---|
| [LlamaIndex](https://www.llamaindex.ai/) | Full-featured RAG toolkit, 160+ data connectors |
| [LangChain](https://www.langchain.com/) | Agents + RAG, huge ecosystem |
| [Haystack](https://haystack.deepset.ai/) | Enterprise pipelines, strong evaluation tooling |
| [RAGFlow](https://github.com/infiniflow/ragflow) | Visual/low-code RAG workflow builder |
| [lancedb/vectordb-recipes](https://github.com/lancedb/vectordb-recipes) | More LanceDB RAG examples |

## Contributing

This project is primarily a learning resource. If you find a bug, an outdated dependency, or a better way to explain a concept, PRs are welcome. Keep changes minimal and beginner-readable — clarity over cleverness.

## License

MIT
