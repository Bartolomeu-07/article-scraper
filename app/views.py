from rest_framework import viewsets, mixins

from .models import Article
from .serializers import ArticleSerializer


class ArticleViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):

    serializer_class = ArticleSerializer
    queryset = Article.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        source = self.request.query_params.get("source")

        if source:
            # Normalize query params
            # Removing extra spaces to avoid errors when the user accidentally includes a space
            source = source.strip().lower()
            qs = qs.filter(source_domain__icontains=source)
        return qs