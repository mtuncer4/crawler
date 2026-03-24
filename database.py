import aiosqlite

DB_NAME = "crawler.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Taranan URL'leri tutar (Tekrar taramamak icin)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS visited (
                url TEXT PRIMARY KEY
            )
        """)
        
        # Crawler koptugunda devam edebilmesi icin siradaki URL'ler (Frontier)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS frontier (
                url TEXT PRIMARY KEY,
                origin_url TEXT,
                depth INTEGER
            )
        """)
        
        # Arama motoru icin kelime indeksi (Search)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS search_index (
                word TEXT,
                relevant_url TEXT,
                origin_url TEXT,
                depth INTEGER
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_word ON search_index(word)")
        await db.commit()

async def mark_visited(url):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO visited (url) VALUES (?)", (url,))
        await db.commit()

async def is_visited(url):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT 1 FROM visited WHERE url = ?", (url,)) as cursor:
            return await cursor.fetchone() is not None

async def save_index(word, relevant_url, origin_url, depth):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO search_index (word, relevant_url, origin_url, depth) VALUES (?, ?, ?, ?)",
            (word, relevant_url, origin_url, depth)
        )
        await db.commit()

async def search_query(query):
    async with aiosqlite.connect(DB_NAME) as db:
        words = query.lower().split()
        results = []
        for word in words:
            async with db.execute(
                "SELECT relevant_url, origin_url, depth FROM search_index WHERE word = ?", 
                (word,)
            ) as cursor:
                rows = await cursor.fetchall()
                results.extend(rows)
        # Basit bir frequency (frekans) siralamasi yapilabilir ama simdilik direkt donuyoruz
        return list(set(results))