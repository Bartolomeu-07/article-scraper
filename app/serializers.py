from rest_framework import serializers
from django.utils import timezone
from zoneinfo import ZoneInfo
from .models import Article
WARSAW_TZ = ZoneInfo("Europe/Warsaw")


class ArticleSerializer(serializers.ModelSerializer):
    published_at = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content_html",
            "content_text",
            "source_url",
            "source_domain",
            "published_at",
            ]
    def get_published_at(self, obj):

        if not obj.published_at:
            return None

        dt = obj.published_at.astimezone(WARSAW_TZ)

        return dt.strftime("%d.%m.%Y %H:%M:%S")