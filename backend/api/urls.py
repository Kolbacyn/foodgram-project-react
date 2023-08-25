from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import CustomUserViewSet
from recipes.views import TagViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('rest_framework.urls')),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
