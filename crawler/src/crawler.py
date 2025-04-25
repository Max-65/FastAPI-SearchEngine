import httpx
from bs4 import BeautifulSoup, ResultSet, Tag

from config import REQUEST_TIMEOUT, DEFAULT_AGENT, MAX_DEPTH, MAX_COUNT
from typing import Set, Dict, TYPE_CHECKING
from dataclasses import dataclass

from src.print import log
from src.parser import extract

if TYPE_CHECKING:
    from src.parser import extract # Only typechecking

@dataclass
class Fetched:
    code:    int
    content: str

@dataclass
class PageContent:
    title:   str            | None
    meta:    ResultSet[Tag] | None
    headers: list[str]

class Crawler:
    def __init__(self):
        self.visited: Set[str] = set()
        self.results: Dict[str, PageContent] = {}
        self.client = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)
        self.count: int = 0

    async def fetch(self, url: str) -> Fetched: # URL fetching function
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers={
                        "User-Agent": DEFAULT_AGENT,
                        "Accept": "text/html" # Only HTML docs are expected to be relevant for keywords
                    },
                    follow_redirects=True,
                    timeout=REQUEST_TIMEOUT
                )
                response.raise_for_status()
                return Fetched(response.status_code, response.text)
            
        except httpx.RequestError as err:
            # Error occured before response (DNS, timeout, no network connection)
            log(f"Request failed: {str(err)}")
            return Fetched(500, f"Request Error: {str(err)}")

        except httpx.HTTPStatusError as err:
            # Error occured after response (4xx, 5xx)
            log(f"HTTP Error: {err.response.status_code}")
            return Fetched(err.response.status_code, err.response.text)

        except Exception as err:
            # Unexpected errors
            log(f"Unexpected error: {str(err)}")
            return Fetched(500, f"Unexpected Error: {str(err)}")

    async def crawl(self, url: str, depth: int = 0): # Recursive URL crawling function
        if (depth > MAX_DEPTH) or (self.count > MAX_COUNT) or (url in self.visited):
            return
        
        self.count += 1
        self.visited.add(url)
        log(f'Crawling: {url} (depth {depth} | count {self.count})')

        html = await self.fetch(url)
        if not html:
            return
        
        soup = BeautifulSoup(html.content, "html.parser")
        title   = soup.title
        meta    = soup.select('meta[name="description"], meta[name="keywords"]')
        headers = soup.find_all(["h1", "h2", "h3"])

        self.results[url] = PageContent(
            title   = title.string if title else None,
            meta    = meta if meta else None,
            headers = [h.text for h in headers]
        )

        links = extract(html, url)
        for link in links:
            await self.crawl(link, depth+1)
    
    async def close(self):
        await self.client.aclose()