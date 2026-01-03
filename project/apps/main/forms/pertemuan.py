from django import forms
from django.utils.translation import gettext_lazy as _

from apps.services.mixins import FormErrorsMixin
from apps.main.models import Pertemuan


class PertemuanForm(forms.ModelForm, FormErrorsMixin):
    class Meta:
        model   = Pertemuan
        # fields  = ['tipe_pertemuan', 'judul', 'deskripsi', 'pembicara', 'tanggal_range', 'presensi_range', 'tautan', 'materi']
        fields  = ['tipe_pertemuan', 'judul', 'deskripsi', 'pembicara', 'mulai', 'akhir', 'presensi_mulai', 'presensi_akhir', 'tautan', 'materi', 'sertifikat', 'sertifikat_position']

        labels  = {
            'tipe_pertemuan' : _('Tipe AIK'),
            'mulai' : _('Mulai Kajian'),
            'akhir' : _('Akhir Kajian'),
            'presensi_mulai' : _('Mulai Absensi'),
            'presensi_akhir' : _('Berakhir Absensi'),
        }

        widgets = {
            'deskripsi': forms.Textarea(attrs={'rows': 2}),

            'mulai': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'akhir': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'presensi_mulai': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'presensi_akhir': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),

            'sertifikat_position': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # UPDATE MODE
        if self.instance.pk and self.instance.sertifikat:
            self.fields["sertifikat"].widget.attrs.update({
                "data-existing-url": self.instance.sertifikat.url
            })


class PertemuanExcelForm(forms.Form, FormErrorsMixin):
    excel_file = forms.FileField(
        label=_('Unggah Berkas Excel'),
        help_text=_('Unggah berkas Excel yang berisi data kajian'),
        widget=forms.ClearableFileInput(attrs={'accept': '.xlsx, .xls'})
    )