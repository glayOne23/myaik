from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from apps.services.mixins import FormErrorsMixin
from apps.authentication.models import Profile


class FormUserEdit(forms.ModelForm, FormErrorsMixin):
    username    = forms.CharField(max_length=150, required=False, help_text='Optional')
    first_name  = forms.CharField(max_length=150, required=False, help_text='Optional')
    last_name   = forms.CharField(max_length=150, required=False, help_text='Optional')
    email       = forms.EmailField(max_length=254, required=False, help_text='Enter a valid email address')
    password1   = forms.CharField(max_length=50, required=False, help_text='Optional')
    password2   = forms.CharField(max_length=50, required=False, help_text='Optional')

    class Meta:
        model   = User
        fields  = ['username','first_name','last_name','email','password1','password2']
    

class FormProfileEdit(forms.ModelForm, FormErrorsMixin):
    class Meta:
        model   = Profile
        fields  = ['nip', 'nidn', 'ext_email', 'phone_number', 'image']
        labels  = {
            'nip'           : _('NIP'),
            'nidn'          : _('NIDN'),
            'ext_email'     : _('Additional email'), # Extra Email
            'phone_number'  : _('Phone number'),
            'image'         : _('Image'),
        }