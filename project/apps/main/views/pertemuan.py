from json import dumps

from apps.main.forms.pertemuan import PertemuanForm
from apps.main.models import Pertemuan, TipePertemuan
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.db import transaction
from django.db.models import CharField, F, Value
from django.db.models.functions import Concat
from django.http import HttpResponse, HttpResponseForbidden
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (CreateView, DeleteView, ListView,
                                  TemplateView, UpdateView)


# =====================================================================================================
#                                               MIXINS
# =====================================================================================================
def in_grup(user, grup_name):
    if user:
        return user.groups.filter(name=grup_name).count() > 0
    return False


class AdminRequiredMixin(AccessMixin):
    """Mixin untuk membatasi akses hanya untuk grup personalia."""
    def dispatch(self, request, *args, **kwargs):
        if not in_grup(request.user, 'admin'):
            return HttpResponseForbidden("Anda tidak memiliki hak akses.")
        return super().dispatch(request, *args, **kwargs)


class CustomTemplateBaseMixin(LoginRequiredMixin):
    """Mixin dasar untuk semua view"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        return context


# =====================================================================================================
#                                               LOAD PAGE
# =====================================================================================================
class AdminPertemuanListView(AdminRequiredMixin, CustomTemplateBaseMixin, TemplateView):
    # model = Pertemuan
    template_name = 'main/admin/pertemuan/table.html'
    # context_object_name = 'data_pertemuan'

    # def get_queryset(self):
    #     return self.model.objects.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ===[Select CSS and JS Files]===
        context['data_tipe_pertemuan'] = TipePertemuan.objects.all()
        context['data_tahun_pertemuan'] = Pertemuan.objects.values_list('created_at__year', flat=True).distinct().order_by('-created_at__year')
        context['tipe_pertemuan'] = int(self.request.GET.get('tipe_pertemuan', 1))
        context['tahun_pertemuan'] = context['data_tahun_pertemuan'][0] if context['data_tahun_pertemuan'] else ''
        return context


class AdminPertemuanCreateView(AdminRequiredMixin, CustomTemplateBaseMixin, CreateView):
    model = Pertemuan
    template_name = 'main/admin/pertemuan/add.html'
    form_class = PertemuanForm

    def get_success_url(self):
        tipe_id = self.object.tipe_pertemuan.id
        return reverse_lazy('main:admin.pertemuan.table') + f'?tipe_pertemuan={tipe_id}'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Data AIK berhasil dibuat!")
        return response


class AdminPertemuanUpdateView(AdminRequiredMixin, CustomTemplateBaseMixin, UpdateView):
    model = Pertemuan
    template_name = 'main/admin/pertemuan/add.html'
    form_class = PertemuanForm

    def get_success_url(self):
        tipe_id = self.object.tipe_pertemuan.id
        return reverse_lazy('main:admin.pertemuan.table') + f'?tipe_pertemuan={tipe_id}'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, id=self.kwargs.get('id'))

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Data AIK berhasil diperbarui")
        return response


# =====================================================================================================
#                                                SERVICE
# =====================================================================================================
class AdminPertemuanDeleteListView(AdminRequiredMixin, View):
    def post(self, request):
        list_id = request.POST.getlist('list_id')

        if not list_id:
            messages.error(request, 'Invalid request!')
            return redirect('main:admin.pertemuan.table')

        try:
            with transaction.atomic():
                # delete sekaligus (lebih cepat & aman)
                deleted_count, _ = Pertemuan.objects.filter(id__in=list_id).delete()

            if deleted_count > 0:
                messages.success(request, f'{deleted_count} data berhasil dihapus')
            else:
                messages.warning(request, 'Tidak ada data dipilih untuk dihapus')

        except Exception as e:
            messages.error(request, f'Terdapat kesalahan ketika menghapus data {str(e)}')

        return redirect('main:admin.pertemuan.table')


class AdminPertemuanListJsonView(AdminRequiredMixin, View):
    def post(self, request):
        # ------------------------------------------------------------------
        # Queryset dengan filter
        # ------------------------------------------------------------------
        queryset = Pertemuan.objects.all().order_by('-id')
        # filter tipe pertemuan
        if tipe_pertemuan_id := request.POST.get('tipe_pertemuan'):
            queryset = queryset.filter(tipe_pertemuan__id=tipe_pertemuan_id)
        # filter tahun
        if tahun_pertemuan := request.POST.get('tahun_pertemuan'):
            queryset = queryset.filter(created_at__year=tahun_pertemuan)

        queryset = queryset.annotate(
            materi_url=Concat(
                Value(settings.MEDIA_URL),
                F('materi'),
                output_field=CharField()
            )
        )
        # ------------------------------------------------------------------
        # Output JSON
        # ------------------------------------------------------------------
        data = queryset.values(
            'id',
            'tipe_pertemuan__id',
            'tipe_pertemuan__nama',
            'judul',
            'deskripsi',   # ← Full name user utama
            'pembicara',
            'mulai',  # ← Full name dari latest state detail
            'akhir',
            'presensi_mulai',
            'presensi_akhir',
            'tautan',
            'materi',
            'materi_url',
            'created_at',
            'updated_at'
        )

        return JsonResponse(list(data), safe=False)
