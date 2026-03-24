from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from database import init_db, search_query
from crawler import crawler_instance
import asyncio

app = FastAPI(title="Crawl Me Maybe Engine")

# Arayuz sablonlari icin klasor tanimlamasi
templates = Jinja2Templates(directory="templates")

# Uygulama baslarken veritabanini (tablolari) hazirla
@app.on_event("startup")
async def on_startup():
    await init_db()

# Ana Sayfa (UI)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request})

# İndekslemeyi baslatan endpoint
# queue_capacity parametresini ekliyoruz
@app.post("/index")
async def start_indexing(background_tasks: BackgroundTasks, origin: str, k: int, queue_capacity: int = 1000):
    if crawler_instance.is_running:
        return {"status": "error", "message": "Crawler is already running!"}
    
    # Yeni parametreyi crawler'a iletiyoruz
    background_tasks.add_task(crawler_instance.start_crawl, origin, k, queue_capacity)
    return {"status": "success", "message": f"Indexing started for {origin} with max depth {k} and capacity {queue_capacity}"}

# Arama yapan endpoint
@app.get("/search")
async def search(query: str):
    results = await search_query(query)
    # Istenen format: (relevant_url, origin_url, depth)
    formatted_results = [
        {"relevant_url": r[0], "origin_url": r[1], "depth": r[2]} 
        for r in results
    ]
    return {"query": query, "results": formatted_results}

# Sistemin anlik durumunu donduren endpoint (Back pressure takibi icin)
@app.get("/status")
async def get_status():
    return {
        "is_running": crawler_instance.is_running,
        "active_workers": crawler_instance.active_workers,
        "queue_size": crawler_instance.queue.qsize(),
        "indexed_pages": crawler_instance.indexed_pages
    }