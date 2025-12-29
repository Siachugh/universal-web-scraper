"""JavaScript rendering using Playwright."""

from playwright.async_api import async_playwright, Browser, Page
from typing import Optional, Dict, List
import asyncio


async def render_with_playwright(url: str, timeout: int = 30000) -> Optional[str]:
    """Render page with Playwright and return HTML."""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate to page
            await page.goto(url, wait_until='networkidle', timeout=timeout)
            
            # Wait a bit for any dynamic content
            await asyncio.sleep(2)
            
            # Get rendered HTML
            html = await page.content()
            
            await browser.close()
            return html
    except Exception as e:
        print(f"Playwright render error: {e}")
        return None


async def render_with_interactions(
    url: str,
    scroll_depth: int = 3,
    click_selectors: Optional[List[str]] = None
) -> tuple[Optional[str], Dict]:
    """Render page with interactions (clicks, scrolls) and return HTML + interaction data."""
    interactions = {
        'clicks': [],
        'scrolls': 0,
        'pages': []
    }
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate to initial page
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(1)
            
            # Perform scrolls
            for i in range(scroll_depth):
                await page.evaluate('window.scrollBy(0, window.innerHeight)')
                await asyncio.sleep(1)
                interactions['scrolls'] += 1
            
            # Scroll back to top
            await page.evaluate('window.scrollTo(0, 0)')
            await asyncio.sleep(1)
            
            # Try to click "Load more" or "Show more" buttons
            if click_selectors:
                for selector in click_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            await element.click()
                            await asyncio.sleep(2)
                            interactions['clicks'].append({
                                'selector': selector,
                                'timestamp': None
                            })
                    except Exception:
                        pass
            
            # Try to find and click tabs
            try:
                tabs = await page.query_selector_all('[role="tab"]')
                if tabs and len(tabs) > 0:
                    # Click first tab if not already active
                    await tabs[0].click()
                    await asyncio.sleep(2)
                    interactions['clicks'].append({
                        'selector': '[role="tab"]',
                        'timestamp': None
                    })
            except Exception:
                pass
            
            # Try pagination
            try:
                next_buttons = await page.query_selector_all('a[aria-label*="next" i], a[aria-label*="Next" i], button[aria-label*="next" i]')
                if not next_buttons:
                    next_buttons = await page.query_selector_all('a:has-text("Next"), a:has-text("next")')
                
                pages_visited = 0
                for btn in next_buttons[:3]:  # Limit to 3 pages
                    try:
                        await btn.click()
                        await asyncio.sleep(2)
                        current_url = page.url
                        interactions['pages'].append(current_url)
                        pages_visited += 1
                        if pages_visited >= 3:
                            break
                    except Exception:
                        break
            except Exception:
                pass
            
            # Get final HTML
            html = await page.content()
            
            await browser.close()
            return html, interactions
            
    except Exception as e:
        print(f"Playwright interactions error: {e}")
        return None, interactions

