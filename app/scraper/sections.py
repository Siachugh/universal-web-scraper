"""Section extraction and parsing from HTML."""

from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Optional
from .utils import make_absolute_url, truncate_html


def filter_noise_elements(soup: BeautifulSoup) -> BeautifulSoup:
    """Remove noise elements like cookie banners, modals, etc."""
    # Remove common noise selectors
    noise_selectors = [
        '[id*="cookie"]',
        '[class*="cookie"]',
        '[id*="banner"]',
        '[class*="banner"]',
        '[id*="modal"]',
        '[class*="modal"]',
        '[id*="popup"]',
        '[class*="popup"]',
        '[id*="newsletter"]',
        '[class*="newsletter"]',
        '[role="dialog"]',
        '[aria-label*="close" i]',
        '[aria-label*="dismiss" i]'
    ]
    
    for selector in noise_selectors:
        for elem in soup.select(selector):
            elem.decompose()
    
    return soup


def extract_sections(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    """Extract sections from HTML."""
    sections = []
    section_id_counter = 0
    
    # Filter noise first
    soup = filter_noise_elements(soup)
    
    # Try to find semantic sections
    semantic_sections = soup.find_all(['section', 'article', 'main', 'header', 'footer', 'nav', 'aside'])
    
    # Also look for common class patterns
    common_patterns = [
        'hero', 'banner', 'navigation', 'nav', 'footer', 'content',
        'section', 'article', 'main-content', 'sidebar', 'faq', 'pricing'
    ]
    
    found_elements = set()
    
    # Process semantic sections
    for elem in semantic_sections:
        if elem in found_elements:
            continue
        found_elements.add(elem)
        
        section_type = determine_section_type(elem)
        label = generate_section_label(elem, section_type)
        
        content = extract_content(elem, base_url)
        raw_html = str(elem)
        truncated = len(raw_html) > 50000
        
        sections.append({
            'id': f"{section_type}-{section_id_counter}",
            'type': section_type,
            'label': label,
            'sourceUrl': base_url,
            'content': content,
            'rawHtml': truncate_html(raw_html),
            'truncated': truncated
        })
        section_id_counter += 1
    
    # If no semantic sections found, create one from body
    if not sections:
        body = soup.find('body')
        if body:
            section_type = 'section'
            label = 'Main Content'
            content = extract_content(body, base_url)
            raw_html = str(body)
            truncated = len(raw_html) > 50000
            
            sections.append({
                'id': f"{section_type}-{section_id_counter}",
                'type': section_type,
                'label': label,
                'sourceUrl': base_url,
                'content': content,
                'rawHtml': truncate_html(raw_html),
                'truncated': truncated
            })
    
    # Ensure at least one section
    if not sections:
        sections.append({
            'id': 'unknown-0',
            'type': 'unknown',
            'label': 'Content',
            'sourceUrl': base_url,
            'content': {
                'headings': [],
                'text': soup.get_text(strip=True)[:1000],
                'links': [],
                'images': [],
                'lists': [],
                'tables': []
            },
            'rawHtml': truncate_html(str(soup)),
            'truncated': False
        })
    
    return sections


def determine_section_type(elem: Tag) -> str:
    """Determine section type from element."""
    tag_name = elem.name.lower()
    
    if tag_name == 'nav':
        return 'nav'
    if tag_name == 'footer':
        return 'footer'
    if tag_name == 'header':
        # Check if it's a hero section
        classes = ' '.join(elem.get('class', [])).lower()
        if 'hero' in classes:
            return 'hero'
        return 'section'
    
    # Check class names for hints
    classes = ' '.join(elem.get('class', [])).lower()
    id_attr = elem.get('id', '').lower()
    combined = f"{classes} {id_attr}"
    
    if 'hero' in combined:
        return 'hero'
    if 'faq' in combined:
        return 'faq'
    if 'pricing' in combined:
        return 'pricing'
    if 'list' in combined or tag_name == 'ul' or tag_name == 'ol':
        return 'list'
    if 'grid' in combined:
        return 'grid'
    
    return 'section'


def generate_section_label(elem: Tag, section_type: str) -> str:
    """Generate human-readable label for section."""
    # Try heading inside section
    heading = elem.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    if heading:
        return heading.get_text(strip=True)
    
    # Try aria-label
    aria_label = elem.get('aria-label')
    if aria_label:
        return aria_label
    
    # Use type as fallback
    return section_type.replace('-', ' ').title()


def extract_content(elem: Tag, base_url: str) -> Dict:
    """Extract content from element."""
    # Extract headings
    headings = []
    for heading in elem.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        text = heading.get_text(strip=True)
        if text:
            headings.append(text)
    
    # Extract text (remove script and style)
    for script in elem(['script', 'style']):
        script.decompose()
    text = elem.get_text(separator=' ', strip=True)
    
    # Extract links
    links = []
    for link in elem.find_all('a', href=True):
        link_text = link.get_text(strip=True)
        href = make_absolute_url(base_url, link.get('href', ''))
        if href:
            links.append({
                'text': link_text,
                'href': href
            })
    
    # Extract images
    images = []
    for img in elem.find_all('img', src=True):
        src = make_absolute_url(base_url, img.get('src', ''))
        alt = img.get('alt', '')
        if src:
            images.append({
                'src': src,
                'alt': alt
            })
    
    # Extract lists
    lists = []
    for ul_ol in elem.find_all(['ul', 'ol']):
        items = []
        for li in ul_ol.find_all('li', recursive=False):
            item_text = li.get_text(strip=True)
            if item_text:
                items.append(item_text)
        if items:
            lists.append(items)
    
    # Extract tables (simplified)
    tables = []
    for table in elem.find_all('table'):
        rows = []
        for tr in table.find_all('tr'):
            cells = []
            for td in tr.find_all(['td', 'th']):
                cell_text = td.get_text(strip=True)
                if cell_text:
                    cells.append(cell_text)
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    
    return {
        'headings': headings,
        'text': text[:5000],  # Limit text length
        'links': links[:100],  # Limit links
        'images': images[:50],  # Limit images
        'lists': lists[:20],  # Limit lists
        'tables': tables[:10]  # Limit tables
    }

