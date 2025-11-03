from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "source_domain", "published_at")
    search_fields = ("title", "source_url", "source_domain")
    list_filter = ("source_domain",)
