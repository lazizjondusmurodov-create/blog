from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='authors/', blank=True, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    title = models.CharField(max_length=150)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title


class Blog(models.Model):
    title = models.CharField(max_length=255)
    short_description = models.CharField(max_length=500)
    long_description = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='blogs'
    )
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name='blogs'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Image(models.Model):
    image = models.ImageField(upload_to='blog_images/')
    blog = models.ForeignKey(
        Blog, on_delete=models.CASCADE, related_name='images'
    )

    def __str__(self):
        return f'Image #{self.pk} - {self.blog.title}'



class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.blog.title}"

class ContactMessage(models.Model):
    """Aloqa sahifasidan yuborilgan xabar.

    Email jo'natish uchun SMTP sozlamasi kerak, shuning uchun xabar bazaga
    saqlanadi va admin panelda ko'riladi.
    """

    name = models.CharField('Ism', max_length=100)
    email = models.EmailField('Email')
    subject = models.CharField('Mavzu', max_length=200)
    message = models.TextField('Xabar')
    created_at = models.DateTimeField('Yuborilgan vaqt', auto_now_add=True)
    is_read = models.BooleanField("O'qilgan", default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Aloqa xabari'
        verbose_name_plural = 'Aloqa xabarlari'

    def __str__(self):
        return f'{self.name} — {self.subject}'
