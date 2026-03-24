import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from database import is_visited, mark_visited, save_index

class WebCrawler:
    def __init__(self, max_concurrent_workers=10, max_queue_size=1000):
        self.max_workers = max_concurrent_workers
        self.max_queue_size = max_queue_size
        self._queue = None  
        self.is_running = False
        self.active_workers = 0
        self.indexed_pages = 0

    @property
    def queue(self):
        if self._queue is None:
            self._queue = asyncio.Queue(maxsize=self.max_queue_size)
        return self._queue

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and parsed.scheme in ['http', 'https']

    def extract_words(self, text):
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        return [w.lower() for w in words]

    async def fetch_page(self, session, url):
        try:
            async with session.get(url, timeout=5, ssl=False) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"HATA: Sayfa reddetti (HTTP {response.status}) ← {url}")
        except Exception as e:
            pass 
        return None

    async def worker(self, session, max_depth):
        self.active_workers += 1
        while self.is_running:
            try:
                if self.queue.empty():
                    await asyncio.sleep(1)
                    continue

                current_url, origin_url, current_depth = await self.queue.get()
                
                if current_depth > max_depth:
                    self.queue.task_done()
                    continue

                if await is_visited(current_url):
                    self.queue.task_done()
                    continue

                await mark_visited(current_url)
                
                print(f"Taraniyor ← {current_url} (Derinlik: {current_depth})")
                
                html_content = await self.fetch_page(session, current_url)
                if html_content:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    text_content = soup.get_text(separator=' ')
                    words = set(self.extract_words(text_content))
                    for word in words:
                        await save_index(word, current_url, origin_url, current_depth)
                    
                    self.indexed_pages += 1

                    if current_depth < max_depth:
                        for link in soup.find_all('a', href=True):
                            next_url = urljoin(current_url, link['href'])
                            if self.is_valid_url(next_url) and not await is_visited(next_url):
                                try:
                                    self.queue.put_nowait((next_url, origin_url, current_depth + 1))
                                except asyncio.QueueFull:
                                    pass 

                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"HATA: Worker icinde beklenmeyen sorun ← {e}")
                self.queue.task_done()
                
        self.active_workers -= 1

    async def start_crawl(self, origin, k, queue_capacity=1000):
        try:
            self.is_running = True
            self.indexed_pages = 0
            
            # Eski kuyrugu silip kullanicinin istedigi kapasitede yepyeni bir kuyruk yaratiyoruz
            self.max_queue_size = queue_capacity
            self._queue = asyncio.Queue(maxsize=self.max_queue_size)
                
            await self.queue.put((origin, origin, 0))
            print("\n>>> Sistem tetiklendi, Worker'lar basliyor... <<<")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            connector = aiohttp.TCPConnector(ssl=False, limit=self.max_workers)
            
            async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
                tasks = []
                for _ in range(self.max_workers):
                    task = asyncio.create_task(self.worker(session, max_depth=k))
                    tasks.append(task)
                
                await self.queue.join()
                print(">>> Tarama tamamlandi, sistem duruyor. <<<\n")
                
                self.is_running = False
                for task in tasks:
                    task.cancel()
        except Exception as e:
            print(f"KRITIK HATA: {e}")
            self.is_running = False

# En kritik satir: Uygulamanin aradigi instance
crawler_instance = WebCrawler()