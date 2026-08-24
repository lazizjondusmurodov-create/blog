from rest_framework import serializers

from blog.models import Author, Blog, Category, Comment, Image


class BlogsCountField(serializers.IntegerField):
    """Queryset annotate qilgan bo'lsa o'shani, aks holda .count() ni qaytaradi.

    Shu tufayli ro'yxatda N+1 bo'lmaydi, ichma-ich (nested) ishlatilganda esa
    maydon yo'qolib qolmaydi.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault('read_only', True)
        super().__init__(**kwargs)

    def get_attribute(self, instance):
        annotated = getattr(instance, 'blogs_count', None)
        if annotated is not None:
            return annotated
        return instance.blogs.count()

    def to_representation(self, value):
        return int(value)


class AuthorSerializer(serializers.ModelSerializer):
    blogs_count = BlogsCountField()

    class Meta:
        model = Author
        fields = ['id', 'name', 'bio', 'image', 'blogs_count']


class CategorySerializer(serializers.ModelSerializer):
    blogs_count = BlogsCountField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'image', 'blogs_count']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image', 'blog']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'blog', 'name', 'email', 'text', 'created_at']
        read_only_fields = ['created_at']


class BlogListSerializer(serializers.ModelSerializer):
    """Ro'yxat uchun — yengil, faqat kerakli maydonlar."""

    category = serializers.StringRelatedField()
    author = serializers.StringRelatedField()
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'short_description',
            'category', 'author', 'comments_count', 'created_at',
        ]


class BlogDetailSerializer(serializers.ModelSerializer):
    """Bitta blog uchun — ichma-ich bog'liq ma'lumotlar bilan."""

    category = CategorySerializer(read_only=True)
    author = AuthorSerializer(read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'short_description', 'long_description',
            'category', 'author', 'images', 'comments', 'created_at',
        ]


class BlogWriteSerializer(serializers.ModelSerializer):
    """POST / PUT / PATCH uchun — id orqali bog'lanadi."""

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'short_description', 'long_description',
            'category', 'author',
        ]

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Sarlavha kamida 5 ta belgidan iborat bo'lishi kerak."
            )
        return value
