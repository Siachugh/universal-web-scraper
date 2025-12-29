"""FastAPI main application."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
import uvicorn

from app.scraper.static import fetch_static_html, parse_static_html, should_use_js_fallback
from app.scraper.js import render_with_playwright, render_with_interactions
from app.scraper.sections import extract_sections
from app.scraper.interactions import find_click_targets
from app.scraper.utils import is_valid_url

app = FastAPI(title="Universal Website Scraper")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")


class ScrapeRequest(BaseModel):
    url: str


@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Frontend page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/scrape")
async def scrape(request: ScrapeRequest):
    """Scrape website endpoint."""
    url = request.url
    
    # Validate URL
    if not is_valid_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL. Must be http or https.")
    
    errors = []
    html = None
    parsed_data = None
    interactions = {
        'clicks': [],
        'scrolls': 0,
        'pages': []
    }
    
    # Step 1: Try static scraping first
    try:
        html = await fetch_static_html(url)
        if html:
            parsed_data = parse_static_html(html, url)
    except Exception as e:
        errors.append({
            'message': f"Static fetch failed: {str(e)}",
            'phase': 'fetch'
        })
    
    # Step 2: Check if JS fallback is needed
    use_js = False
    if parsed_data:
        use_js = should_use_js_fallback(parsed_data)
    else:
        use_js = True
    
    # Step 3: Use JS rendering if needed
    if use_js:
        try:
            # Try to find click targets from static HTML if available
            click_selectors = []
            if html:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                click_selectors = find_click_targets(soup)
            
            # Render with interactions
            js_html, js_interactions = await render_with_interactions(
                url,
                scroll_depth=3,
                click_selectors=click_selectors if click_selectors else None
            )
            
            if js_html:
                html = js_html
                interactions = js_interactions
                # Re-parse with JS-rendered HTML
                parsed_data = parse_static_html(html, url)
            else:
                # Fallback to simple JS render
                js_html = await render_with_playwright(url)
                if js_html:
                    html = js_html
                    parsed_data = parse_static_html(html, url)
                    # Still do some scrolling
                    interactions['scrolls'] = 3
        except Exception as e:
            errors.append({
                'message': f"JS rendering failed: {str(e)}",
                'phase': 'render'
            })
    
    # Step 4: Extract sections
    sections = []
    if parsed_data and parsed_data.get('soup'):
        try:
            sections = extract_sections(parsed_data['soup'], url)
        except Exception as e:
            errors.append({
                'message': f"Section extraction failed: {str(e)}",
                'phase': 'parse'
            })
    
    # Ensure sections is not empty
    if not sections:
        # Create a minimal section
        sections = [{
            'id': 'unknown-0',
            'type': 'unknown',
            'label': 'Content',
            'sourceUrl': url,
            'content': {
                'headings': [],
                'text': parsed_data.get('title', '') if parsed_data else '',
                'links': [],
                'images': [],
                'lists': [],
                'tables': []
            },
            'rawHtml': '<div>No content extracted</div>',
            'truncated': False
        }]
    
    # Build response
    result = {
        'url': url,
        'scrapedAt': datetime.utcnow().isoformat() + 'Z',
        'meta': {
            'title': parsed_data.get('title', '') if parsed_data else '',
            'description': parsed_data.get('description', '') if parsed_data else '',
            'language': parsed_data.get('language', '') if parsed_data else '',
            'canonical': parsed_data.get('canonical') if parsed_data else None
        },
        'sections': sections,
        'interactions': interactions,
        'errors': errors
    }
    
    return {'result': result}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

