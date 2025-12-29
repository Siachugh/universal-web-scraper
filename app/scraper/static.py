"""Static HTML scraping using httpx and BeautifulSoup."""

import httpx
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
from .utils import make_absolute_url


async def fetch_static_html(url: str, timeout: float = 10.0) -> Optional[str]:
    """Fetch HTML content using httpx (static fetch)."""
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except Exception as e:
        print(f"Static fetch error: {e}")
        return None


def parse_static_html(html: str, base_url: str) -> Dict:
    """Parse static HTML and extract metadata."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract title
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else ""
    
    # Extract description
    desc_tag = soup.find('meta', attrs={'name': 'description'}) or \
               soup.find('meta', attrs={'property': 'og:description'})
    description = desc_tag.get('content', '') if desc_tag else ""
    
    # Extract language
    html_tag = soup.find('html')
    language = html_tag.get('lang', '') if html_tag else ""
    
    # Extract canonical
    canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
    canonical = make_absolute_url(base_url, canonical_tag.get('href', '')) if canonical_tag else None
    
    return {
        'title': title,
        'description': description,
        'language': language,
        'canonical': canonical,
        'soup': soup,
        'text_length': len(soup.get_text(strip=True))
    }


def should_use_js_fallback(parsed_data: Dict, min_text_length: int = 500) -> bool:
    """Determine if JS rendering fallback is needed."""
    text_length = parsed_data.get('text_length', 0)
    title = parsed_data.get('title', '')
    
    # Use JS if text is too short or title is missing
    if text_length < min_text_length:
        return True
    if not title:
        return True
    
    return False

