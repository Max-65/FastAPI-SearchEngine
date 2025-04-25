from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse, urlunparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.crawler import Fetched

def extract(html: 'Fetched', base_url: str) -> list[str]:
    soup = BeautifulSoup(html.content, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        if not a or not isinstance(a, Tag):
            continue
        
        url = urljoin(base_url, str(a["href"]))
        parsed = urlparse(url)
        path = '/'.join(segment for segment in parsed.path.split('/') if segment)
        
        url = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            '/' + path,
            parsed.params,
            parsed.query,
            parsed.fragment.lower()
        ))
        if url.startswith('http'):
            links.append(url)

    return links
