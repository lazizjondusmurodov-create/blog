from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from blog.models import Author, Blog, Category, Comment, Image

from .throttles import CommentBurstThrottle

from .serializers import (
    AuthorSerializer,
    BlogDetailSerializer,
    BlogListSerializer,
    BlogWriteSerializer,
    CategorySerializer,
    CommentSerializer,
    ImageSerializer,
)


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = (
        Author.objects
        .annotate(blogs_count=Count('blogs'))
        .order_by('id')
    )
    serializer_class = AuthorSerializer
    search_fields = ['name', 'bio']
    ordering_fields = ['id', 'name', 'blogs_count']


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = (
        Category.objects
        .annotate(blogs_count=Count('blogs'))
        .order_by('id')
    )
    serializer_class = CategorySerializer
    search_fields = ['title']
    ordering_fields = ['id', 'title', 'blogs_count']


class BlogViewSet(viewsets.ModelViewSet):
    queryset = (
        Blog.objects
        .select_related('category', 'author')
        .prefetch_related('images', 'comments')
        .annotate(comments_count=Count('comments'))
    )
    filterset_fields = ['category', 'author']
    search_fields = ['title', 'short_description', 'long_description']
    ordering_fields = ['created_at', 'title', 'comments_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return BlogWriteSerializer
        if self.action == 'retrieve':
            return BlogDetailSerializer
        return BlogListSerializer

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def comments(self, request, pk=None):
        """GET /api/blogs/<id>/comments/ — shu blogning izohlari."""
        blog = self.get_object()
        serializer = CommentSerializer(blog.comments.all(), many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('blog')
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]  # izohni har kim qoldira oladi
    filterset_fields = ['blog']
    search_fields = ['name', 'text']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_throttles(self):
        """Chegara faqat yozishga — izohlarni o'qish cheklanmaydi."""
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [CommentBurstThrottle()]
        return super().get_throttles()


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.select_related('blog').order_by('id')
    serializer_class = ImageSerializer
    filterset_fields = ['blog']
