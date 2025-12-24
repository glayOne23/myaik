from django.db import models
from django.contrib.auth.models import User


class TipePertemuan(models.Model):
    nama            = models.CharField(max_length=50)
    deskripsi       = models.TextField(blank=True, null=True)
    has_sertifikat = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering    = ['id']

    def __str__(self):
        return self.nama


class Pertemuan(models.Model):
    tipe_pertemuan  = models.ForeignKey(TipePertemuan, on_delete=models.SET_NULL, null=True)
    judul           = models.CharField(max_length=100)
    pembicara       = models.CharField(max_length=256)
    deskripsi       = models.TextField(blank=True, null=True)
    mulai           = models.DateTimeField(null=True, blank=True)
    akhir           = models.DateTimeField(null=True, blank=True)
    presensi_mulai  = models.DateTimeField(null=True, blank=True)
    presensi_akhir  = models.DateTimeField(null=True, blank=True)
    tautan          = models.URLField(max_length=200, blank=True, null=True)
    materi          = models.FileField(null=True, blank=True, upload_to='materi/')
    sertifikat = models.FileField(null=True, blank=True, upload_to='sertifikat/')
    sertifikat_position = models.JSONField(blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering    = ['id']

    def __str__(self):
        txt = '{\n'
        txt += 'ID \t: {},\n'.format(str(self.id))
        txt += 'TIPE_PERTEMUAN \t: {},\n'.format(str(self.tipe_pertemuan))
        txt += 'JUDUL \t: {},\n'.format(str(self.judul))
        txt += 'DESKRIPSI \t: {},\n'.format(str(self.deskripsi))
        txt += 'MULAI \t: {},\n'.format(str(self.mulai))
        txt += 'AKHIR \t: {},\n'.format(str(self.akhir))
        txt += '}\n'
        return txt


class Presensi(models.Model):
    pertemuan       = models.ForeignKey(Pertemuan, on_delete=models.CASCADE, null=True)
    peserta         = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    rangkuman       = models.TextField()
    berkas_rangkuman = models.FileField(null=True, blank=True, upload_to='rangkuman/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering    = ['id']
        unique_together = ('pertemuan', 'peserta')

    def __str__(self):
        txt = '{\n'
        txt += 'ID \t: {},\n'.format(str(self.id))
        txt += 'PERTEMUAN \t: {},\n'.format(str(self.pertemuan))
        txt += 'PESERTA \t: {},\n'.format(str(self.peserta))
        txt += '}\n'
        return txt
