from apps.main.models import Jabatan
from apps.main.views.base import AdminRequiredMixin, CustomTemplateBaseMixin
from apps.services.sihrd_sync import sync_jabatan
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
        is_success, _ = sync_jabatan()
        if not is_success:
            messages.error(request, 'Gagal mengambil data jabatan dari API Gateway.')

        return redirect('main:admin.jabatan.table')
