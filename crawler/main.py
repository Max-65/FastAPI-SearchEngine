from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.crawler import Crawler
from config import START_URL

app = FastAPI()

@app.post('/test')
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
                "content": content
            }
            cached_response["pages"].append(page)

        return cached_response
    
    finally:
        await crawler.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)