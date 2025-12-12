from django import forms
from django.utils.translation import gettext_lazy as _

from apps.services.mixins import FormErrorsMixin
from apps.main.models import TipePertemuan


class TipePertemuanForm(forms.ModelForm, FormErrorsMixin):
    class Meta:
        model   = TipePertemuan
        fields  = '__all__'

        # labels  = {
        #     'name'        : _('Name'),
        #     'description' : _('Description'),
        # }
