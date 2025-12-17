import openpyxl
from apps.main.forms.presensi import PresensiExcelForm, PresensiForm
from apps.main.models import Pertemuan, Presensi, TipePertemuan
from apps.main.views.base import AdminRequiredMixin, CustomTemplateBaseMixin
from apps.services.apigateway import apigateway
from apps.services.utils import profilesync
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
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


class AdminPresensiExcelImportView(AdminRequiredMixin, View):

    def get_or_sync_user(self, username, nip):
        """
        Cari user:
        1. username
        2. profile.nip
        3. API sync (profilesync)
        """
        user = User.objects.select_related("profile").filter(Q(username=username) | Q(profile__nip=nip)).first()

        if user:
            return user

        user, is_success = profilesync(username)

        if not is_success or not user:
            raise Exception(f"Peserta tidak ditemukan " f"(username='{username}', NIP='{nip}')")

        return user


    def _import_regular(self, tipe_pertemuan: TipePertemuan, workbook):
        user_cache = {}

        for sheet in workbook.worksheets:

            if sheet.max_row < 2:
                continue

            for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                if not any(row):
                    continue

                try:
                    timestamp = row[0]
                    email = str(row[1]).strip()
                    nip = str(row[4]).strip()
                    kajian = str(row[5]).strip()
                    kesimpulan = row[6]

                    username = email.replace('@ums.ac.id', '').lower().strip()

                    cache_key = f"{username}:{nip}"

                    if cache_key in user_cache:
                        peserta = user_cache[cache_key]
                    else:
                        peserta = self.get_or_sync_user(username, nip)
                        user_cache[cache_key] = peserta

                    # =============================
                    # 🔧 SIMPAN DATA PRESENSI
                    # =============================
                    dt = timezone.make_aware(timestamp) if timezone.is_naive(timestamp) else timestamp
                    mulai = dt.replace(minute=0, second=0, microsecond=0)
                    pertemuan_obj, _ = Pertemuan.objects.get_or_create(
                        tipe_pertemuan=tipe_pertemuan,
                        judul=kajian,
                        defaults={
                            'mulai': mulai,
                            'akhir': mulai + timezone.timedelta(hours=2),
                            'presensi_mulai': mulai,
                            'presensi_akhir': mulai + timezone.timedelta(hours=2),
                        }
                    )
                    Presensi.objects.update_or_create(
                        pertemuan=pertemuan_obj,
                        peserta=peserta,
                        defaults={
                            'rangkuman': kesimpulan,
                            'created_at': dt,
                            'updated_at': dt,
                        }
                    )

                except Exception as e:
                    raise Exception(f"Sheet='{sheet.title}' " f"Baris={idx} " f"Error={e}")


    def _import_webinar(self, tipe_pertemuan: TipePertemuan, workbook):
        raise Exception("Format Webinar belum diimplementasikan")


    def post(self, request, *args, **kwargs):
        form = PresensiExcelForm(request.POST, request.FILES)
        form.fields['tipe_pertemuan'].queryset = TipePertemuan.objects.all()

        if not form.is_valid():
            messages.error(request, f"Form tidak valid. {form.get_form_errors()}")
            return redirect('main:admin.pertemuan.table')

        try:
            workbook = openpyxl.load_workbook(request.FILES['excel_file'], data_only=True)
        except Exception as e:
            messages.error(request, f"Gagal membaca file Excel: {e}")
            return redirect('main:admin.pertemuan.table')

        try:
            with transaction.atomic():
                tipe = form.cleaned_data['tipe_pertemuan']
                if tipe == 1:
                    self._import_webinar(tipe, workbook)
                else:
                    self._import_regular(tipe, workbook)
        except Exception as e:
            messages.error(request, f"Gagal impor Excel. {e}")
            return redirect('main:admin.pertemuan.table')

        messages.success(request, "Import selesai. Semua data berhasil diunggah.")
        return redirect('main:admin.pertemuan.table')


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


class UserPresensiBaganView(LoginRequiredMixin, View):
    def get(self, request):
        tahun = request.GET.get('tahun')
        karyawan_id = request.GET.get('karyawan')

        if not tahun or not karyawan_id:
            return JsonResponse({"error": "Tahun dan karyawan harus disediakan."}, status=400)

        try:
            data = (
                TipePertemuan.objects
                .annotate(
                    total_pertemuan=Count(
                        'pertemuan',
                        filter=Q(pertemuan__mulai__year=tahun),
                        distinct=True
                    ),
                    total_presensi=Count(
                        'pertemuan__presensi',
                        filter=Q(
                            pertemuan__mulai__year=tahun,
                            pertemuan__presensi__peserta_id=karyawan_id
                        ),
                        distinct=True
                    )
                )
                .values(
                    'id',
                    'nama',
                    'total_pertemuan',
                    'total_presensi'
                )
                .order_by('nama')
            )

            response_data = list(data)
            return JsonResponse(response_data, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)