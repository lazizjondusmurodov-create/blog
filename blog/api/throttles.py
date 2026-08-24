from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle


class CommentBurstThrottle(AnonRateThrottle):
    """Izoh yozish uchun alohida chegara (settings: 'comment').

    Faqat yozishga ta'sir qiladi — izohlarni o'qish cheklanmaydi.
    """

    scope = 'comment'


class LoginRateThrottle(SimpleRateThrottle):
    """Token olish uchun chegara — parol tanlab ko'rishga qarshi.

    Anonim so'rov bo'lgani uchun IP bo'yicha hisoblanadi.
    """

    scope = 'login'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }
