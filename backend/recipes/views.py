from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from recipes.models import Tag
from api.serializers import TagSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Отображение тегов."""
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)

    # def perform_create(self, serializer):
    #     tag = get_object_or_404(
    #         Ingredient,
    #         id=self.kwargs.get('tag_id')
    #     )
    #     serializer.save(
    #         author=self.request.user.is_superuser,
    #         tag=tag
    #     )