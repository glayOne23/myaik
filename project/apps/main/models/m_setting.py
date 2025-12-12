from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from private_storage.fields import PrivateFileField
from uuid import uuid4

import os

def path_file(instance, filename):
    upload_to = 'file/setting'
    ext = filename.split('.')[-1]
    hex = '{}'.format(uuid4().hex)
    filename = '%s.%s' % (hex, ext)
    return os.path.join(upload_to, filename)


class Setting(models.Model):
    class MODE(models.TextChoices):
        CHAR        = "char", _("CHAR")
        TEXT        = "text", _("TEXT")
        FILE        = "file", _("FILE")
        CHARFILE    = "charfile", _("CHARFILE")
        TEXTFILE    = "textfile", _("TEXTFILE")

    id              = models.BigAutoField(primary_key=True)
    category        = models.CharField(max_length=250, null=True)
    key             = models.CharField(max_length=250, null=True)
    alias           = models.CharField(max_length=100, null=True)
    mode            = models.CharField(max_length=10, null=True, choices=MODE.choices)
    value           = models.TextField(null=True, blank=True)
    file            = PrivateFileField(null=True, blank=True, upload_to=path_file)

    class Meta:
        ordering    = ['id']

    def __str__(self):
        txt = '{\n'
        txt += 'ID \t: {},\n'.format(str(self.id))
        txt += 'CATEGORY \t: {},\n'.format(str(self.category))
        txt += 'KEY \t: {},\n'.format(str(self.key))
        txt += 'ALIAS \t: {},\n'.format(str(self.alias))
        txt += 'MODE \t: {},\n'.format(str(self.mode))
        txt += 'VALUE \t: {},\n'.format(str(self.value))
        txt += 'FILE \t: {},\n'.format(str(self.file))
        txt += '}\n'
        return txt
    

    def save(self, *args, **kwargs):
        try:
            this = Setting.objects.get(id=self.id)
            if this.file != self.file:
                this.file.delete()
        except: pass
        super().save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)


    def is_image(self):
        if self.file and hasattr(self.file, 'url'):
            IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
            _, extension = os.path.splitext(self.file.url)
            return extension.lower() in IMAGE_EXTENSIONS
        else:
            return None


    def file_url(self):
        if self.file and hasattr(self.file, 'url'):
            return self.file.url
        else:
            return os.path.join(settings.STATIC_URL, 'images/nofile.png')


    @staticmethod
    def getmode(txt):
        choices = [choice[0] for choice in Setting.MODE.choices]
        return [choice for choice in choices if txt.lower() in choice.lower()]