"""blog.api uchun testlar.

Django test runner alohida test bazasi yaratadi — haqiqiy db.sqlite3 ga tegmaydi.
Ishga tushirish:  python manage.py test blog.api
"""
from datetime import timedelta

from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from blog.api.throttles import CommentBurstThrottle, LoginRateThrottle
from blog.models import Author, Blog, Category, Comment


class ApiTestData(APITestCase):
    """Barcha testlar uchun umumiy boshlang'ich ma'lumot."""

    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(name='Diyorbek', bio='Dasturchi')
        cls.author2 = Author.objects.create(name='Ali Valiyev', bio='Muharrir')
        cls.category = Category.objects.create(title='Texnologiya')
        cls.category2 = Category.objects.create(title='Sayohat')

        cls.blog = Blog.objects.create(
            title='Django bilan blog yaratish',
            short_description='Qisqacha tavsif',
            long_description='Batafsil matn',
            category=cls.category,
            author=cls.author,
        )
        cls.blog2 = Blog.objects.create(
            title='Fotografiya sirlari',
            short_description='Kamera haqida',
            long_description='Uzun matn',
            category=cls.category2,
            author=cls.author2,
        )
        cls.comment = Comment.objects.create(
            blog=cls.blog, name='Lazizjon',
            email='test@example.com', text='Zo\'r maqola',
        )

        cls.user = User.objects.create_user('tester', password='parol12345')
        cls.token = Token.objects.create(user=cls.user)


class ReadEndpointTests(ApiTestData):
    """Anonim foydalanuvchi hamma narsani o'qiy oladi."""

    def test_api_root_lists_all_routes(self):
        r = self.client.get('/api/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        for route in ('blogs', 'categories', 'authors', 'comments', 'images'):
            self.assertIn(route, r.data)

    def test_blog_list_is_paginated(self):
        r = self.client.get('/api/blogs/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['count'], 2)
        self.assertIn('results', r.data)

    def test_blog_list_uses_light_serializer(self):
        """Ro'yxatda long_description bo'lmasligi kerak."""
        r = self.client.get('/api/blogs/')
        row = r.data['results'][0]
        self.assertIn('short_description', row)
        self.assertNotIn('long_description', row)
        self.assertIn('comments_count', row)

    def test_blog_detail_is_nested(self):
        r = self.client.get(f'/api/blogs/{self.blog.pk}/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('long_description', r.data)
        # category va author ichma-ich obyekt bo'lib kelishi kerak
        self.assertEqual(r.data['category']['title'], 'Texnologiya')
        self.assertEqual(r.data['author']['name'], 'Diyorbek')
        self.assertEqual(len(r.data['comments']), 1)

    def test_blog_detail_404_for_missing_id(self):
        r = self.client.get('/api/blogs/999999/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_blog_comments_action(self):
        r = self.client.get(f'/api/blogs/{self.blog.pk}/comments/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data[0]['text'], 'Zo\'r maqola')

    def test_other_list_endpoints_ok(self):
        for url in ('/api/categories/', '/api/authors/',
                    '/api/comments/', '/api/images/'):
            with self.subTest(url=url):
                self.assertEqual(
                    self.client.get(url).status_code, status.HTTP_200_OK
                )


class BlogsCountTests(ApiTestData):
    """blogs_count — N+1 tuzatishdan keyin ham to'g'ri ishlashi kerak."""

    def test_author_list_has_blogs_count(self):
        r = self.client.get('/api/authors/')
        by_name = {a['name']: a for a in r.data['results']}
        self.assertEqual(by_name['Diyorbek']['blogs_count'], 1)

    def test_category_list_has_blogs_count(self):
        r = self.client.get('/api/categories/')
        by_title = {c['title']: c for c in r.data['results']}
        self.assertEqual(by_title['Texnologiya']['blogs_count'], 1)

    def test_nested_author_keeps_blogs_count(self):
        """Regressiya testi: ichma-ich author'da ham maydon yo'qolmasin."""
        r = self.client.get(f'/api/blogs/{self.blog.pk}/')
        self.assertEqual(r.data['author']['blogs_count'], 1)
        self.assertEqual(r.data['category']['blogs_count'], 1)

    def test_author_list_has_no_n_plus_one(self):
        """Muallif sonidan qat'i nazar so'rovlar soni o'zgarmasligi kerak."""
        with self.assertNumQueries(2):  # COUNT (pagination) + asosiy so'rov
            self.client.get('/api/authors/')

        Author.objects.create(name='Yangi muallif 1')
        Author.objects.create(name='Yangi muallif 2')

        with self.assertNumQueries(2):
            self.client.get('/api/authors/')

    def test_category_list_has_no_n_plus_one(self):
        with self.assertNumQueries(2):
            self.client.get('/api/categories/')


class FilterSearchOrderingTests(ApiTestData):

    def test_filter_blogs_by_category(self):
        r = self.client.get(f'/api/blogs/?category={self.category.pk}')
        self.assertEqual(r.data['count'], 1)
        self.assertEqual(r.data['results'][0]['title'],
                         'Django bilan blog yaratish')

    def test_filter_blogs_by_author(self):
        r = self.client.get(f'/api/blogs/?author={self.author2.pk}')
        self.assertEqual(r.data['count'], 1)

    def test_invalid_filter_value_returns_400(self):
        r = self.client.get('/api/blogs/?category=notanumber')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_blogs(self):
        r = self.client.get('/api/blogs/?search=Fotografiya')
        self.assertEqual(r.data['count'], 1)
        self.assertEqual(r.data['results'][0]['title'], 'Fotografiya sirlari')

    def test_ordering_by_title(self):
        r = self.client.get('/api/blogs/?ordering=title')
        titles = [b['title'] for b in r.data['results']]
        self.assertEqual(titles, sorted(titles))

    def test_ordering_by_blogs_count(self):
        """blogs_count ordering_fields ga qo'shilgani uchun ishlashi kerak."""
        r = self.client.get('/api/authors/?ordering=-blogs_count')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_default_ordering_is_newest_first(self):
        # created_at auto_now_add bo'lgani uchun ikkala blog ham bir xil
        # vaqtda yaratiladi — tartibni sinash uchun vaqtni aniq belgilaymiz.
        old = timezone.now() - timedelta(days=2)
        new = timezone.now() - timedelta(days=1)
        Blog.objects.filter(pk=self.blog.pk).update(created_at=old)
        Blog.objects.filter(pk=self.blog2.pk).update(created_at=new)

        r = self.client.get('/api/blogs/')
        ids = [b['id'] for b in r.data['results']]
        self.assertEqual(ids, [self.blog2.pk, self.blog.pk])

    def test_filter_comments_by_blog(self):
        r = self.client.get(f'/api/comments/?blog={self.blog.pk}')
        self.assertEqual(r.data['count'], 1)


class PermissionTests(ApiTestData):
    """IsAuthenticatedOrReadOnly + izohlar uchun AllowAny."""

    def test_anonymous_cannot_create_blog(self):
        r = self.client.post('/api/blogs/', {
            'title': 'Ruxsatsiz blog', 'short_description': 'q',
            'long_description': 'u', 'category': self.category.pk,
            'author': self.author.pk,
        }, format='json')
        self.assertIn(r.status_code, (status.HTTP_401_UNAUTHORIZED,
                                      status.HTTP_403_FORBIDDEN))
        self.assertFalse(Blog.objects.filter(title='Ruxsatsiz blog').exists())

    def test_anonymous_can_create_comment(self):
        r = self.client.post('/api/comments/', {
            'blog': self.blog.pk, 'name': 'Mehmon',
            'email': 'mehmon@example.com', 'text': 'Rahmat!',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Comment.objects.filter(name='Mehmon').exists())

    def test_anonymous_cannot_delete_blog(self):
        r = self.client.delete(f'/api/blogs/{self.blog.pk}/')
        self.assertIn(r.status_code, (status.HTTP_401_UNAUTHORIZED,
                                      status.HTTP_403_FORBIDDEN))
        self.assertTrue(Blog.objects.filter(pk=self.blog.pk).exists())


class TokenAuthTests(ApiTestData):
    """rest_framework.authtoken o'rnatilmagani sabab bo'lgan 500 xatosi.

    Bu testlar authtoken INSTALLED_APPS dan olib tashlansa darrov yiqiladi.
    """

    def test_invalid_token_returns_401_not_500(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token notarealtoken')
        r = self.client.post('/api/blogs/', {}, format='json')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_valid_token_can_create_blog(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        r = self.client.post('/api/blogs/', {
            'title': 'Token orqali yaratilgan',
            'short_description': 'q', 'long_description': 'u',
            'category': self.category.pk, 'author': self.author.pk,
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_token_model_is_usable(self):
        self.assertEqual(Token.objects.filter(user=self.user).count(), 1)


class WriteTests(ApiTestData):
    """Autentifikatsiyadan o'tgan foydalanuvchi uchun to'liq CRUD."""

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_create_blog(self):
        r = self.client.post('/api/blogs/', {
            'title': 'Yangi maqola sarlavhasi',
            'short_description': 'qisqa', 'long_description': 'uzun',
            'category': self.category.pk, 'author': self.author.pk,
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Blog.objects.count(), 3)

    def test_create_blog_uses_write_serializer(self):
        """Yozishda category id bo'lib qaytadi, ichma-ich obyekt emas."""
        r = self.client.post('/api/blogs/', {
            'title': 'Yana bir sarlavha',
            'short_description': 'q', 'long_description': 'u',
            'category': self.category.pk, 'author': self.author.pk,
        }, format='json')
        self.assertEqual(r.data['category'], self.category.pk)

    def test_short_title_is_rejected(self):
        r = self.client.post('/api/blogs/', {
            'title': 'abc', 'short_description': 'q', 'long_description': 'u',
            'category': self.category.pk, 'author': self.author.pk,
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', r.data)

    def test_whitespace_only_title_is_rejected(self):
        """'     ' — strip() dan keyin 5 belgidan kam."""
        r = self.client.post('/api/blogs/', {
            'title': '        ', 'short_description': 'q',
            'long_description': 'u', 'category': self.category.pk,
            'author': self.author.pk,
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update(self):
        r = self.client.patch(f'/api/blogs/{self.blog.pk}/',
                              {'title': 'Yangilangan sarlavha'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.title, 'Yangilangan sarlavha')

    def test_delete_blog(self):
        r = self.client.delete(f'/api/blogs/{self.blog.pk}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Blog.objects.filter(pk=self.blog.pk).exists())

    def test_comment_requires_all_fields(self):
        r = self.client.post('/api/comments/', {'blog': self.blog.pk},
                             format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ('name', 'email', 'text'):
            self.assertIn(field, r.data)

    def test_comment_rejects_invalid_email(self):
        r = self.client.post('/api/comments/', {
            'blog': self.blog.pk, 'name': 'X',
            'email': 'notanemail', 'text': 'salom',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', r.data)

    def test_created_at_is_read_only(self):
        r = self.client.post('/api/comments/', {
            'blog': self.blog.pk, 'name': 'X', 'email': 'x@example.com',
            'text': 'salom', 'created_at': '1999-01-01T00:00:00Z',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(r.data['created_at'][:4], '1999')


class AuthEndpointTests(ApiTestData):
    """/api/auth/ — token olish, o'chirish, joriy foydalanuvchi."""

    def setUp(self):
        # DRF chegarani keshda saqlaydi — testlar bir-biriga ta'sir qilmasin.
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_obtain_token_with_valid_credentials(self):
        r = self.client.post('/api/auth/token/', {
            'username': 'tester', 'password': 'parol12345',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['token'], self.token.key)
        self.assertEqual(r.data['username'], 'tester')
        self.assertEqual(r.data['user_id'], self.user.pk)

    def test_obtain_token_with_wrong_password(self):
        r = self.client.post('/api/auth/token/', {
            'username': 'tester', 'password': 'notarealpassword',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', r.data)

    def test_token_from_endpoint_actually_works(self):
        """Olingan token bilan haqiqatan blog yaratib bo'lishi kerak."""
        r = self.client.post('/api/auth/token/', {
            'username': 'tester', 'password': 'parol12345',
        }, format='json')
        key = r.data['token']

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {key}')
        r = self.client.post('/api/blogs/', {
            'title': 'Token endpointi orqali',
            'short_description': 'q', 'long_description': 'u',
            'category': self.category.pk, 'author': self.author.pk,
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_new_user_gets_token_created(self):
        """Tokeni yo'q foydalanuvchi ham token ola bilishi kerak."""
        User.objects.create_user('yangi', password='parol12345')
        self.assertFalse(Token.objects.filter(user__username='yangi').exists())

        r = self.client.post('/api/auth/token/', {
            'username': 'yangi', 'password': 'parol12345',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertTrue(Token.objects.filter(user__username='yangi').exists())

    def test_me_requires_authentication(self):
        r = self.client.get('/api/auth/me/')
        self.assertIn(r.status_code, (status.HTTP_401_UNAUTHORIZED,
                                      status.HTTP_403_FORBIDDEN))

    def test_me_returns_current_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        r = self.client.get('/api/auth/me/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['username'], 'tester')

    def test_logout_deletes_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        r = self.client.post('/api/auth/logout/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

        # Eski token endi ishlamasligi kerak
        r = self.client.get('/api/auth/me/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)


class ThrottleTests(ApiTestData):
    """Spamga qarshi chegaralar.

    DRF throttle tezligini klass yaratilganda bir marta o'qiydi, shuning uchun
    override_settings ish bermaydi — rate'ni to'g'ridan-to'g'ri patch qilamiz.
    """

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def _post_comment(self):
        return self.client.post('/api/comments/', {
            'blog': self.blog.pk, 'name': 'Spam',
            'email': 'spam@example.com', 'text': 'xabar',
        }, format='json')

    def test_comment_spam_is_blocked(self):
        """Chegaradan oshgan izoh 429 qaytarishi kerak."""
        with patch.object(CommentBurstThrottle, 'rate', '3/hour', create=True):
            for i in range(3):
                self.assertEqual(self._post_comment().status_code,
                                 status.HTTP_201_CREATED, f'{i + 1}-izoh')

            r = self._post_comment()

        self.assertEqual(r.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(Comment.objects.filter(name='Spam').count(), 3)

    def test_reading_comments_is_not_throttled(self):
        """Yozish chegarasi o'qishga ta'sir qilmasligi kerak."""
        with patch.object(CommentBurstThrottle, 'rate', '1/hour', create=True):
            self._post_comment()  # chegarani tugatamiz
            self.assertEqual(self._post_comment().status_code,
                             status.HTTP_429_TOO_MANY_REQUESTS)

            for _ in range(5):
                self.assertEqual(self.client.get('/api/comments/').status_code,
                                 status.HTTP_200_OK)

    def test_login_bruteforce_is_blocked(self):
        """Parol tanlashga urinish chegaralanadi."""
        with patch.object(LoginRateThrottle, 'rate', '2/min', create=True):
            for _ in range(2):
                self.client.post('/api/auth/token/', {
                    'username': 'tester', 'password': 'wrong',
                }, format='json')

            r = self.client.post('/api/auth/token/', {
                'username': 'tester', 'password': 'wrong',
            }, format='json')

        self.assertEqual(r.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_normal_usage_is_not_throttled(self):
        """Oddiy foydalanuvchi chegaraga urilmasligi kerak."""
        self.assertEqual(self._post_comment().status_code,
                         status.HTTP_201_CREATED)
        r = self.client.post('/api/auth/token/', {
            'username': 'tester', 'password': 'parol12345',
        }, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
