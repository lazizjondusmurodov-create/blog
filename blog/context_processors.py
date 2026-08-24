from django.db.models import Count

from .models import Blog, Category


def site_context(request):
    """Har bir sahifada kerak bo'ladigan umumiy ma'lumot (footer, sidebar).

    Kategoriyalar blogs_count bilan annotate qilinadi — aks holda shablondagi
    har bir {{ category.blogs.count }} alohida so'rov yuborardi (N+1).
    """
    categories = Category.objects.annotate(blogs_count=Count('blogs'))

    return {
        'footer_categories': categories[:6],
        'footer_recent_blogs': (
            Blog.objects
            .select_related('category')
            .prefetch_related('images')
            .order_by('-created_at')[:3]
        ),
    }
