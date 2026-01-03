from json import dumps

from apps.main.models import Jabatan, Lembaga, Pertemuan
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
    context['datatables']       = False
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

    context['data_tahun_pertemuan'] = Pertemuan.objects.values_list('mulai__year', flat=True).distinct().order_by('-mulai__year')
    if user.groups.filter(name='admin').exists():
        context['datalembaga'] = Lembaga.objects.all()
        context['datakaryawan'] = User.objects.all().filter(profile__home_id__isnull=False)
    elif datajabatan:
        context['datalembaga'] = Lembaga.objects.filter(Q(id__in=datajabatan) | Q(superunit__id__in=datajabatan)).distinct()
        datakodelembaga = context['datalembaga'].values_list('kode_lembaga', flat=True)
        context['datakaryawan'] = User.objects.filter(Q(profile__home_id__in=datakodelembaga) | Q(username=request.user.username)).distinct()
    else:
        context['datalembaga'] = Lembaga.objects.filter(kode_lembaga=user.profile.home_id).distinct()
        context['datakaryawan'] = User.objects.filter(username=request.user.username)


    # ===[Render Template]===
    return render(request, 'main/index.html', context)
