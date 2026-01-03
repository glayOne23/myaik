import datetime

import openpyxl
from apps.main.forms.presensi import (PresensiExcelForm, PresensiForm,
                                      PresensiTotalExcelForm)
from apps.main.models import Pertemuan, Presensi, TipePertemuan
from apps.main.views.base import (AdminRequiredMixin, CustomTemplateBaseMixin,
                                  in_grup)
from apps.services.stream_pdf import stream_sertifikat_pdf
from apps.services.utils import profilesync
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q, Value
from django.db.models.functions import Replace
from django.http import HttpResponse, HttpResponseForbidden
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import (CreateView, DeleteView, FormView, ListView,
                                  TemplateView, UpdateView)


# =====================================================================================================
#                                              MIXINS
# =====================================================================================================
class AdminorUserPresensiRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        presensi_obj = get_object_or_404(Presensi, id=kwargs.get("presensi_id"))
        if in_grup(request.user, 'admin') or presensi_obj.peserta == request.user:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden("Anda tidak memiliki hak akses.")


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


# class AdminPresensiExcelImportView(AdminRequiredMixin, View):

#     def get_or_sync_user(self, username, nip):
#         """
#         Cari user:
#         1. username
#         2. profile.nip
#         3. API sync (profilesync)
#         """
#         user = User.objects.select_related("profile").filter(Q(username=username) | Q(profile__nip=nip)).first()

#         if user:
#             return user

#         user, is_success = profilesync(username)

#         if not is_success or not user:
#             raise Exception(f"Peserta tidak ditemukan " f"(username='{username}', NIP='{nip}')")

#         return user


#     def _import_regular(self, tipe_pertemuan: TipePertemuan, workbook):
#         user_cache = {}

#         for sheet in workbook.worksheets:

#             if sheet.max_row < 2:
#                 continue

#             for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
#                 if not any(row):
#                     continue

#                 try:
#                     timestamp = row[0]
#                     email = str(row[1]).strip()
#                     nip = str(row[4]).strip()
#                     kajian = str(row[5]).strip()
#                     kesimpulan = row[6]

#                     username = email.replace('@ums.ac.id', '').lower().strip()

#                     cache_key = f"{username}:{nip}"

#                     if cache_key in user_cache:
#                         peserta = user_cache[cache_key]
#                     else:
#                         peserta = self.get_or_sync_user(username, nip)
#                         user_cache[cache_key] = peserta

#                     # =============================
#                     # 🔧 SIMPAN DATA PRESENSI
#                     # =============================
#                     dt = timezone.make_aware(timestamp) if timezone.is_naive(timestamp) else timestamp
#                     mulai = dt.replace(minute=0, second=0, microsecond=0)
#                     pertemuan_obj, _ = Pertemuan.objects.get_or_create(
#                         tipe_pertemuan=tipe_pertemuan,
#                         judul=kajian,
#                         defaults={
#                             'mulai': mulai,
#                             'akhir': mulai + timezone.timedelta(hours=2),
#                             'presensi_mulai': mulai,
#                             'presensi_akhir': mulai + timezone.timedelta(hours=2),
#                         }
#                     )
#                     Presensi.objects.update_or_create(
#                         pertemuan=pertemuan_obj,
#                         peserta=peserta,
#                         defaults={
#                             'rangkuman': kesimpulan,
#                             'created_at': dt,
#                             'updated_at': dt,
#                         }
#                     )

#                 except Exception as e:
#                     raise Exception(f"Sheet='{sheet.title}' " f"Baris={idx} " f"Error={e}")


#     def post(self, request, *args, **kwargs):
#         form = PresensiExcelForm(request.POST, request.FILES)
#         form.fields['tipe_pertemuan'].queryset = TipePertemuan.objects.all()

#         if not form.is_valid():
#             messages.error(request, f"Form tidak valid. {form.get_form_errors()}")
#             return redirect('main:admin.pertemuan.table')

#         try:
#             workbook = openpyxl.load_workbook(request.FILES['excel_file'], data_only=True)
#         except Exception as e:
#             messages.error(request, f"Gagal membaca file Excel: {e}")
#             return redirect('main:admin.pertemuan.table')

#         try:
#             with transaction.atomic():
#                 tipe = form.cleaned_data['tipe_pertemuan']
#                 self._import_regular(tipe, workbook)
#         except Exception as e:
#             messages.error(request, f"Gagal impor Excel. {e}")
#             return redirect('main:admin.pertemuan.table')

#         messages.success(request, "Import selesai. Semua data berhasil diunggah.")
#         return redirect('main:admin.pertemuan.table')



class AdminPresensiExcelImportV2View(AdminRequiredMixin, View):

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
        errors = []  # ⬅️ kumpulkan error

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

                    if not timestamp or not email:
                        raise ValueError("Timestamp atau email kosong")

                    username = email.replace('@ums.ac.id', '').lower().strip()
                    cache_key = f"{username}:{nip}"

                    if cache_key in user_cache:
                        peserta = user_cache[cache_key]
                    else:
                        peserta = self.get_or_sync_user(username, nip)
                        user_cache[cache_key] = peserta

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
                    errors.append(
                        f"Sheet '{sheet.title}' baris {idx}: {e}"
                    )

        return errors


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
                errors = self._import_regular(tipe, workbook)

                if errors:
                    # gabungkan error jadi satu pesan
                    error_text = "<br>".join(errors)
                    messages.warning(request, mark_safe(f"Import selesai dengan error:<br>{error_text}"))
                    return redirect('main:admin.pertemuan.table')

        except Exception as e:
            messages.error(request, f"Gagal impor Excel. {e}")
            return redirect('main:admin.pertemuan.table')

        messages.success(request, "Import selesai. Semua data berhasil diunggah.")
        return redirect('main:admin.pertemuan.table')




class AdminPresensiTotalExcelImportView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = PresensiTotalExcelForm(request.POST, request.FILES)

        if not form.is_valid():
            messages.error(request, f"Form tidak valid. {form.get_form_errors()}")
            return redirect('main:admin.pertemuan.table')

        try:
            workbook = openpyxl.load_workbook(request.FILES['excel_file'], data_only=True)
        except Exception as e:
            messages.error(request, f"Gagal membaca file Excel: {e}")
            return redirect('main:admin.pertemuan.table')

        def col_is_valid(val):
            return val not in (None, '', 0)

        try:
            with transaction.atomic():
                sheet = workbook['Sheet1']

                for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=3):
                    if not any(row):
                        continue

                    try:
                        nip = row[0]
                        tahun = row[15]
                        ql = row[3]
                        webinar = row[4]
                        tarjih = row[5]

                        # print(f"{type(nip)} - {type(tahun)} - QL:{ql} Webinar:{webinar} Tarjih:{tarjih}")

                        if tahun == 2025:
                            queryset = User.objects.annotate(
                                nip_normalized=Replace('profile__nip', Value('.'), Value(''))
                            ).filter(nip_normalized=nip)

                            if len(queryset) == 0:
                                print(f"NIP '{nip}' tidak ditemukan.")

                            if len(queryset) > 1:
                                print(f"NIP '{nip}' terdapat lebih dari 1")

                    except Exception as e:
                        raise Exception(f"Sheet='{sheet.title}' " f"Baris={idx} " f"Error={e}")

        except Exception as e:
            messages.error(request, f"Gagal impor Excel. {e}")
            return redirect('main:admin.pertemuan.table')

        messages.success(request, "Import selesai. Semua data total presensi berhasil diunggah.")
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

        karyawan_obj = get_object_or_404(User, id=karyawan_id)
        tanggalmulaimasuk = None
        if karyawan_obj.profile.tanggalmulaimasuk:
            tanggalmulaimasuk = datetime.datetime.strptime(
                karyawan_obj.profile.tanggalmulaimasuk,
                "%Y-%m-%d"
            ).date()

        try:
            pertemuan_filter = Q(pertemuan__mulai__year=tahun)

            if tanggalmulaimasuk:
                pertemuan_filter &= Q(
                    pertemuan__mulai__date__gte=tanggalmulaimasuk
                )

            data = (
                TipePertemuan.objects
                .annotate(
                    total_pertemuan=Count(
                        'pertemuan',
                        filter=pertemuan_filter,
                        distinct=True
                    ),
                    total_presensi=Count(
                        'pertemuan__presensi',
                        filter=pertemuan_filter & Q(
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

            return JsonResponse(list(data), safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class LembagaPresensiGrafikView(LoginRequiredMixin, View):
    def get(self, request):
        tahun = request.GET.get('tahun')
        kode_lembaga = request.GET.get('lembaga')

        if not tahun or not kode_lembaga:
            return JsonResponse({"error": "Tahun dan lembaga harus disediakan."}, status=400)

        try:
            # ---------------------------------------------------
            # Query Pertemuan + aggregate presensi
            # ---------------------------------------------------
            pertemuandata = Pertemuan.objects.all().order_by('mulai')
            if kode_lembaga != 'all':
                pertemuandata = pertemuandata.filter(mulai__year=tahun, presensi__peserta__profile__home_id=kode_lembaga)
            pertemuan_qs = (
                pertemuandata
                .annotate(
                    total_presensi=Count('presensi', distinct=True)
                )
                .select_related('tipe_pertemuan')
                .order_by('tipe_pertemuan__id', 'mulai')
            )

            # ---------------------------------------------------
            # Grouping by TipePertemuan
            # ---------------------------------------------------
            result = {}

            for p in pertemuan_qs:
                tipe = p.tipe_pertemuan
                if not tipe:
                    continue

                if tipe.id not in result:
                    result[tipe.id] = {
                        "tipe_id": tipe.id,
                        "tipe_nama": tipe.nama,
                        "has_sertifikat": tipe.has_sertifikat,
                        "pertemuan": []
                    }

                result[tipe.id]["pertemuan"].append({
                    "pertemuan_id": p.id,
                    "judul": p.judul,
                    "mulai": p.mulai.isoformat() if p.mulai else None,
                    "total_presensi": p.total_presensi
                })

            return JsonResponse(list(result.values()), safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class UserPresensiSertifikatView(AdminorUserPresensiRequiredMixin, CustomTemplateBaseMixin, View):
    def get(self, request, *args, **kwargs):
        presensi_obj = get_object_or_404(Presensi, id=kwargs.get("presensi_id"))

        context_data = {
            "nip1": presensi_obj.peserta.profile.nip,
            "nama1": presensi_obj.peserta.get_full_name(),
            "homebase": presensi_obj.peserta.profile.homebase,
            "nip2": presensi_obj.peserta.profile.nip,
            "nama2": presensi_obj.peserta.get_full_name(),
        }

        pdf_stream = stream_sertifikat_pdf(
            template_path=presensi_obj.pertemuan.sertifikat.path,
            position_data=presensi_obj.pertemuan.sertifikat_position,
            context_data=context_data,
        )

        response = HttpResponse(
            pdf_stream.getvalue(),
            content_type="application/pdf"
        )

        # 🔑 inline = preview, attachment = download
        response["Content-Disposition"] = 'inline; filename="sertifikat-preview.pdf"'

        return response
