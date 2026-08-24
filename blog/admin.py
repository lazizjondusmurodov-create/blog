from django.contrib import admin
from .models import Author, Category, Blog, ContactMessage, Image, Comment


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


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'subject', 'email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_read',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_unread']

    @admin.action(description="O'qilgan deb belgilash")
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} ta xabar o'qilgan deb belgilandi.")

    @admin.action(description="O'qilmagan deb belgilash")
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} ta xabar o'qilmagan deb belgilandi.")

    def has_add_permission(self, request):
        """Xabar faqat sayt orqali keladi — admindan qo'lda qo'shilmaydi."""
        return False
