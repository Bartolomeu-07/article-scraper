import logging
from typing import Optional
from urllib.parse import urlparse

from .domain_scrapers import *

logger = logging.getLogger(__name__)


# --- DOMAIN REGISTRY ---
SCRAPER_REGISTRY: dict[str, type[MainScraper]] = {
    "take-group.github.io": TakeGroupScraper,
    "galicjaexpress.pl": GalicjaExpressScraper,
}

def get_scraper_for_domain(url: str) -> Optional[MainScraper]:
    host = (urlparse(url).hostname or "").lower()
    for domain, klass in SCRAPER_REGISTRY.items():
        if host == domain or host.endswith("." + domain):
            return klass()

    logger.error(f"Brak scrapera dla domeny: {host}")
    return None

def scrap_article(url: str) -> Optional[dict]:
    scraper = get_scraper_for_domain(url)
    return scraper.extract_article(url)