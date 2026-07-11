from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Blog, Category, Comment


def blog_list(request):
    blogs = Blog.objects.select_related('author', 'category').all()
    categories = Category.objects.all()
    return render(request, 'blog/blog.html', {
        'blogs': blogs,
        'categories': categories,
    })


def blog_detail(request, pk):
    blog = get_object_or_404(
        Blog.objects.select_related('author', 'category'),
        pk=pk
    )
    comments = blog.comments.all().order_by('-created_at')
    categories = Category.objects.all()

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

    related_blogs = Blog.objects.filter(
        category=blog.category
    ).exclude(pk=blog.pk)[:3]

    return render(request, 'blog/single.html', {
        'blog': blog,
        'comments': comments,
        'comments_count': comments.count(),
        'related_blogs': related_blogs,
        'categories': categories,
    })


def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    blogs = category.blogs.all()
    categories = Category.objects.all()
    return render(request, 'blog/category.html', {
        'category': category,
        'blogs': blogs,
        'categories': categories,
    })


def search(request):
    query = request.GET.get('s', '')
    blogs = Blog.objects.filter(
        title__icontains=query
    ) | Blog.objects.filter(
        short_description__icontains=query
    ) | Blog.objects.filter(
        long_description__icontains=query
    )
    blogs = blogs.select_related('author', 'category').distinct()
    categories = Category.objects.all()
    return render(request, 'blog/search-result.html', {
        'blogs': blogs,
        'categories': categories,
        'query': query,
    })


def contact(request):
    return render(request, 'blog/contact.html')
