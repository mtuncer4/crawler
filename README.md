# Advanced Web Crawler & Search Engine

A high-performance, asynchronous web crawler and search engine built with Python, FastAPI, and SQLite. This project demonstrates concurrent execution, back pressure management, and real-time search capabilities.

## Features
- **Asynchronous Crawling:** Utilizes `asyncio` and `aiohttp` for non-blocking, highly concurrent web scraping.
- **Back Pressure Management:** Configurable max depth ($k$) and queue capacity to prevent memory overload.
- **Thread-Safe Search:** Search functionality remains fully operational while the indexer is actively crawling, thanks to `aiosqlite`.
- **Resumability:** Visited URLs and indexes are stored in a local SQLite database, ensuring the crawler doesn't restart from scratch if interrupted.
- **Modern UI:** A clean, responsive dashboard built with Tailwind CSS to monitor live system metrics and perform searches.

## Installation & Setup
1. Clone the repository and navigate to the project directory.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

## Run the application 

1. uvicorn main:app --reload
2. Open your browser and navigate to http://127.0.0.1:8000
