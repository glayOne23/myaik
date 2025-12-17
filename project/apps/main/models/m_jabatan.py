from django.db import models
from apps.main.models.m_lembaga import Lembaga


class Jabatan(models.Model):
    kode_jabatan = models.CharField(max_length=50)
    nama = models.CharField(max_length=255)
    unit = models.ForeignKey(Lembaga, on_delete=models.CASCADE, null=True, blank=True)
    eselon = models.CharField(max_length=100, null=True, blank=True)
    sks = models.IntegerField(null=True, blank=True)
    uniid_penjabat = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering    = ['id']

    def __str__(self):
        return self.nama