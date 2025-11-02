import logging
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from app.models import Article
from app.utils.extractors import extract_article

logger = logging.getLogger(__name__)

URLS = [
    "https://galicjaexpress.pl/ford-c-max-jaki-silnik-benzynowy-wybrac-aby-zaoszczedzic-na-paliwie",
    "https://galicjaexpress.pl/bmw-e9-30-cs-szczegolowe-informacje-o-osiagach-i-historii-modelu",
    "https://take-group.github.io/example-blog-without-ssr/jak-kroic-piers-z-kurczaka-aby-uniknac-suchych-kawalkow-miesa",
    "https://take-group.github.io/example-blog-without-ssr/co-mozna-zrobic-ze-schabu-oprocz-kotletow-5-zaskakujacych-przepisow",
]


class Command(BaseCommand):
    help = "Scrape predefined articles and store them in the database (unique by source_url)."

    def handle(self, *args, **options):
        total = len(URLS)
        self.stdout.write(self.style.NOTICE(f"Start scraping {total} articles"))

        for idx, url in enumerate(URLS, start=1):
            self.stdout.write(f"Scraping article {idx}/{total}... {url}")

            if Article.objects.filter(source_url=url).exists():
                self.stdout.write(self.style.WARNING("→ Już w bazie. Pomijam."))
                continue

            try:
                data = extract_article(url)
                if not data:
                    self.stdout.write(self.style.ERROR("→ Błąd ekstrakcji (pomijam)"))
                    continue

                article = Article(**data)
                article.save()
                self.stdout.write(self.style.SUCCESS(f"→ Zapisano (id={article.id})"))

            except IntegrityError:
                self.stdout.write(self.style.WARNING("→ Duplikat URL – pominięty"))

            except Exception as e:
                logger.exception("Błąd przy przetwarzaniu %s: %s", url, e)
                self.stdout.write(self.style.ERROR(f"→ Wyjątek: {e}"))

        self.stdout.write(self.style.SUCCESS("Zakończono."))