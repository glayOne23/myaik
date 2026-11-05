from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from apps.services.mixins import FormErrorsMixin
from apps.main.models import Presensi


# minimal karakter rangkuman presensi peserta (tidak berlaku untuk input admin)
RANGKUMAN_MIN_LENGTH = 50


class PresensiForm(forms.ModelForm, FormErrorsMixin):
    class Meta:
        model   = Presensi
        fields  = ['rangkuman', 'berkas_rangkuman']

        labels  = {
            'berkas_rangkuman' : _('Berkas Rangkuman (Jika Ada)'),
        }
        help_texts = {
            'rangkuman' : _('Minimal %(min)s karakter.') % {'min': RANGKUMAN_MIN_LENGTH},
        }
        widgets = {
            'rangkuman' : forms.Textarea(attrs={'minlength': RANGKUMAN_MIN_LENGTH, 'rows': 6}),
        }

    def clean_rangkuman(self):
        # spasi/enter berlebih tidak ikut dihitung
        rangkuman = ' '.join(self.cleaned_data.get('rangkuman', '').split())
        if len(rangkuman) < RANGKUMAN_MIN_LENGTH:
            raise forms.ValidationError(
                _('Rangkuman minimal %(min)s karakter (saat ini %(len)s karakter).'),
                params={'min': RANGKUMAN_MIN_LENGTH, 'len': len(rangkuman)},
            )
        return rangkuman


class AdminPresensiForm(forms.ModelForm, FormErrorsMixin):
    peserta = forms.ModelChoiceField(
        label=_('Peserta'),
        queryset=User.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control select2bs4'}),
    )

    class Meta:
        model  = Presensi
        fields = ['peserta', 'rangkuman', 'berkas_rangkuman']
        labels = {
            'berkas_rangkuman': _('Berkas Rangkuman (Jika Ada)'),
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


class PresensiTotalExcelForm(forms.Form, FormErrorsMixin):
    excel_file = forms.FileField(
        label=_('Unggah Berkas Excel'),
        help_text=_('Unggah berkas Excel yang berisi data presensi.'),
        widget=forms.ClearableFileInput(attrs={'accept': '.xlsx, .xls'})
    )
