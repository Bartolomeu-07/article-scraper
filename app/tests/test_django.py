from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from unittest.mock import patch, MagicMock

from app.models import Article
from app.utils.main_scraper import MainScraper
from app.utils.scraper_factory import SCRAPER_REGISTRY, get_scraper_for_domain


# ---MODELS---
class TestArticleModel(TestCase):

    def test_save_sets_source_domain_from_source_url(self):
        test_cases = [
            ("https://example.com/some/path?x=1", "example.com"),
            ("http://example.com", "example.com"),
            ("https://www.example.com/articles/123", "www.example.com"),
            ("https://example.com:8443/docs", "example.com:8443"),
        ]

        for url, expected_domain in test_cases:
            article = Article.objects.create(
                title="T",
                content_html="<p>x</p>",
                content_text="x",
                source_url=url,
                source_domain="",
                published_at=timezone.now(),
            )

            article.save()
            self.assertEqual(article.source_domain, expected_domain)


# ---VIEWS---
class TestArticleViewSet(APITestCase):
    def setUp(self):
        now = timezone.now()
        self.a1 = Article.objects.create(
            title="One",
            content_html="<p>one</p>",
            content_text="one",
            source_url="https://example.com/a1",
            source_domain="example.com",
            published_at=now,
        )
        self.a2 = Article.objects.create(
            title="Two",
            content_html="<p>two</p>",
            content_text="two",
            source_url="https://blog.example.com/a2",
            source_domain="blog.example.com",
            published_at=now,
        )
        self.a3 = Article.objects.create(
            title="Three",
            content_html="<p>three</p>",
            content_text="three",
            source_url="https://another.net/a3",
            source_domain="another.net",
            published_at=now,
        )

    def test_list_returns_all_articles(self):
        url = reverse("article-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        returned_ids = {item["id"] for item in resp.data}
        self.assertSetEqual(returned_ids, {self.a1.id, self.a2.id, self.a3.id})

    def test_retrieve_returns_single_article(self):
        url = reverse("article-detail", args=[self.a2.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["id"], self.a2.id)
        self.assertEqual(resp.data["title"], "Two")
        self.assertEqual(resp.data["source_domain"], "blog.example.com")

    def test_list_filters_by_source_domain(self):
        url = reverse("article-list")
        resp = self.client.get(url, {"source": " example.COM "})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in resp.data]
        self.assertEqual(ids, [self.a1.id])

        resp2 = self.client.get(url, {"source": "blog.example.com"})
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        ids2 = [item["id"] for item in resp2.data]
        self.assertEqual(ids2, [self.a2.id])

    def test_list_no_filter_when_source_empty(self):
        url = reverse("article-list")
        resp = self.client.get(url, {"source": ""})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        returned_ids = {item["id"] for item in resp.data}
        self.assertSetEqual(returned_ids, {self.a1.id, self.a2.id, self.a3.id})


# ---SCRAPER_FACTORY---
class ExampleScraper:
    pass


class TestScraper:
    pass


class TestGetScraperForDomain(SimpleTestCase):

    def setUp(self):
        SCRAPER_REGISTRY.clear()
        SCRAPER_REGISTRY.update(
            {
                "example.com": ExampleScraper,
                "test.pl": TestScraper,
            }
        )

    def test_returns_scraper_for_example_com(self):
        scraper = get_scraper_for_domain("https://example.com/page")
        self.assertIsInstance(scraper, ExampleScraper)

    def test_returns_scraper_for_test_pl(self):
        scraper = get_scraper_for_domain("https://test.pl/abc")
        self.assertIsInstance(scraper, TestScraper)

    def test_returns_none_for_unknown_domain(self):
        scraper = get_scraper_for_domain("https://unknown.org")
        self.assertIsNone(scraper)


class _DummyScraper(MainScraper):
    def _extract_title(self, page):
        return None

    def _extract_content_html(self, page):
        return None

    def _extract_content_plain_text(self, page):
        return None

    def _extract_published(self, page):
        return None


class TestFetchPageLogs(SimpleTestCase):

    @patch("app.utils.main_scraper.logger")
    @patch("app.utils.main_scraper.sync_playwright")
    def test_logs_error_when_http_status_is_400_plus(
        self, mock_sync_playwright, mock_logger
    ):

        mock_p = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_response = MagicMock()
        mock_response.status = 404

        mock_sync_playwright.return_value.start.return_value = mock_p
        mock_p.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.goto.return_value = mock_response

        scraper = _DummyScraper()
        url = "https://example.com/whatever"
        p, page = scraper.fetch_page(url)

        mock_logger.error.assert_called_with(f"{url} → BŁĄD HTTP 404")
        self.assertIsNotNone(p)
        self.assertIs(page, mock_page)

    @patch("app.utils.main_scraper.logger")
    @patch("app.utils.main_scraper.sync_playwright")
    def test_does_not_log_error_when_status_ok(
        self, mock_sync_playwright, mock_logger
    ):

        mock_p = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_response = MagicMock()
        mock_response.status = 200

        mock_sync_playwright.return_value.start.return_value = mock_p
        mock_p.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.goto.return_value = mock_response

        scraper = _DummyScraper()
        url = "https://example.com/ok"
        p, page = scraper.fetch_page(url)

        mock_logger.error.assert_not_called()
        self.assertIsNotNone(p)
        self.assertIs(page, mock_page)

    @patch("app.utils.main_scraper.logger")
    @patch("app.utils.main_scraper.sync_playwright")
    def test_logs_error_when_response_is_none(
        self, mock_sync_playwright, mock_logger
    ):

        mock_p = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()

        mock_sync_playwright.return_value.start.return_value = mock_p
        mock_p.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.goto.return_value = None

        scraper = _DummyScraper()
        url = "https://example.com/no-response"
        scraper.fetch_page(url)

        mock_logger.error.assert_called_with(
            f"{url} → brak odpowiedzi od serwera"
        )
