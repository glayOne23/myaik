from apps.main.api.v1.serializers.presensi import (PresensiSerializer,
                                                   PresensiTotalSerializer)
from apps.main.models import Pertemuan, Presensi, TipePertemuan
from apps.services.api.view import (CustomListAPIView, CustomListCreateAPIView,
                                    CustomRetrieveAPIView,
                                    CustomRetrieveDestroyAPIView,
                                    CustomRetrieveUpdateAPIView,
                                    CustomRetrieveUpdateDestroyAPIView)
from django.db.models import Count, ExpressionWrapper, F, FloatField, Q
from django.db.models.functions import Coalesce
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.permissions import IsAuthenticated


class PresensiUserListAPIView(CustomListCreateAPIView):
    queryset = Presensi.objects.all().order_by('-id')
    serializer_class = PresensiSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        self.queryset = Presensi.objects.filter(peserta__username=username).order_by('-id')

        if tahun := request.GET.get('tahun'):
            self.queryset = self.queryset.filter(pertemuan__mulai__year=tahun)

        if tipe_pertemuan := request.GET.get('tipe_pertemuan'):
            self.queryset = self.queryset.filter(pertemuan__tipe_pertemuan__nama=tipe_pertemuan)

        # paginasi queryset
        return self.list(request)


class PresensiUserTotalListAPIView(CustomListCreateAPIView):
    queryset = Presensi.objects.all().order_by('-id')
    serializer_class = PresensiTotalSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        tahun = request.GET.get('tahun')

        # Filter untuk total presensi user
        presensi_filter = Q(pertemuan__presensi__peserta__username=username)

        # Filter untuk tahun (berlaku ke semua perhitungan)
        pertemuan_filter = Q()
        if tahun:
            pertemuan_filter &= Q(pertemuan__mulai__year=tahun)
            presensi_filter &= Q(pertemuan__mulai__year=tahun)

        self.queryset = (
            TipePertemuan.objects
            .annotate(
                # Total semua pertemuan per tipe
                total_pertemuan=Count(
                    'pertemuan',
                    filter=pertemuan_filter,
                    distinct=True
                ),

                # Total presensi user
                total_presensi=Count(
                    'pertemuan__presensi',
                    filter=presensi_filter,
                    distinct=True
                ),
            )
            .annotate(
                # Hitung persentase
                persentasi=Coalesce(
                    ExpressionWrapper(
                        F('total_presensi') * 100.0 / F('total_pertemuan'),
                        output_field=FloatField()
                    ),
                    0.0
                )
            )
            .order_by('id')
        )

        return self.list(request)
