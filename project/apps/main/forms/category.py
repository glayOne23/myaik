from django import forms
from django.utils.translation import gettext_lazy as _

from apps.services.mixins import FormErrorsMixin
from apps.main.models import Category


class FormCategory(forms.ModelForm, FormErrorsMixin):
    class Meta:
        model   = Category
        fields  = '__all__'
        labels  = {
            'name'        : _('Name'),
            'description' : _('Description'),
        }
