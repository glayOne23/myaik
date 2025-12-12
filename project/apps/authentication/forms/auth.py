from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.services.mixins import FormErrorsMixin
from apps.authentication.models import Profile



class FormSignUp(UserCreationForm, FormErrorsMixin):
    username    = forms.CharField(min_length=5, required=True, help_text='Required')
    first_name  = forms.CharField(max_length=30, required=True, help_text='Required')
    last_name   = forms.CharField(max_length=30, required=False, help_text='Optional')
    email       = forms.CharField(max_length=100, help_text='Enter a valid email address')

    class Meta:
        model   = User
        fields  = ['username','first_name','last_name','email','password1','password2']


class FormSignUpProfile(forms.ModelForm, FormErrorsMixin):
    class Meta:
        model   = Profile
        fields  = ['phone_number']


class FormSignIn(AuthenticationForm, FormErrorsMixin):
    error_messages = {
        "invalid_login": _(
            "Please check your credentials and try again."
        ),
        "inactive": _("This account is inactive. Please check your email for account verification or contact admin!"),
    }
    class Meta:
        model   = User
        fields  = ['username','password']


class FormResetPassword(forms.Form, FormErrorsMixin):
    email       = forms.EmailField(max_length=100, help_text='Enter a valid email address')
    otp         = forms.CharField(max_length=30, required=True, help_text='Enter the OTP sent to your email')
    password1   = forms.CharField(
        label       = 'New Password',
        widget      = forms.PasswordInput,
        required    = True,
        help_text   ='Enter a strong password'
    )
    password2   = forms.CharField(
        label       = 'Confirm New Password',
        widget      = forms.PasswordInput,
        required    = True,
        help_text   = 'Re-enter the same password'
    )


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError(_('This email is not registered.'), code='email_not_found')
        return email


    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        # Gunakan validator Django bawaan
        validate_password(password1)
        return password1


    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        otp = cleaned_data.get('otp')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        # Validasi OTP
        if email and otp:
            if not User.objects.filter(email=email, profile__otp=otp).exists():
                raise ValidationError(_('Invalid OTP for the given email address.'), code='invalid_otp')

        # Validasi password
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(_('Passwords do not match.'), code='password_mismatch')

        return cleaned_data


    def save(self):
        """
        Ubah password user berdasarkan email dan otp.
        """
        email = self.cleaned_data['email']
        otp = self.cleaned_data['otp']
        new_password = self.cleaned_data['password1']

        user = User.objects.get(email=email, profile__otp=otp)
        user.set_password(new_password)
        user.profile.otp = None
        user.save()
        return user