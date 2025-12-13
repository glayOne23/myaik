from functools import wraps

from apps.main.forms.presensi import PresensiForm
from apps.main.models import Pertemuan, Presensi, TipePertemuan
from apps.main.views.base import AdminRequiredMixin, CustomTemplateBaseMixin
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import CharField, Count, F, Q, Value
from django.db.models.functions import Concat
from django.http import HttpResponse, HttpResponseForbidden
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (CreateView, DeleteView, FormView, ListView,
                                  TemplateView, UpdateView)


# =====================================================================================================
#                                              ADMIN LOAD PAGE
# =====================================================================================================
class AdminPresensiListView(AdminRequiredMixin, CustomTemplateBaseMixin, ListView):
    model = Presensi
    template_name = "main/admin/presensi/table.html"
    context_object_name = 'data_presensi'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pertemuan_id = self.kwargs.get("pertemuan_id")
        context["pertemuan"] = get_object_or_404(Pertemuan, id=pertemuan_id) if pertemuan_id else None
        return context

    def get_queryset(self):
        pertemuan_id = self.kwargs.get("pertemuan_id")
        return self.model.objects.filter(pertemuan__id=pertemuan_id).order_by('-id')

# =====================================================================================================
#                                              USER LOAD PAGE
# =====================================================================================================
class UserPresensiCreateView(CustomTemplateBaseMixin, View):
    template_name = "main/user/presensi/add.html"

    def dispatch(self, request, *args, **kwargs):
        self.pertemuan = get_object_or_404(Pertemuan, id=kwargs.get("id"))
        now = timezone.now()

        if request.method == "GET":
            if self.pertemuan.presensi_mulai and now < self.pertemuan.presensi_mulai:
                messages.warning(request, "Presensi belum dibuka.")
                tipe_id = self.pertemuan.tipe_pertemuan.id
                return redirect(reverse_lazy("main:user.pertemuan.table")+ f"?tipe_pertemuan={tipe_id}")

        if request.method == "POST":
            if self.pertemuan.presensi_mulai and now < self.pertemuan.presensi_mulai:
                messages.error(request, "Presensi belum dibuka.")
                return redirect(request.path)

            if self.pertemuan.presensi_akhir and now > self.pertemuan.presensi_akhir:
                messages.error(request, "Presensi sudah ditutup.")
                return redirect(request.path)

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        presensi = Presensi.objects.filter(pertemuan=self.pertemuan, peserta=request.user).first()

        form = PresensiForm(instance=presensi)

        return render(request, self.template_name, {
            "form": form,
            "pertemuan": self.pertemuan,
            "now": timezone.now()
        })

    def post(self, request, *args, **kwargs):
        presensi = Presensi.objects.filter(pertemuan=self.pertemuan, peserta=request.user).first()

        form = PresensiForm(request.POST, request.FILES, instance=presensi)

        if not form.is_valid():
            return render(request, self.template_name, {
                "form": form,
                "pertemuan": self.pertemuan
            })

        presensi = form.save(commit=False)
        presensi.pertemuan = self.pertemuan
        presensi.peserta = request.user
        presensi.save()

        messages.success(request, "Anda berhasil melakukan absensi kehadiran.")

        tipe_id = self.pertemuan.tipe_pertemuan.id
        return redirect(reverse_lazy("main:user.pertemuan.table") + f"?tipe_pertemuan={tipe_id}")