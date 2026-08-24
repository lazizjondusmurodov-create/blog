from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Blog, Category, Comment


def _categories():
    """Sidebar uchun kategoriyalar — blogs_count annotate qilingan.

    Annotate bo'lmasa shablondagi har bir sanoq alohida so'rov yuboradi (N+1).
    """
    return Category.objects.annotate(blogs_count=Count('blogs'))


def blog_list(request):
    blogs = (
        Blog.objects
        .select_related('author', 'category')
        .prefetch_related('images')
        .order_by('-created_at')
    )
    return render(request, 'blog/blog.html', {
        'blogs': blogs,
        'categories': _categories(),
        'nav_active': 'blog',
    })


def blog_detail(request, pk):
    blog = get_object_or_404(
        Blog.objects.select_related('author', 'category'),
        pk=pk
    )

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        text = request.POST.get('text')

        if name and email and text:
            Comment.objects.create(blog=blog, name=name, email=email, text=text)
            messages.success(request, "Izohingiz qo'shildi!")
            return redirect('blog_detail', pk=pk)
        else:
            messages.error(request, "Barcha maydonlarni to'ldiring!")

    comments = blog.comments.all().order_by('-created_at')
    related_blogs = (
        Blog.objects
        .select_related('category')
        .prefetch_related('images')
        .filter(category=blog.category)
        .exclude(pk=blog.pk)[:3]
    )

    return render(request, 'blog/single.html', {
        'blog': blog,
        'comments': comments,
        'comments_count': comments.count(),
        'related_blogs': related_blogs,
        'categories': _categories(),
        'nav_active': 'blog',
    })


def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    blogs = (
        category.blogs
        .select_related('author', 'category')
        .prefetch_related('images')
        .order_by('-created_at')
    )
    return render(request, 'blog/category.html', {
        'category': category,
        'blogs': blogs,
        'categories': _categories(),
        'nav_active': 'blog',
    })


def search(request):
    query = request.GET.get('s', '').strip()

    blogs = Blog.objects.none()
    if query:
        blogs = (
            Blog.objects
            .select_related('author', 'category')
            .prefetch_related('images')
            .filter(
                Q(title__icontains=query)
                | Q(short_description__icontains=query)
                | Q(long_description__icontains=query)
            )
            .distinct()
            .order_by('-created_at')
        )

    return render(request, 'blog/search-result.html', {
        'blogs': blogs,
        'categories': _categories(),
        'query': query,
        'nav_active': 'blog',
    })


def contact(request):
    return render(request, 'blog/contact.html', {
        'categories': _categories(),
        'nav_active': 'contact',
    })
