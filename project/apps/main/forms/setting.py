from django import forms
from apps.main.models import Setting
from django.utils.translation import gettext_lazy as _


class FormSetting(forms.ModelForm):
    class Meta:
        model   = Setting
        fields  = ['value', 'file']
        labels  = {
            'value' : _('Value'),
            'file' : _('File'),
        }
