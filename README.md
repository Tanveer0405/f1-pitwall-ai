# Veloce — F1 Intelligence

> An AI-powered Formula 1 chatbot built on Retrieval-Augmented Generation (RAG). Ask anything about drivers, races, championships, and technical regulations from 1950 to the present day.

---

## Table of Contents

1. [What This Project Is](#what-this-project-is)
2. [System Architecture](#system-architecture)
3. [Tech Stack](#tech-stack)
4. [Data Pipeline](#data-pipeline)
5. [Backend — FastAPI + RAG Engine](#backend--fastapi--rag-engine)
6. [Frontend — Next.js 14](#frontend--nextjs-14)
7. [Project Structure](#project-structure)
8. [Local Setup & Running](#local-setup--running)
9. [Environment Variables](#environment-variables)
10. [How the RAG Pipeline Works](#how-the-rag-pipeline-works)
11. [Design Decisions](#design-decisions)
12. [Deployment Guide](#deployment-guide)


---

## What This Project Is

Veloce is a domain-specific AI chatbot that answers questions about Formula 1 racing. Unlike a general-purpose LLM, Veloce is grounded entirely in a curated, on-disk knowledge base of F1 data — race results, driver standings, constructor standings, driver profiles, technical regulations, Wikipedia articles, and scraped editorial content — spanning 1950 through 2025.

The core intelligence mechanism is **Retrieval-Augmented Generation (RAG)**. When a user asks a question, the system:

1. Converts the question into a high-dimensional vector using a local embedding model
2. Searches a ChromaDB vector store for the most semantically similar knowledge chunks
3. Injects those chunks as context into a Groq-hosted LLaMA 3.1 prompt
4. Returns a grounded, factual answer without hallucinating outside the stored data

The frontend is a dark-themed, F1-aesthetic chat interface built in Next.js 14, named **Veloce** (Italian for *fast*). It features a Claude/Gemini-style collapsible sidebar with full persistent chat history stored in `localStorage`.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                         │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │           Next.js 14 Frontend (Vercel)              │  │
│   │                                                     │  │
│   │  • Veloce chat UI (dark F1 theme)                   │  │
│   │  • Sidebar with localStorage chat history           │  │
│   │  • /api/chat route (server-side proxy)              │  │
│   └──────────────────────┬──────────────────────────────┘  │
└──────────────────────────┼──────────────────────────────────┘
                           │ HTTP POST /chat
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Render)                    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   RAG Engine                         │  │
│  │                                                      │  │
│  │  1. Receive question                                 │  │
│  │  2. Embed via BGE-small-en-v1.5 (local CPU)         │  │
│  │  3. Similarity search → top 8 chunks from ChromaDB  │  │
│  │  4. Build system prompt with context                 │  │
│  │  5. Query Groq API (LLaMA 3.1 8B)                   │  │
│  │  6. Return answer + source file names               │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                   │
│  ┌──────────────────────┴───────────────────────────────┐  │
│  │              ChromaDB Vector Store                   │  │
│  │          (persisted at data/chroma_db/)              │  │
│  │                                                      │  │
│  │  • Thousands of semantic chunks                      │  │
│  │  • Indexed by BGE-small-en-v1.5 embeddings          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                    Groq Cloud API
               (LLaMA-3.1-8B-Instant)
```

---

## Tech Stack

### Backend
| Component | Technology | Purpose |
|---|---|---|
| API Framework | FastAPI | REST API server, request validation |
| RAG Retrieval | ChromaDB | Local vector database for semantic search |
| Embeddings | `BAAI/bge-small-en-v1.5` via HuggingFace | Text-to-vector encoding, runs on CPU |
| LLM | Groq API — LLaMA 3.1 8B Instant | Answer generation from retrieved context |
| LangChain | `langchain-huggingface`, `langchain-chroma` | Embedding and vector store abstraction |
| Runtime | Python 3.11+ with Uvicorn | ASGI server |

### Frontend
| Component | Technology | Purpose |
|---|---|---|
| Framework | Next.js 14 (App Router) | React-based full-stack web app |
| Styling | Tailwind CSS v3 | Utility-first dark theme CSS |
| Language | TypeScript | Type-safe components |
| Markdown | `react-markdown` | Renders LLM responses with formatting |
| Icons | `lucide-react` | UI iconography |
| Storage | Browser `localStorage` | Persistent per-device chat history |
| Deployment | Vercel | Frontend hosting |

### Data Collection
| Script | Technology | Purpose |
|---|---|---|
| `get_complete_history.py` | `requests` + Ergast/Jolpi API | Race results, standings (2018–2025) |
| `get_all_history.py` | `requests` + Ergast/Jolpi API | Driver standings (1950–2025) |
| `expand_f1_data.py` | Wikipedia API | Technical articles, team histories, driver biographies |
| `scrape_articles.py` | Crawl4AI + Playwright | Editorial articles and event summaries |
| `fetch_tech_specs.py` | Crawl4AI + Playwright | Engine history, circuit details |
| `chunk_all_data.py` | LangChain `RecursiveCharacterTextSplitter` | Parse + chunk raw data into semantic units |
| `store_vectors.py` | ChromaDB + HuggingFace | Embed chunks and build the vector database |

---

## Data Pipeline

The knowledge base is built in four sequential stages. These scripts are run **once locally** to build the vector store. The resulting `data/chroma_db/` is committed to the repo and served by the backend at runtime.

### Stage 1 — Raw Data Collection

Three categories of data are collected:

**A. Structured API Data (JSON)**

Via the [Jolpi Ergast F1 API](https://api.jolpi.ca/ergast/f1):

- `{year}_raceResults.json` — Full race-by-race finishing orders (2018–2025), including driver, constructor, grid position, final position, points, and race status
- `{year}_driverStandings.json` — Season-final driver championship standings (1950–2025), including points and wins
- `{year}_constructorStandings.json` — Season-final constructor standings (2018–2025)
- `all_historical_drivers.json` — Complete driver profile index (name, nationality, date of birth) for every F1 driver in history

**B. Wikipedia Articles (Plain Text)**

Via the Wikipedia API (`action=query&prop=extracts&explaintext=true`), covering:

- Technical topics: aerodynamics, ground effect, DRS, tyres, hybrid engines, braking systems, suspension geometry, ECU/telemetry
- Teams: Ferrari, McLaren, Mercedes, Red Bull, Williams, Alpine, Aston Martin, Haas, Sauber
- Drivers: Schumacher, Hamilton, Senna, Verstappen, Vettel, Antonelli
- Circuits: Silverstone, Monza, Spa, Suzuka, Monaco
- Regulations: F1 regulations history, safety evolution
- Championship seasons: 2022, 2023, 2024, 2025, 2026

**C. Scraped Editorial Content (Markdown)**

Via Crawl4AI (headless Chromium):

- 2024 Monaco GP Wikipedia article
- Race reports from Racefans.net
- Engine history and circuit technical details

### Stage 2 — Parsing & Narrative Conversion (`chunk_all_data.py`)

Raw JSON is not directly embeddable — it needs to be converted into natural language sentences that the embedding model can encode meaningfully.

The parser converts structured API data into prose narratives:

```
Input (JSON):
  { "season": "2021", "position": "1", "Driver": { "givenName": "Max", "familyName": "Verstappen" }, ... }

Output (narrative string):
  "Championship Standings: In the 2021 Formula 1 World Championship, driver Max Verstappen
   driving for Red Bull finished in final rank 1 with 395.5 points and 10 race victories."
```

Four parsers handle the different data shapes:
- **Race results parser** — converts position/grid/status/points per driver per race
- **Driver standings parser** — converts final championship rankings per season
- **Constructor standings parser** — converts team championship positions per season
- **Driver profile parser** — converts biographical data

Plain text files (Wikipedia articles, scraped content) are passed through without transformation.

### Stage 3 — Chunking

All narratives are split using LangChain's `RecursiveCharacterTextSplitter`:

- **Chunk size:** 800 characters (~150–200 words)
- **Overlap:** 100 characters (preserves cross-boundary context)
- Each chunk carries metadata: `source` (filename) and `type` (`championship_json` or `technical_text`)

This chunk size is deliberately chosen to keep each unit as a single coherent fact or narrative sentence group, which maximises retrieval precision.

### Stage 4 — Embedding & Indexing (`store_vectors.py`)

Each chunk is encoded using `BAAI/bge-small-en-v1.5`:

- 384-dimensional dense vectors
- Fully local — runs on CPU, no API calls
- L2-normalised for cosine similarity search
- Stored persistently in ChromaDB at `data/chroma_db/`

This stage runs once. The resulting ChromaDB directory is the complete searchable knowledge base. The backend loads it at startup and holds it in memory as a singleton.

---

## Backend — FastAPI + RAG Engine

### `backend/main.py`

The FastAPI application exposes two endpoints:

```
GET  /health   →  {"status": "ok", "service": "F1 Chatbot API"}
POST /chat     →  {"answer": "...", "sources": ["filename1.json", ...]}
```

Request body:
```json
{ "message": "Who won the 2023 championship?" }
```

Response body:
```json
{
  "answer": "Max Verstappen won the 2023 Formula 1 World Championship driving for Red Bull Racing...",
  "sources": ["2023_driverStandings.json", "2023_raceResults.json"]
}
```

CORS is configured to allow requests from `localhost:3000` (development) and the production Vercel domain.

### `backend/rag_engine.py`

The RAG engine uses a **singleton pattern** — the embedding model and ChromaDB connection are initialised once at server startup and reused across all requests. This avoids reloading the ~130MB embedding model on every query, keeping response latency low.

Query flow:

```python
def query_rag(question: str, k: int = 8) -> dict:
    # 1. Embed the question using BGE-small
    # 2. Retrieve top-8 semantically similar chunks from ChromaDB
    # 3. Concatenate chunks into a context block
    # 4. Build system prompt with strict grounding instruction
    # 5. Call Groq API (LLaMA 3.1 8B, temp=0.2, max_tokens=1000)
    # 6. Return answer text + list of source filenames
```

The system prompt instructs the model to synthesise across chunks if needed, answer directly without prefacing with "based on the context", and only admit missing data if the context genuinely contains nothing relevant.

`k=8` (retrieving 8 chunks) was chosen over the initial `k=4` to give the model enough coverage for multi-part questions like championship comparisons across seasons.

---

## Frontend — Next.js 14

### App Router Structure

```
frontend/src/app/
├── layout.tsx          ← Root layout, metadata ("Veloce — F1 Intelligence")
├── globals.css         ← Tailwind directives + custom animations
├── page.tsx            ← Full chatbot UI (single page app)
└── api/
    └── chat/
        └── route.ts    ← Server-side API proxy to FastAPI backend
```

### Why a Next.js API Route?

The `/api/chat/route.ts` server-side proxy serves two purposes:

1. **Hides the backend URL** — `BACKEND_URL` is an environment variable only available on the server, never exposed to the browser
2. **Enables future auth** — middleware can be added here to attach user tokens, rate-limit, or validate sessions without touching the frontend component

### Chat History

Conversations are stored in `localStorage` under the key `veloce_conversations`. Each conversation is:

```ts
interface Conversation {
  id: string;       // "conv_1718123456789"
  title: string;    // First message, truncated to 42 chars
  messages: Message[];
  createdAt: number;  // Unix timestamp for sorting
}
```

On mount, the app hydrates from `localStorage` and re-instantiates `Date` objects (which JSON serialisation flattens to strings). On every state change, it persists back. This gives Claude/Gemini-style persistent history with zero backend infrastructure.

### UI Components

**Sidebar** — Collapsible (240px → 0) with CSS transition. Shows all past conversations sorted newest-first. Hovering a conversation reveals a delete button. Active conversation highlighted with a subtle red border. "Engine online" indicator with a pulsing red dot at the bottom.

**Message Bubbles** — User messages: red gradient background, rounded with cut corner. Bot messages: dark panel with subtle white border, bot avatar (Veloce logo) on the left. Both use 14px sans-serif for readability. Bot responses render full Markdown including headings, bold, lists, and inline code.

**Input Bar** — HUD-panel aesthetic with four corner bracket accents in F1 red. A status dot changes: dim white (idle) → glowing red (typing) → pulsing yellow (loading). The send button glows red when active.

**Empty State** — Logo and greeting displayed side-by-side. Greeting randomly selects from five F1 radio-call phrases on each page load ("Box, box. Ready when you are.", "Lights out. Let's talk Formula 1.", etc.). Six suggestion cards with emoji icons and hover interactions.

### Tailwind Theme

Custom colour tokens defined in `tailwind.config.js`:

```js
f1red:    "#E10600"   // Official F1 red
f1dark:   "#08090a"   // Near-black background
f1panel:  "#0f1117"   // Slightly lighter panel background
f1border: "#1e2130"   // Subtle border colour
f1accent: "#FF4D00"   // Brighter orange-red for hover states
f1muted:  "#6b7280"   // Muted grey for secondary text
```

---

## Project Structure

```
f1-pitwall-ai/
│
├── backend/                        ← FastAPI application
│   ├── main.py                     ← API server (routes, CORS, request models)
│   ├── rag_engine.py               ← RAG logic (embedding, retrieval, LLM call)
│   ├── requirements.txt            ← Python dependencies
│   └── .env                        ← Local env vars (NOT committed)
│
├── frontend/                       ← Next.js 14 application
│   ├── src/
│   │   └── app/
│   │       ├── layout.tsx          ← Root layout + metadata
│   │       ├── page.tsx            ← Full chatbot UI
│   │       ├── globals.css         ← Global styles + Tailwind + animations
│   │       └── api/chat/route.ts   ← Server-side proxy to FastAPI
│   ├── package.json
│   ├── tailwind.config.js          ← Custom F1 colour tokens + keyframes
│   ├── next.config.js
│   ├── tsconfig.json
│   └── postcss.config.js
│
├── data/
│   ├── raw/                        ← Raw collected data (JSON + TXT)
│   │   ├── {year}_raceResults.json
│   │   ├── {year}_driverStandings.json
│   │   ├── {year}_constructorStandings.json
│   │   ├── all_historical_drivers.json
│   │   ├── {topic}.txt             ← Wikipedia plaintext articles
│   │   └── text_source_{n}.txt     ← Scraped editorial content
│   ├── processed/
│   │   └── master_f1_chunks.json   ← Parsed + chunked data (intermediate)
│   └── chroma_db/                  ← ChromaDB vector store (final knowledge base)
│
├── chunk_all_data.py               ← Stage 2: Parse raw → narrative chunks
├── store_vectors.py                ← Stage 4: Embed chunks → ChromaDB
├── get_complete_history.py         ← Stage 1a: Fetch race/standings data (2018–2025)
├── get_all_history.py              ← Stage 1b: Fetch driver standings (1950–2025)
├── get_api_data.py                 ← Stage 1c: Fetch specific round data
├── expand_f1_data.py               ← Stage 1d: Download Wikipedia articles
├── scrape_articles.py              ← Stage 1e: Scrape editorial articles (Crawl4AI)
├── fetch_tech_specs.py             ← Stage 1f: Scrape engine/circuit tech pages
├── app.py                          ← Original CLI chatbot (prototype, not used in deployment)
├── .gitignore
└── README.md
```

---

## Local Setup & Running

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Groq API key (free at [console.groq.com](https://console.groq.com))

### 1. Clone the repo

```bash
git clone https://github.com/Tanveer0405/f1-pitwall-ai.git
cd f1-pitwall-ai
```

### 2. Set up the backend

```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env`:
```
GROQ_API_KEY=your_groq_api_key_here
CHROMA_DIR=D:\f1-chatbot\data\chroma_db
```

> Use the absolute path to your `chroma_db` directory. On Windows use backslashes or forward slashes — both work with `os.path.normpath()`.

Start the backend:
```bash
uvicorn main:app --reload --port 8000
```

Verify it's running:
```
http://localhost:8000/health
→ {"status":"ok","service":"F1 Chatbot API"}
```

On first startup, the terminal will print:
```
[RAG] Loading ChromaDB from: D:\f1-chatbot\data\chroma_db
[RAG] ChromaDB loaded. XXXX vectors in collection.
```

If it prints `0 vectors`, the chroma_db path is wrong or you need to re-run `store_vectors.py`.

### 3. Set up the frontend

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```
BACKEND_URL=http://localhost:8000
```

Start the frontend:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### 4. Rebuilding the vector store (if needed)

If you want to rebuild the knowledge base from scratch:

```bash
# Collect raw data (run from project root)
python get_complete_history.py     # race results + standings 2018–2025
python get_all_history.py          # driver standings 1950–2025
python expand_f1_data.py           # Wikipedia articles

# Parse and chunk
python chunk_all_data.py           # → data/processed/master_f1_chunks.json

# Build vector store
python store_vectors.py            # → data/chroma_db/
```

> Scraping scripts (`scrape_articles.py`, `fetch_tech_specs.py`) require Playwright browsers. Run `playwright install chromium` first and note they write to hardcoded `D:\f1-chatbot\` paths — update these if your project is in a different location.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq API key for LLaMA inference |
| `CHROMA_DIR` | Yes | Absolute path to the `data/chroma_db/` directory |

### Frontend (`frontend/.env.local` for dev, Vercel env vars for production)

| Variable | Required | Description |
|---|---|---|
| `BACKEND_URL` | Yes | URL of the FastAPI backend (`http://localhost:8000` locally, Render URL in production) |

---

## How the RAG Pipeline Works

### Why RAG instead of fine-tuning?

Fine-tuning a model on F1 data would bake the knowledge into the weights — but F1 data changes every season. RAG keeps knowledge and model separate: update the vector store with 2025 race results and the model immediately has that knowledge, no retraining required.

### Why `bge-small-en-v1.5`?

BGE (BAAI General Embeddings) models consistently outperform OpenAI's `ada-002` on retrieval benchmarks at a fraction of the cost (free, local). The `-small` variant (384 dims) gives excellent performance with low memory and fast CPU inference — important since the backend runs on a free Render instance with no GPU.

### Why ChromaDB?

ChromaDB is a lightweight vector database that persists to disk as a directory of files. For a project of this scale (tens of thousands of chunks), it requires no separate database server, no cloud costs, and no operational complexity. The entire knowledge base ships as part of the repository.

### Why Groq?

Groq's inference hardware (LPUs) runs LLaMA 3.1 8B at extremely low latency — typical response times are under 1 second for the LLM call, making the total RAG pipeline feel responsive despite CPU-based retrieval.

### Retrieval quality

The system retrieves `k=8` chunks per query. The chunk size of 800 characters was chosen to ensure each chunk is a complete, coherent unit of information (typically 2–4 sentences of narrative text or a group of race results from one event). The 100-character overlap prevents context from being split at chunk boundaries for facts that span sentences.

---

## Design Decisions

**Why narrative conversion of JSON?**
Embedding models are trained on natural language. Embedding raw JSON (`{"position": "1", "points": "25"}`) produces poor-quality vectors because the model has no linguistic signal to work with. Converting to `"Driver Max Verstappen finished in position 1 with 25 points"` gives the embedding model real semantic content to encode, dramatically improving retrieval accuracy.

**Why a Next.js API route instead of calling FastAPI directly from the browser?**
Calling the backend directly from the browser would expose the backend URL in client-side JavaScript, making it trivially easy to scrape or abuse. The server-side API route (`/api/chat/route.ts`) keeps the backend URL in a server-side environment variable. It also provides a natural insertion point for rate limiting, authentication, or request logging without touching the UI.

**Why `localStorage` for chat history?**
For a portfolio/demo deployment, `localStorage` gives a polished user experience — history persists across page refreshes and browser restarts — with zero backend infrastructure. The tradeoff is that history is device-local and lost on browser data clear. A future upgrade path to per-user server-side history via NextAuth.js + PostgreSQL is planned.

**Why singleton globals in the RAG engine?**
Loading the BGE embedding model takes ~3–5 seconds on cold start and consumes ~130MB of RAM. Reloading it on every HTTP request would make every query slow and eventually OOM-crash the server. The singleton pattern loads it once when the first request arrives and reuses it indefinitely.

---

## Deployment Guide

### Backend → Render

| Setting | Value |
|---|---|
| Root Directory | `backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

Environment variables to set in Render dashboard:
```
GROQ_API_KEY = <your key>
CHROMA_DIR   = ../data/chroma_db
```

> The path `../data/chroma_db` works because Render sets the working directory to `backend/` — one level up resolves to the repo root where `data/` lives.

### Frontend → Vercel

| Setting | Value |
|---|---|
| Root Directory | `frontend` |
| Framework | Next.js (auto-detected) |

Environment variable to set in Vercel dashboard:
```
BACKEND_URL = https://your-render-service.onrender.com
```

After both are deployed, update CORS in `backend/main.py`:
```python
allow_origins=[
    "http://localhost:3000",
    "https://your-project.vercel.app",
]
```

### Critical deployment note

The `data/chroma_db/` directory must be present in the repo for Render to serve it. Render's filesystem is ephemeral — the vector store cannot be built at deploy time (it takes too long and exceeds memory). Check the size of `data/chroma_db/` before pushing:

- **Under 80MB** → commit directly, push to GitHub
- **Over 80MB** → use Git LFS: `git lfs track "data/chroma_db/**"`

---


