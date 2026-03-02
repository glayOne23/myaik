from django.urls import include, path

from .v1.views import presensi


urlpatterns = [
    path('v1/', include([
        path('presensi/user/<str:username>/', presensi.PresensiUserListAPIView.as_view()),
        path('presensi/user/<str:username>/total', presensi.PresensiUserTotalListAPIView.as_view()),
    ])),
]
