# Projekt Django ze scraperem artykułów

## 📦 Instalacja zależności

Upewnij się, że masz zainstalowane Python 3.10+ oraz `pip`.

```bash

git clone <repo-url>
cd <project-folder>
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Wykonaj migracje bazy danych:

```bash

python manage.py migrate
```

## ▶️ Uruchomienie projektu

Aby uruchomić serwer developerski Django:

```bash

python manage.py runserver
```

Aplikacja będzie dostępna pod adresem:

```
http://127.0.0.1:8000/
```

## 🕷️ Uruchomienie scrapera artykułów

Projekt zawiera komendę do scrapowania artykułów:

```bash
python manage.py scrape_articles
```

Scraper pobiera dane z zewnętrznych źródeł i zapisuje je do bazy.

## 📡 Endpointy API

### ✅ Lista artykułów

**GET** `/api/articles/`

**Przykład odpowiedzi:**

```json
[
  {
    "id": 1,
    "title": "Przykładowy artykuł",
    "content_html": "<p> Treść artykułu </p",
    "content_text": "Treść artykułu",
    "source_url": "https://example.com/artykul",
    "published_at": "12.10.2025 08:00:00"
  }
]
```

### ✅ Szczegóły artykułu

**GET** `/api/articles/<id>/`

**Przykład odpowiedzi:**

```json
{
  "id": 1,
  "title": "Przykładowy artykuł",
  "content_html": "<p> Treść artykułu </p",
  "content_text": "Treść artykułu",
  "source_url": "https://example.com/artykul",
  "published_at": "12.10.2025 08:00:00"
}
```

### ✅ Artykuły z wybranej domeny

**GET** `/api/articles/?source=example.com`

**Przykład odpowiedzi:**

```json
[
    {
      "id": 1,
      "title": "Przykładowy artykuł",
      "content_html": "<p> Treść artykułu </p",
      "content_text": "Treść artykułu",
      "source_url": "https://example.com/artykul",
      "published_at": "12.10.2025 08:00:00"
    }
]
```
---
