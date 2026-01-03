from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.validators import FileExtensionValidator

from apps.services.utils import data_jabfung
from private_storage.fields import PrivateImageField

from uuid import uuid4
import os


def path_image(instance, filename):
    upload_to = 'images/profile'
    ext = filename.split('.')[-1]
    hex = '{}'.format(uuid4().hex)
    filename = '%s.%s' % (hex, ext)
    return os.path.join(upload_to, filename)


class Profile(models.Model):
    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', primary_key=True)
    nip             = models.CharField(max_length=20, null=True, blank=True)
    nidn            = models.CharField(max_length=50, null=True, blank=True)
    ext_email       = models.CharField(max_length=100, null=True, blank=True) # Extra Email
    phone_number    = models.CharField(max_length=15, null=True, blank=True)
    is_dosen        = models.IntegerField(null=True, blank=True)
    home_id         = models.CharField(max_length=20, null=True, blank=True)
    homebase        = models.CharField(max_length=255, null=True, blank=True)
    tanggalmulaimasuk = models.CharField(max_length=255, null=True, blank=True)
    image           = PrivateImageField(null=True, blank=True, upload_to=path_image, validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','webp'])])
    otp             = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        txt = '{\n'
        txt += 'USERNAME \t: {},\n'.format(str(self.user.username if self.user else self.user))
        txt += 'NIP \t: {},\n'.format(str(self.nip))
        txt += 'NIDN \t: {},\n'.format(str(self.nidn))
        txt += 'EXT_EMAIL \t: {},\n'.format(str(self.ext_email))
        txt += 'PHONE_NUMBER \t: {},\n'.format(str(self.phone_number))
        txt += 'IS_DOSEN \t: {},\n'.format(str(self.is_dosen))
        txt += 'HOME_ID \t: {},\n'.format(str(self.home_id))
        txt += 'HOMEBASE \t: {},\n'.format(str(self.homebase))
        txt += 'IMAGE \t: {},\n'.format(str(self.image))
        txt += 'OTP \t: {},\n'.format(str(self.otp))
        txt += '}\n'
        return txt


    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return os.path.join(settings.STATIC_URL, 'images/profile/default.png')


    def save(self, *args, **kwargs):
        try:
            this = Profile.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
        except: pass
        super().save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete()
        super().delete(*args, **kwargs)


    def get_jabfung(self, uid=None):
        data = data_jabfung()
        try:
            if uid:
                return data[uid]
            return data[self.is_dosen]
        except:
            return None


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()