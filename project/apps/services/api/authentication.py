import jwt
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission


class GatewayJWTAuthentication(BaseAuthentication):
    """
    Validasi token JWT dari API Gateway (RS256).
    Kirim header: Authorization: Bearer <access_token>
    """

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ', 1)[1]
        try:
            with open(settings.API_GATEWAY_KEY, 'r') as f:
                public_key = f.read()

            payload = jwt.decode(
                token,
                key=public_key,
                algorithms=settings.API_GATEWAY_ALGO,
                options={"verify_signature": settings.API_GATEWAY_VERIFY},
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token sudah kadaluarsa.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Token tidak valid.')

        username = payload.get('username')
        if not username:
            raise AuthenticationFailed('Token tidak mengandung username.')

        user, _ = User.objects.get_or_create(username=username)
        return (user, payload)


class IsSelfOrAdmin(BasePermission):
    """
    Izinkan akses jika username di URL sama dengan user yang login,
    atau jika user adalah staff/admin.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        url_username = view.kwargs.get('username', '')
        return request.user.username == url_username
