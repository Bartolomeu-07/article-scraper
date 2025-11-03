from __future__ import annotations
import logging
from http.client import responses

from typing import Optional
from abc import ABC, abstractmethod

from playwright.sync_api import sync_playwright, Page, Playwright
import nest_asyncio

from .date_utils import parse_any_date


logger = logging.getLogger(__name__)


class MainScraper(ABC):
    def extract_article(self, url: str) -> Optional[dict]:

        nest_asyncio.apply()
        playwright = None
        page = None

        try:
            playwright, page = self.fetch_page(url)
            title = self._extract_title(page)
            content_html = self._extract_content_html(page)
            content_plain_text = self._extract_content_plain_text(page)
            datetime_raw = self._extract_published(page)
            published_at = parse_any_date(datetime_raw)
        finally:
            if page:
                page.context.browser.close()
            if playwright:
                playwright.stop()

        return {
            "title": title,
            "content_html": content_html,
            "content_text": content_plain_text,
            "source_url": url,
            "published_at": published_at,
        }

    def fetch_page(self, url: str) -> tuple[Playwright, Page]:
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        response = page.goto(url, timeout=40000, wait_until="domcontentloaded")

        if response is None:
            logger.error(f"{url} → brak odpowiedzi od serwera")
        else:
            status = response.status
            if status >= 400:
                logger.error(f"{url} → BŁĄD HTTP {status}")

        selectors = [
            "article",
            "div.article-content",
            ".post-text-two-red",
        ]
        page.wait_for_selector(", ".join(selectors), timeout=30000)
        return (p, page)

    @abstractmethod
    def _extract_title(self, page: Page) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def _extract_content_html(self, page: Page) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def _extract_content_plain_text(self, page: Page) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def _extract_published(self, page: Page) -> Optional[str]:
        raise NotImplementedError
