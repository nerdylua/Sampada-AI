# MumbaiHacks · Sampada AI

**Sampada AI** is a financial agentic copilot powered by the Model Context Protocol (MCP) and RAG tools. It combines real-time market intelligence, document understanding, and autonomous computer-use capabilities into a unified AI assistant for financial analysis and decision-making.

## Demo

[Watch on YouTube](https://youtu.be/dmaqJURPUNA)

## Key Features

- **Agentic Tool Use** — AI autonomously decides when to query documents, fetch market data, or generate reports
- **Structure-Aware RAG** — Table-aware chunking and cell-level reranking for accurate financial document Q&A
- **Real-Time Market Data** — Live stock charts, PE ratios, peer comparisons, quarterly results via screener.in integration
- **Computer Automation** — Stream analysis reports directly to Notepad, read PDFs/bills, automate keyboard input
- **Multi-Provider LLM Support** — Switch between OpenAI, Gemini, Groq, Cerebras, OpenRouter, or local LM Studio models
- **Decision Tree Generation** — Auto-generate policy decision trees with Mermaid visualization

## Repository Structure

```
MumbaiHacks/
├── Backend/                    # FastAPI RAG API, MCP servers, decision tree tools
│   ├── app/                    # Main application code (services, providers, pipelines)
│   ├── mcp_server/             # RAG and Computer MCP server implementations
│   ├── screener_server/        # Financial screener API service
│   ├── scripts/                # Utility scripts for decision trees
│   ├── tests/                  # Sample evaluation prompts + answers (JSON)
│   ├── results/                # Saved RAG inference outputs
│   ├── Policy documents/       # Source PDFs used during development
│   ├── run_mcp.py              # Entry point for RAG MCP server
│   ├── run_computer_mcp.py     # Entry point for Computer MCP server
│   ├── main.py                 # Entry point for FastAPI RAG REST API
│   ├── build_trees.py          # Decision tree builder script
│   └── requirements.txt        # Python dependencies
├── Frontend/                   # Next.js application (auth, chat, marketing)
│   ├── app/                    # Next.js App Router pages
│   ├── components/             # React components
│   ├── lib/                    # Utilities, config, Supabase client
│   ├── actions/                # Server actions
│   └── env.example             # Environment variable template
└── README.md                   # This file
```

---

## Prerequisites

- **Python 3.12+**
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`
- **Node.js 18.18+** (or latest LTS) and npm
- **Supabase project** (optional, for persistent vector storage)
- **Azure Document Intelligence credentials** (optional, for advanced document parsing)
- **Windows OS** (required for computer-use MCP server due to pyautogui/pywin32 dependencies)

---

## Quick Start

| Task | Command | Notes |
|------|---------|-------|
| Install backend deps | `cd Backend && pip install uv && uv venv --python=3.12 && uv pip install -r requirements.txt` | Installs MCP + FastAPI requirements |
| Run RAG MCP server | `cd Backend && python run_mcp.py` | Default port **8000** (`MCP_SERVER_PORT` env var) |
| Run Computer MCP server | `cd Backend && python run_computer_mcp.py` | Default port **8002** (`COMPUTER_MCP_PORT` env var) |
| Run Screener server | `cd Backend/screener_server && python run_server.py` | Default port **8080** |
| (Optional) Run FastAPI RAG API | `cd Backend && uv run main.py` | REST access at `http://localhost:8000` |
| Run backend tests | `cd Backend && python test_api.py` | Validates `/rag/run` behavior |
| Install frontend deps | `cd Frontend && npm install` | Installs Next.js app deps |
| Start frontend dev | `cd Frontend && npm run dev` | Available at `http://localhost:3000` |

> **Note:** Run backend services and frontend in parallel for the full experience.

---

## Backend Setup

### 1. Environment Variables

Create a `.env` file in the `Backend/` directory with the following variables:

```bash
# Environment
ENVIRONMENT=development  # or "production"

# Vector Store
DEFAULT_VECTOR_STORE=supabase  # or "inmemory"
EMBEDDING_MODEL=text-embedding-3-small

# LLM Provider (choose one as default)
DEFAULT_LLM_PROVIDER=openai  # openai | gemini | groq | cerebras | openrouter | lmstudio

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini

# Google Gemini (optional)
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

# Groq (optional)
GROQ_API_KEY=
GROQ_MODEL=llama-3.1-70b-versatile

# Cerebras (optional)
CEREBRAS_API_KEY=
CEREBRAS_MODEL=openai/gpt-oss-20b

# OpenRouter (optional)
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openai/gpt-4.1-mini

# LM Studio (optional, for local models)
LMSTUDIO_API_KEY=lm-studio
LMSTUDIO_MODEL=qwen/qwen3-4b
LMSTUDIO_BASE_URL=http://localhost:1234/v1

# Azure Document Intelligence (optional)
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=
AZURE_DOCUMENT_INTELLIGENCE_KEY=

# Supabase (required if using supabase vector store)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=
SUPABASE_TABLE_NAME=documents
SUPABASE_QUERY_NAME=match_documents

# Logging
ENABLE_REQUEST_LOGGING=true

# MCP Server Ports (optional overrides)
MCP_SERVER_PORT=8000
COMPUTER_MCP_PORT=8002
```

### 2. RAG MCP Server

```bash
cd Backend
python run_mcp.py
```

- Implements `process_document_rag` using FastMCP
- Default port: **8000** (override with `MCP_SERVER_PORT` env var)
- The frontend calls this server directly via `@modelcontextprotocol/sdk`

### 3. Computer MCP Server (Windows Only)

```bash
cd Backend
python run_computer_mcp.py
```

- Provides tools: `read_file`, `read_pdf`, `write_file`, `stream_to_notepad`, `type_text`, `list_files`
- Default port: **8002** (override with `COMPUTER_MCP_PORT` env var)
- **Requirements:** Windows + `pyautogui`, `pywin32`, `pyperclip`, `pymupdf` (all included in requirements.txt)

### 4. Screener Server

```bash
cd Backend/screener_server
pip install -r requirements.txt
python run_server.py
```

Or alternatively:

```bash
cd Backend/screener_server
uvicorn server:app --host 0.0.0.0 --port 8080 --reload
```

- Logs into screener.in (headless browser), fetches charts/PE data, quarterly results, announcements
- Exposes `/query_agent` endpoint backed by Google Custom Search
- Configure credentials in `credentials.py`

### 5. FastAPI RAG REST API (Optional)

```bash
cd Backend
uv run main.py
```

- Endpoints: `GET /`, `GET /health`, `POST /rag/run`
- Useful for CLI testing outside the MCP context
- Runs on port **8000** (same as MCP server, so only run one at a time)

### 6. Testing

```bash
cd Backend
python test_api.py
```

### 7. Decision Tree Builder

```bash
cd Backend
python build_trees.py
```

- Analyzes insurance documents and generates decision trees
- Outputs are saved to `Backend/results/`

Convert trees to Mermaid diagrams:

```bash
cd Backend/scripts/decision_tree
python convert_json_to_flowchart.py
```

### 8. Supabase Setup (Optional)

Enable `pgvector` and create the documents table:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents table
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for document_id filtering
CREATE INDEX IF NOT EXISTS idx_documents_metadata_docid
    ON public.documents ((metadata->>'document_id'));
```

Create the match function:

```sql
CREATE OR REPLACE FUNCTION public.match_documents(
    query_embedding VECTOR(1536),
    match_count INT,
    filter JSONB DEFAULT '{}'::JSONB
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE SQL STABLE AS $$
    SELECT d.id, d.content, d.metadata,
           1 - (d.embedding <=> query_embedding) AS similarity
    FROM public.documents d
    WHERE (
        (filter ? 'document_id' AND d.metadata->>'document_id' = filter->>'document_id')
        OR NOT (filter ? 'document_id')
    )
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
$$;
```

---

## Frontend Setup

### 1. Environment Variables

Copy the example file and fill in your values:

```bash
cd Frontend
cp env.example .env.local
```

Required variables in `.env.local`:

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_ADMIN=

# App Config
NEXT_PUBLIC_APP_NAME=Sampada AI
NEXT_PUBLIC_APP_ICON='/logos/sampada-ai-logo.webp'

# LLM Providers
GOOGLE_GENERATIVE_AI_API_KEY=
OPENAI_API_KEY=

# Web Search
TAVILY_API_KEY=

# Email (optional)
RESEND_API_KEY=
RESEND_DOMAIN=
```

### 2. Install & Run

```bash
cd Frontend
npm install
npm run dev
```

The app runs on `http://localhost:3000`.

### 3. Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server with Turbopack |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |

---

## Agentic Architecture

The copilot leverages MCP (Model Context Protocol) to expose tools that the AI can autonomously invoke:

| Service | Entry Point | Port | Capabilities |
|---------|-------------|------|--------------|
| **RAG MCP Server** | `python run_mcp.py` | 8000 | Document ingestion, semantic search, structure-aware Q&A |
| **Computer MCP Server** | `python run_computer_mcp.py` | 8002 | File read/write, PDF extraction, Notepad streaming, keyboard automation |
| **Screener Server** | `python run_server.py` | 8080 | Stock charts, PE ratios, quarterly results, peer analysis, concall links |
| **FastAPI RAG API** | `uv run main.py` | 8000 | REST interface for RAG (alternative to MCP) |

---

## API Reference

### POST /rag/run (FastAPI)

Request body:

```json
{
    "documents": "https://.../documents/Policy.pdf",
    "questions": [
        "What is the maternity coverage?",
        "What is the waiting period for pre-existing conditions?"
    ],
    "k": 8,
    "processing_mode": "structure_aware"
}
```

- `k` (optional): Static number of chunks to retrieve. Omit for dynamic k selection.
- `processing_mode`: `"traditional"` or `"structure_aware"` (table-aware chunking and reranking)

Response:

```json
{
    "success": true,
    "answers": ["...", "..."],
    "processing_time": 2.34,
    "document_metadata": {
        "chunks": 123,
        "vector_store": "supabase",
        "document_id": "<hash>"
    }
}
```

---

## Contributing

1. Keep README files updated when adding new services
2. Update `.env.example` / `env.example` when adding new config keys
3. Run `python test_api.py` and `npm run lint` before opening a PR

---

## Tech Stack

**Agentic Layer:**
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) via FastMCP
- Multi-provider LLM orchestration (OpenAI, Gemini, Groq, Cerebras, OpenRouter, LM Studio)
- Autonomous tool invocation with streaming responses

**Backend:**
- Python 3.12+ / FastAPI / Uvicorn
- LangChain + LangChain Community (RAG pipelines)
- Supabase pgvector (embeddings storage)
- Azure Document Intelligence (advanced PDF parsing)
- Selenium + undetected-chromedriver (screener.in scraping)
- pyautogui / pywin32 (desktop automation)

**Frontend:**
- Next.js 15 (App Router) + React 19
- Tailwind CSS 4 + shadcn/ui
- Supabase Auth + Realtime
- AI SDK (Vercel) with MCP client integration
- Recharts (financial visualizations)
