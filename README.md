Universal Website Scraper with Interaction-Aware JSON Output

A full-stack universal web scraping system built using FastAPI that extracts content from both static and JavaScript-rendered websites, performs basic user interactions (clicks, scrolling, pagination), and returns section-aware structured JSON.
The project also includes a minimal frontend UI to trigger scraping and view/download results.

Features:

Static-first web scraping with intelligent JavaScript fallback
Handles JS-rendered pages using Playwright
Supports user interactions:
Clicking tabs / “Load more” buttons
Infinite scrolling / pagination (depth ≥ 3)
Extracts content into logical sections (hero, nav, footer, etc.)
Returns schema-compliant structured JSON
Minimal frontend to:
Enter a URL
Trigger scraping
View structured sections

Tech Stack:
Backend
Python 3.10+
FastAPI
Playwright (Python) for JS rendering
BeautifulSoup4 for HTML parsing
httpx for static fetching
Uvicorn as ASGI server

Frontend
Jinja2 templates
Basic HTML + CSS (minimal UI)
Download full JSON output
Robust error handling with partial result recovery

How to Run:
Prerequisites

Python 3.10 or higher
Node.js (required for Playwright browsers)

Interaction Strategy

Detects clickable elements such as:
Tabs
“Load more / Show more” buttons

Performs:
Scroll depth ≥ 3
Pagination or infinite scrolling where applicable
Records all interactions in the response JSON
