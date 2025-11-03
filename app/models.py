from django.db import models
from urllib.parse import urlparse


class Article(models.Model):
    title = models.CharField(max_length=500)
    content_html = models.TextField()
    content_text = models.TextField()
    source_url = models.URLField(unique=True)
    source_domain = models.CharField(max_length=255, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.source_url and not self.source_domain:
            self.source_domain = urlparse(self.source_url).netloc
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.source_domain})"
