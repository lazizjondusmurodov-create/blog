from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .throttles import LoginRateThrottle


class LoginView(ObtainAuthToken):
    """POST /api/auth/token/ — username + password evaziga token beradi.

    Javob: {"token": "...", "user_id": 1, "username": "..."}
    """

    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.get_username(),
        })


class LogoutView(APIView):
    """POST /api/auth/logout/ — tokenni o'chiradi.

    Shundan keyin eski token bilan kirib bo'lmaydi.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    """GET /api/auth/me/ — joriy foydalanuvchi ma'lumoti."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.pk,
            'username': user.get_username(),
            'email': user.email,
            'is_staff': user.is_staff,
        })
