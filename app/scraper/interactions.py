"""Interaction detection and handling for dynamic content."""

from typing import List, Dict, Optional
from bs4 import BeautifulSoup


def find_click_targets(soup: BeautifulSoup) -> List[str]:
    """Find potential click targets (tabs, load more buttons, etc.)."""
    selectors = []
    
    # Find tabs
    tabs = soup.find_all(attrs={'role': 'tab'})
    if tabs:
        selectors.append('[role="tab"]')
    
    # Find "Load more" or "Show more" buttons
    load_more_texts = ['load more', 'show more', 'see more', 'view more']
    for text in load_more_texts:
        # Find buttons with text containing the search term
        all_buttons = soup.find_all('button')
        buttons = [btn for btn in all_buttons if text.lower() in btn.get_text().lower()]
        if buttons:
            selectors.append(f'button:has-text("{text}")')
        
        # Find links with text containing the search term
        all_links = soup.find_all('a')
        links = [link for link in all_links if text.lower() in link.get_text().lower()]
        if links:
            selectors.append(f'a:has-text("{text}")')
    
    return selectors

