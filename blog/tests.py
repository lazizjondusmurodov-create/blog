"""Sayt sahifalari uchun testlar (API testlari blog/api/tests.py da).

Ishga tushirish:  python manage.py test blog
"""
from django.test import TestCase
from django.urls import reverse

from .models import Author, Blog, Category, Comment, ContactMessage


class SiteTestData(TestCase):
    """Sahifa testlari uchun umumiy ma'lumot."""

    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(name='Diyorbek', bio='Dasturchi')
        cls.category = Category.objects.create(title='Texnologiya')
        cls.category2 = Category.objects.create(title='Sayohat')
        cls.blog = Blog.objects.create(
            title='Django bilan blog yaratish',
            short_description='Qisqacha tavsif',
            long_description='Batafsil matn',
            category=cls.category,
            author=cls.author,
        )


class PageTests(SiteTestData):
    """Har bir sahifa ochilishi va kerakli shablonni ishlatishi kerak."""

    def test_blog_list_page(self):
        r = self.client.get(reverse('blog_list'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'blog/blog.html')
        self.assertTemplateUsed(r, 'blog/base.html')
        self.assertContains(r, 'Django bilan blog yaratish')

    def test_blog_detail_page(self):
        r = self.client.get(reverse('blog_detail', args=[self.blog.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'blog/single.html')
        self.assertContains(r, 'Batafsil matn')

    def test_blog_detail_404(self):
        r = self.client.get(reverse('blog_detail', args=[999999]))
        self.assertEqual(r.status_code, 404)

    def test_category_page(self):
        r = self.client.get(reverse('category_detail', args=[self.category.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Texnologiya')

    def test_empty_category_shows_empty_state(self):
        r = self.client.get(reverse('category_detail', args=[self.category2.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'empty-state')

    def test_contact_page(self):
        r = self.client.get(reverse('contact'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'blog/contact.html')

    def test_footer_is_on_every_page(self):
        """base.html footer'i barcha sahifada bo'lishi kerak."""
        for name, args in [('blog_list', []), ('contact', []),
                           ('blog_detail', [self.blog.pk])]:
            with self.subTest(page=name):
                r = self.client.get(reverse(name, args=args))
                self.assertContains(r, 'Barcha huquqlar himoyalangan')


class SearchTests(SiteTestData):

    def test_search_finds_by_title(self):
        r = self.client.get(reverse('search'), {'s': 'Django'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Django bilan blog yaratish')

    def test_search_finds_by_long_description(self):
        r = self.client.get(reverse('search'), {'s': 'Batafsil'})
        self.assertContains(r, 'Django bilan blog yaratish')

    def test_search_with_no_results(self):
        r = self.client.get(reverse('search'), {'s': 'zzzqwerty'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'empty-state')

    def test_empty_search_returns_nothing(self):
        """Bo'sh so'rov barcha bloglarni qaytarmasligi kerak."""
        r = self.client.get(reverse('search'), {'s': ''})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context['blogs']), 0)

    def test_search_query_is_kept_in_input(self):
        r = self.client.get(reverse('search'), {'s': 'Django'})
        self.assertContains(r, 'value="Django"')


class CommentPostTests(SiteTestData):
    """Blog sahifasidagi izoh formasi."""

    def test_valid_comment_is_saved(self):
        r = self.client.post(
            reverse('blog_detail', args=[self.blog.pk]),
            {'name': 'Lazizjon', 'email': 'test@example.com',
             'text': 'Zo\'r maqola'},
        )
        self.assertEqual(r.status_code, 302)  # POST-Redirect-GET
        self.assertTrue(Comment.objects.filter(name='Lazizjon').exists())

    def test_incomplete_comment_is_rejected(self):
        r = self.client.post(
            reverse('blog_detail', args=[self.blog.pk]),
            {'name': 'Lazizjon', 'email': '', 'text': ''},
        )
        self.assertEqual(r.status_code, 200)  # redirect emas
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_appears_on_page(self):
        Comment.objects.create(
            blog=self.blog, name='Sharhchi',
            email='a@b.com', text='Ajoyib',
        )
        r = self.client.get(reverse('blog_detail', args=[self.blog.pk]))
        self.assertContains(r, 'Sharhchi')
        self.assertContains(r, 'Ajoyib')


class ContactFormTests(SiteTestData):
    """Aloqa formasi — xabar bazaga saqlanadi."""

    VALID = {
        'name': 'Lazizjon',
        'email': 'test@example.com',
        'subject': 'Hamkorlik taklifi',
        'message': 'Salom, siz bilan hamkorlik qilmoqchiman.',
        'website': '',  # honeypot bo'sh
    }

    def test_valid_message_is_saved(self):
        r = self.client.post(reverse('contact'), self.VALID)
        self.assertEqual(r.status_code, 302)  # POST-Redirect-GET
        self.assertEqual(ContactMessage.objects.count(), 1)

        msg = ContactMessage.objects.first()
        self.assertEqual(msg.name, 'Lazizjon')
        self.assertEqual(msg.subject, 'Hamkorlik taklifi')
        self.assertFalse(msg.is_read)

    def test_success_message_is_shown_after_redirect(self):
        r = self.client.post(reverse('contact'), self.VALID, follow=True)
        self.assertContains(r, 'Xabaringiz yuborildi')

    def test_invalid_email_is_rejected(self):
        data = {**self.VALID, 'email': 'notanemail'}
        r = self.client.post(reverse('contact'), data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertContains(r, 'field-error')

    def test_short_message_is_rejected(self):
        data = {**self.VALID, 'message': 'qisqa'}
        r = self.client.post(reverse('contact'), data)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertContains(r, 'kamida 10 ta belgi')

    def test_short_name_is_rejected(self):
        data = {**self.VALID, 'name': 'A'}
        self.client.post(reverse('contact'), data)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_empty_fields_are_rejected(self):
        r = self.client.post(reverse('contact'), {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_honeypot_blocks_bot(self):
        """'website' maydonini faqat bot to'ldiradi — xabar saqlanmaydi."""
        data = {**self.VALID, 'website': 'http://spam.example.com'}
        r = self.client.post(reverse('contact'), data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_honeypot_field_is_hidden_from_users(self):
        r = self.client.get(reverse('contact'))
        self.assertContains(r, 'honeypot')

    def test_whitespace_is_stripped(self):
        data = {**self.VALID, 'name': '  Lazizjon  '}
        self.client.post(reverse('contact'), data)
        self.assertEqual(ContactMessage.objects.first().name, 'Lazizjon')

    def test_form_data_survives_validation_error(self):
        """Xato bo'lsa foydalanuvchi yozganlari yo'qolmasligi kerak."""
        data = {**self.VALID, 'email': 'notanemail'}
        r = self.client.post(reverse('contact'), data)
        self.assertContains(r, 'Hamkorlik taklifi')


class QueryCountTests(SiteTestData):
    """Shablondagi N+1 qaytib kelmasligi uchun qo'riqchi."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Ko'proq blog qo'shamiz — so'rov soni shunga bog'liq bo'lmasligi kerak
        for i in range(5):
            Blog.objects.create(
                title=f'Maqola {i}', short_description='q',
                long_description='u', category=cls.category,
                author=cls.author,
            )

    def test_blog_list_query_count_is_flat(self):
        with self.assertNumQueries(6):
            self.client.get(reverse('blog_list'))

        for i in range(5):
            Blog.objects.create(
                title=f'Yana {i}', short_description='q',
                long_description='u', category=self.category,
                author=self.author,
            )

        # Blog soni ikki barobar oshdi — so'rov soni o'zgarmasligi kerak
        with self.assertNumQueries(6):
            self.client.get(reverse('blog_list'))
