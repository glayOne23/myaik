from apps.main.models import Lembaga
from apps.main.views.base import AdminRequiredMixin, CustomTemplateBaseMixin
from apps.services.sihrd_sync import sync_lembaga
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
        is_success, _ = sync_lembaga()
        if not is_success:
            messages.error(request, 'Gagal mengambil data lembaga dari API Gateway.')

        return redirect('main:admin.lembaga.table')
