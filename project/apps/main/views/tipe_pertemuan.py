from json import dumps

from apps.main.forms.tipe_pertemuan import TipePertemuanForm
from apps.main.models import TipePertemuan
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden
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
        context['select2']          = False
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
class AdminTipePertemuanListView(AdminRequiredMixin, CustomTemplateBaseMixin, ListView):
    model = TipePertemuan
    template_name = 'main/admin/tipe_pertemuan/table.html'
    context_object_name = 'data_tipe_pertemuan'

    def get_queryset(self):
        return self.model.objects.order_by('-id')


class AdminTipePertemuanCreateView(AdminRequiredMixin, CustomTemplateBaseMixin, CreateView):
    model = TipePertemuan
    template_name = 'main/admin/tipe_pertemuan/add.html'
    form_class = TipePertemuanForm
    success_url = reverse_lazy('main:admin.tipe_pertemuan.table')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Data tipe AIK berhasil dibuat!")
        return response


class AdminTipePertemuanUpdateView(AdminRequiredMixin, CustomTemplateBaseMixin, UpdateView):
    model = TipePertemuan
    template_name = 'main/admin/tipe_pertemuan/add.html'
    form_class = TipePertemuanForm
    success_url = reverse_lazy('main:admin.tipe_pertemuan.table')

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, id=self.kwargs.get('id'))

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Data tipe AIK berhasil diperbarui")
        return response


# =====================================================================================================
#                                                SERVICE
# =====================================================================================================
class AdminTipePertemuanDeleteListView(AdminRequiredMixin, View):
    def post(self, request):
        list_id = request.POST.getlist('list_id')

        if not list_id:
            messages.error(request, 'Invalid request!')
            return redirect('main:admin.tipe_pertemuan.table')

        try:
            with transaction.atomic():
                # delete sekaligus (lebih cepat & aman)
                deleted_count, _ = TipePertemuan.objects.filter(id__in=list_id).delete()

            if deleted_count > 0:
                messages.success(request, f'{deleted_count} data berhasil dihapus')
            else:
                messages.warning(request, 'Tidak ada data dipilih untuk dihapus')

        except Exception as e:
            messages.error(request, f'Terdapat kesalahan ketika menghapus data {str(e)}')

        return redirect('main:admin.tipe_pertemuan.table')
