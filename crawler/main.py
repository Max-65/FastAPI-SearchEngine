from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.crawler import Crawler
from config import START_URL, REQUEST_TIMEOUT
import httpx

app = FastAPI()

@app.post('/api/crawler')
async def main():
    crawler = Crawler()
    try:
        await crawler.crawl(START_URL)

        id = 0
        cached_response = {
            "message": f"Found {len(crawler.results)} pages",
            "pages": list()
        }
        for url, content in crawler.results.items():
            id += 1
            page = {
                "id":      id,
                "url":     url,
                "content": {
                    'title':   content.title,
                    'meta':    content.meta,
                    'headers': content.headers
                }
            }
            cached_response["pages"].append(page)

        async with httpx.AsyncClient() as client:
            await client.post(
                'http://api-gateway/api/extractor',
                json = cached_response,
                timeout = REQUEST_TIMEOUT
            )
    
    finally:
        await crawler.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)