from json import dumps

from apps.main.models import Lembaga
from apps.main.views.base import AdminRequiredMixin, CustomTemplateBaseMixin
from apps.services.apigateway import apigateway
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView


# =====================================================================================================
#                                               LOAD PAGE
# =====================================================================================================
class AdminLembagaListView(AdminRequiredMixin, CustomTemplateBaseMixin, ListView):
    model = Lembaga
    template_name = 'main/admin/lembaga/table.html'
    context_object_name = 'data_lembaga'

    def get_queryset(self):
        return self.model.objects.order_by('-id')


class AdminLembagaGenerateView(AdminRequiredMixin, View):
    def get(self, request):
        multilembaga = apigateway.getLembaga()

        if not multilembaga.get('status'):
            messages.error(request, 'Gagal mengambil data lembaga dari API Gateway.')
            return redirect('main:admin.lembaga.table')

        for lembaga in multilembaga.get('data', []):
            lembaga_obj, _ = Lembaga.objects.update_or_create(
                kode_lembaga=lembaga.get('uniid'),
                defaults={
                    'nama': lembaga.get('nama'),
                    'namasingkat': lembaga.get('namasingkat'),
                    'jenis_id': lembaga.get('jenis_id'),
                    'jenis': lembaga.get('jenis'),
                    'subjenis_id': lembaga.get('subjenis_id'),
                    'subjenis': lembaga.get('subjenis'),
                }
            )

            if superunit := Lembaga.objects.filter(kode_lembaga=lembaga.get('superunit')):
                superunit_obj = superunit.first()
                lembaga_obj.superunit = superunit_obj

            if lembaga.get('unitpendahulu'):
                unitpendahulu = []
                for unit in lembaga.get('unitpendahulu', []):
                    unitpendahulu.append(unit.get('uniid'))
                lembaga_obj.unitpendahulu = dumps(unitpendahulu)

            lembaga_obj.save()


        return redirect('main:admin.lembaga.table')
