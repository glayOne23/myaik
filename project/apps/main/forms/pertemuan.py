from django import forms
from django.utils.translation import gettext_lazy as _

from apps.services.mixins import FormErrorsMixin
from apps.main.models import Pertemuan


class PertemuanForm(forms.ModelForm, FormErrorsMixin):
    # 1️⃣ EXTRA FIELD (single input for date range)
    # tanggal_range = forms.CharField(required=True, label=_('Tanggal Mulai sampai Akhir'))
    # presensi_range = forms.CharField(required=True, label=_('Presensi Mulai sampai Akhir'))

    class Meta:
        model   = Pertemuan
        # fields  = ['tipe_pertemuan', 'judul', 'deskripsi', 'pembicara', 'tanggal_range', 'presensi_range', 'tautan', 'materi']
        fields  = ['tipe_pertemuan', 'judul', 'deskripsi', 'pembicara', 'mulai', 'akhir', 'presensi_mulai', 'presensi_akhir', 'tautan', 'materi']

        labels  = {
            'tipe_pertemuan' : _('Tipe AIK'),
            'mulai' : _('Mulai Kajian'),
            'akhir' : _('Akhir Kajian'),
            'presensi_mulai' : _('Mulai Absensi'),
            'presensi_akhir' : _('Berakhir Absensi'),
        }

        widgets = {
            'deskripsi'     : forms.Textarea(attrs={'rows': 2}),
            'mulai'         : forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'akhir'         : forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'presensi_mulai': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'presensi_akhir': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    # def clean(self):
    #     cleaned = super().clean()

    #     # ==============================
    #     # 1️⃣ Parse "mulai – akhir" range
    #     # ==============================
    #     t_range = cleaned.get("tanggal_range")
    #     if t_range and " to " in t_range:
    #         mulai, akhir = t_range.split(" to ")
    #         cleaned["mulai"] = mulai
    #         cleaned["akhir"] = akhir

    #     # =====================================
    #     # 2️⃣ Parse "presensi_mulai – presensi_akhir"
    #     # =====================================
    #     p_range = cleaned.get("presensi_range")
    #     if p_range and " to " in p_range:
    #         p_mulai, p_akhir = p_range.split(" to ")
    #         cleaned["presensi_mulai"] = p_mulai
    #         cleaned["presensi_akhir"] = p_akhir

    #     return cleaned
