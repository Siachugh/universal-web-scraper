# Design Notes

## Static vs JS Fallback

- **Strategy**: Always attempt static HTML fetch first using httpx. This is faster and more efficient for most websites. JS rendering (Playwright) is only triggered if:
  - Static fetch fails
  - Extracted text length is less than 500 characters
  - Page title is missing
  - This heuristic ensures we only use the heavier JS rendering when necessary

## Wait Strategy for JS

- [x] Network idle
- [ ] Fixed sleep
- [x] Selector wait
- **Details**: 
  - Primary wait: `wait_until='networkidle'` for initial page load
  - Additional fixed sleep: 2 seconds after network idle to allow dynamic content
  - After interactions (clicks, scrolls): 1-2 second delays to allow content to load
  - This combination balances speed and reliability

## Click & Scroll Strategy

- **Clicks implemented**:
  - Tab elements: Detects `[role="tab"]` and clicks first tab if available
  - Load more buttons: Searches for buttons/links with text containing "load more", "show more", "see more", "view more"
  - Uses Playwright's selector API for reliable element interaction
  
- **Scroll/pagination**:
  - Infinite scroll: Performs 3 scrolls by scrolling down by viewport height each time
  - Pagination: Searches for next buttons using aria-labels or text content, clicks up to 3 pages
  - Scrolls back to top after initial scrolling to capture above-fold content
  
- **Stop conditions**:
  - Maximum 3 pagination pages
  - Maximum 3 scrolls
  - Element not found (graceful failure)
  - Timeout after 30 seconds

## Section Grouping & Labels

- **Grouping logic**:
  - Primary: Semantic HTML5 elements (`<section>`, `<article>`, `<main>`, `<header>`, `<footer>`, `<nav>`, `<aside>`)
  - Fallback: If no semantic sections found, creates one section from `<body>`
  - Ensures at least one section is always returned (non-empty requirement)
  
- **Label derivation**:
  1. First heading (h1-h6) within the section
  2. `aria-label` attribute if present
  3. Section type as fallback (e.g., "Hero", "Section", "Nav")
  - Labels are human-readable and descriptive

## Noise Filtering & Truncation

- **Filters**:
  - Cookie banners: `[id*="cookie"]`, `[class*="cookie"]`
  - Modals/popups: `[id*="modal"]`, `[class*="modal"]`, `[id*="popup"]`, `[class*="popup"]`
  - Newsletters: `[id*="newsletter"]`, `[class*="newsletter"]`
  - Generic banners: `[id*="banner"]`, `[class*="banner"]`
  - Dialogs: `[role="dialog"]`
  - Close buttons: `[aria-label*="close" i]`, `[aria-label*="dismiss" i]`
  - Uses BeautifulSoup's `decompose()` to remove elements from DOM before parsing
  
- **Truncation method**:
  - HTML truncation: Limits rawHtml to 50,000 characters, appends "... [truncated]"
  - Content limits: Text (5000 chars), links (100), images (50), lists (20), tables (10)
  - Prevents response bloat while preserving essential content
  - `truncated` flag indicates if truncation occurred

