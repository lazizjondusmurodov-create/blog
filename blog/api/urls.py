from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AuthorViewSet,
    BlogViewSet,
    CategoryViewSet,
    CommentViewSet,
    ImageViewSet,
)

router = DefaultRouter()
router.register('blogs', BlogViewSet, basename='blog')
router.register('categories', CategoryViewSet, basename='category')
router.register('authors', AuthorViewSet, basename='author')
router.register('comments', CommentViewSet, basename='comment')
router.register('images', ImageViewSet, basename='image')

urlpatterns = [
    path('', include(router.urls)),
]
