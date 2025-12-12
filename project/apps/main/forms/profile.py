from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

from apps.services.mixins import FormErrorsMixin
from apps.authentication.models import Profile


class FormMyProfile(forms.ModelForm, FormErrorsMixin):
    class Meta:
        model   = Profile
        fields  = ['ext_email', 'phone_number', 'image']
        labels  = {
            'ext_email'     : _('Additional Email'), # Extra Email
            'phone_number'  : _('Phone number'),
            'image'         : _('Image'),
        }


class FormChangePassword(PasswordChangeForm, FormErrorsMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ('old_password', 'new_password1', 'new_password2'):
            self.fields[field].widget.attrs = {'class': 'form-control'}


class FormChangePasswordNew(forms.ModelForm, FormErrorsMixin):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, max_length=20)
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput, max_length=20)

    class Meta:
        model   = User
        fields  = ('password1', 'password2')
        labels  = {
            'password1' : _('Password'),
            'password2' : _('Password confirmation'),
        }