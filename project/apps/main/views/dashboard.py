from json import dumps

from apps.main.models import Jabatan, Lembaga, Pertemuan
from apps.main.views.base import STATUS_KEAKTIFAN_DEFAULT, STATUS_KEAKTIFAN_SEMUA
from apps.services.decorators import group_required, login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Q


# =====================================================================================================
#                                               LOAD PAGE
# =====================================================================================================
@login_required
def index(request):
    context = {}
    # ===[Select CSS and JS Files]===
    context['datatables']       = True
    context['select2']          = True
    context['summernote']       = False
    context['maxlength']        = False
    context['inputmask']        = False
    context['duallistbox']      = False
    context['moment']           = False
    context['daterange']        = False
    context['chartjs']          = False
    context['chartjsv4']          = True

    # data
    user = request.user
    datajabatan = Jabatan.objects.filter(uniid_penjabat=user.username).values_list('unit__id', flat=True)

    # Base filter karyawan aktif & bukan DTT
    base_karyawan_qs = (
        User.objects
        .filter(
            profile__home_id__isnull=False,
            profile__status="Aktif"
        )
        .exclude(profile__kepegawaian="Dosen Tidak Tetap")
    )

    # Pilihan status keaktifan (hanya untuk admin & pejabat, user biasa hanya melihat datanya sendiri)
    data_status_keaktifan = (
        User.objects
        .filter(profile__home_id__isnull=False)
        .exclude(profile__kepegawaian="Dosen Tidak Tetap")
        .exclude(profile__status__isnull=True)
        .exclude(profile__status='')
        .order_by('profile__status')
        .values_list('profile__status', flat=True)
        .distinct()
    )
    context['status_keaktifan_default'] = STATUS_KEAKTIFAN_DEFAULT
    context['status_keaktifan_semua'] = STATUS_KEAKTIFAN_SEMUA

    context['data_tahun_pertemuan'] = Pertemuan.objects.values_list('mulai__year', flat=True).distinct().order_by('-mulai__year')
    if user.groups.filter(name='admin').exists():
        context['data_status_keaktifan'] = data_status_keaktifan
        context['datalembaga'] = Lembaga.objects.all()
        context['datalembaga_pie'] = Lembaga.objects.filter(jenis_id__in=[1, 3]).order_by('nama')
        context['datakaryawan'] = (
            base_karyawan_qs
            .distinct()
        )
    elif datajabatan:
        home_id = user.profile.home_id
        context['data_status_keaktifan'] = data_status_keaktifan
        context['datalembaga'] = Lembaga.objects.filter(
            Q(id__in=datajabatan) | Q(superunit__id__in=datajabatan) | Q(kode_lembaga=home_id)
        ).distinct()
        context['datalembaga_pie'] = context['datalembaga'].filter(jenis_id__in=[1, 3]).order_by('nama')
        context['user_home_id'] = home_id
        context['datakaryawan'] = (
            base_karyawan_qs
            .filter(profile__home_id=home_id)
            .distinct()
        )
    else:
        context['datalembaga'] = Lembaga.objects.filter(kode_lembaga=user.profile.home_id).distinct()
        context['datalembaga_pie'] = Lembaga.objects.filter(
            Q(kode_lembaga=user.profile.home_id) | Q(superunit__kode_lembaga=user.profile.home_id),
            jenis_id__in=[1, 3]
        ).order_by('nama').distinct()
        context['datakaryawan'] = User.objects.filter(username=request.user.username)


    # ===[Render Template]===
    return render(request, 'main/index.html', context)
