# Product Requirements Document (PRD)

## Objective
Build a concurrent web crawler and search engine using an AI coding assistant (Claude/Cursor/Copilot). The system must handle indexing and searching simultaneously on localhost, manage its own load, and feature a modern UI.

## Core Components

### 1. Indexer (`/index`)
- **Inputs:** `origin` (URL), `k` (max depth), `queue_capacity`.
- **Logic:** Crawl pages asynchronously up to depth `k`. Extract all textual words and outgoing links.
- **Constraints:** Never crawl the same page twice. Implement back pressure using a bounded queue.
- **Resumability:** Store visited URLs in a database to prevent redundant work upon restart.

### 2. Search Engine (`/search`)
- **Inputs:** `query` (string).
- **Outputs:** A list of triples: `(relevant_url, origin_url, depth)`.
- **Constraints:** Must be thread-safe. Search must run concurrently without being blocked by active indexing workers.

### 3. Database
- Use `SQLite` with an asynchronous driver (`aiosqlite`) to support concurrent read/write operations.

### 4. User Interface
- Provide a single-page application using `FastAPI` and `Tailwind CSS`.
- Display real-time metrics (Queue Depth, Active Workers, Indexed Pages, System State) via background polling.