from json import dumps

from apps.main.models import Jabatan, Lembaga
from apps.main.views.base import AdminRequiredMixin, CustomTemplateBaseMixin
from apps.services.apigateway import apigateway
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView


# =====================================================================================================
#                                               LOAD PAGE
# =====================================================================================================
class AdminJabatanListView(AdminRequiredMixin, CustomTemplateBaseMixin, ListView):
    model = Jabatan
    template_name = 'main/admin/jabatan/table.html'
    context_object_name = 'data_jabatan'

    def get_queryset(self):
        return self.model.objects.order_by('-id')


class AdminJabatanGenerateView(AdminRequiredMixin, View):
    def get(self, request):
        multijabatan = apigateway.getJabatan()

        if not multijabatan.get('status'):
            messages.error(request, 'Gagal mengambil data jabatan dari API Gateway.')
            return redirect('main:admin.jabatan.table')

        for jabatan in multijabatan.get('data', []):
            jabatan_obj, _ = Jabatan.objects.update_or_create(
                kode_jabatan=jabatan.get('kode_jabatan'),
                defaults={
                    'nama': jabatan.get('nama'),
                    'eselon': jabatan.get('eselon'),
                    'sks': jabatan.get('sks'),
                    'uniid_penjabat': jabatan.get('uniid_penjabat'),
                }
            )

            if unit := Lembaga.objects.filter(kode_lembaga=jabatan.get('kode_lembaga')):
                unit_obj = unit.first()
                jabatan_obj.unit = unit_obj
                jabatan_obj.save()


        return redirect('main:admin.jabatan.table')
