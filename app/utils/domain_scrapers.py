import logging
from typing import Optional

from playwright.sync_api import Page

from .main_scraper import MainScraper


logger = logging.getLogger(__name__)


class TakeGroupScraper(MainScraper):
    def _extract_title(self, page: Page) -> Optional[str]:
        title = page.locator("article h1").text_content()
        if title:
            return title

        logger.warning("Błąd przy pobieraniu tytułu")
        return None

    def _extract_content_html(self, page: Page) -> Optional[str]:
        content = page.locator("div[class*='article-content']").inner_html()
        if content:
            return content

        logger.warning("Błąd przy pobieraniu html artykułu")

    def _extract_content_plain_text(self, page: Page) -> Optional[str]:
        content = page.locator("div[class*='article-content']").inner_text()
        if content:
            return content

        logger.warning("Błąd przy pobieraniu plain text artykułu")

    def _extract_published(self, page: Page) -> Optional[str]:
        datetime = page.locator("time").text_content()
        if datetime:
            return datetime

        logger.warning("Błąd przy pobieraniu daty")
        return None


class GalicjaExpressScraper(MainScraper):
    def _extract_title(self, page: Page) -> Optional[str]:
        title = page.locator("article h1").text_content()
        if title:
            return title

        logger.warning("Błąd przy pobieraniu tytułu")
        return None

    def _extract_content_html(self, page: Page) -> Optional[str]:
        content = page.locator("div.post-text-two-red").inner_html()
        if content:
            return content

        logger.warning("Błąd przy pobieraniu html artykułu")

    def _extract_content_plain_text(self, page: Page) -> Optional[str]:
        content = page.locator("div.post-text-two-red").inner_text()
        if content:
            return content

        logger.warning("Błąd przy pobieraniu plain text artykułu")

    def _extract_published(self, page: Page) -> Optional[str]:
        datetime = page.locator("article p").first.text_content()
        if datetime:
            return datetime

        logger.warning("Błąd przy pobieraniu daty")
        return None
