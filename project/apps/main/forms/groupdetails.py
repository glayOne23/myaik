from django import forms
from django.utils.translation import gettext_lazy as _

from apps.services.mixins import FormErrorsMixin
from apps.authentication.models import GroupDetails


class FormGroupDetails(forms.ModelForm, FormErrorsMixin):
    class Meta:
        model   = GroupDetails
        fields  = ['alias','description']
        labels  = {
            'alias'       : _('Alias'),
            'description' : _('Description'),
        }
