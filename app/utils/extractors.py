from __future__ import annotations

import logging
import time
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from .date import parse_any_date

logger = logging.getLogger(__name__)


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

def fetch_html(
    url: str,
    timeout: int = 15,
    wait_selector: Optional[str] = None,
    do_scroll: bool = False,
    headless: bool = True,
    user_agent: Optional[str] = None,
) -> Optional[str]:
    """
    Pobiera renderowany HTML strony przy użyciu Playwright.
    Zwraca HTML (string) lub None przy błędzie.
    """
    ua = user_agent or DEFAULT_USER_AGENT
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(user_agent=ua)
            page = context.new_page()

            ms_timeout = int(timeout * 1000)
            page.goto(url, wait_until="networkidle", timeout=ms_timeout)

            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=8000)


            if do_scroll:
                # proste przewijanie, żeby wymusić lazy-load
                for _ in range(5):
                    page.evaluate("window.scrollBy(0, window.innerHeight);")
                    time.sleep(0.4)

            html = page.content()
            browser.close()
            return html

    except Exception as e:
        logger.exception("Błąd podczas fetch_html_playwright_simple dla %s: %s", url, e)
        return None


def extract_title(soup: BeautifulSoup) -> Optional[str]:
    og = soup.select_one('meta[property="og:title"]')
    if og and og.get("content"):
        return og["content"].strip()

    if soup.title and soup.title.string:
        return soup.title.string.strip()

    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    return None


def extract_published(soup: BeautifulSoup) -> Optional[str]:
    # Szukamy kilku popularnych wariantów
    candidates: list[str] = []

    for sel in [
        'meta[property="article:published_time"]',
        'meta[name="pubdate"]',
        'meta[name="publish-date"]',
        'meta[name="publication_date"]',
        'meta[name="date"]',
        'meta[itemprop="datePublished"]',
        "time[datetime]",
    ]:
        el = soup.select_one(sel)
        if el:
            val = el.get("content") or el.get("datetime")
            if val:
                candidates.append(val)

    # Ostatnia próba: element <time> bez datetime – jego tekst
    if not candidates:
        for t in soup.find_all("time"):
            txt = t.get_text(strip=True)
            if txt:
                candidates.append(txt)

    print(candidates)

    return candidates[0] if candidates else None


def extract_main_html(soup: BeautifulSoup) -> Optional[str]:
    # Priorytet: <article>
    art = soup.find("article")
    if art:
        return str(art)

    # Dalej: <main>
    main = soup.find("main")
    if main:
        return str(main)

    # Dalej: heurystyka po klasach
    for cls in [
        "content",
        "post",
        "article",
        "entry",
        "post-content",
        "article-body",
    ]:
        div = soup.find("div", class_=lambda c: c and cls in c)
        if div:
            return str(div)

    # Fallback: body (ryzyko szumu)
    body = soup.find("body")
    return str(body) if body else None


def extract_article(url: str) -> Optional[dict]:
    html = fetch_html(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    title = extract_title(soup) or "(brak tytułu)"
    published_raw = extract_published(soup)
    published_dt = parse_any_date(published_raw[0])

    main_html = extract_main_html(soup)
    if not main_html:
        logger.error("Nie udało się wyodrębnić treści dla %s", url)
        return None

    main_soup = BeautifulSoup(main_html, "html.parser")
    content_html = str(main_soup)
    content_text = main_soup.get_text(strip=True)

    return {
        "title": title,
        "content_html": content_html,
        "content_text": content_text,
        "published_at": published_dt,
        "source_url": url,
        "source_domain": urlparse(url).netloc,
    }
