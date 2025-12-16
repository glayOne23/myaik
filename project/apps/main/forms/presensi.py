from django import forms
from django.utils.translation import gettext_lazy as _

from apps.services.mixins import FormErrorsMixin
from apps.main.models import Presensi


class PresensiForm(forms.ModelForm, FormErrorsMixin):
    class Meta:
        model   = Presensi
        fields  = ['rangkuman', 'berkas_rangkuman']

        labels  = {
            'berkas_rangkuman' : _('Berkas Rangkuman (Jika Ada)'),
        }


class PresensiExcelForm(forms.Form, FormErrorsMixin):
    tipe_pertemuan = forms.ModelChoiceField(
        label=_('Tipe Pertemuan'),
        queryset=None,
    )
    excel_file = forms.FileField(
        label=_('Unggah Berkas Excel'),
        help_text=_('Unggah berkas Excel yang berisi data presensi.'),
        widget=forms.ClearableFileInput(attrs={'accept': '.xlsx, .xls'})
    )
