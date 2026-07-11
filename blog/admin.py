from django.contrib import admin
from .models import Author, Category, Blog, Image, Comment


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'author', 'created_at')
    list_filter = ('category', 'author')
    search_fields = ('title', 'short_description')
    inlines = [ImageInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'blog', 'created_at')
    list_filter = ('blog',)
    search_fields = ('name', 'email', 'text')