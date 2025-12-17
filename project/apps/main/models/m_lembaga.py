from django.db import models


class Lembaga(models.Model):
    kode_lembaga = models.CharField(max_length=50)
    nama = models.CharField(max_length=255)
    namasingkat = models.CharField(max_length=255, null=True, blank=True)
    superunit = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    jenis_id = models.IntegerField(null=True, blank=True)
    jenis = models.CharField(max_length=100, null=True, blank=True)
    subjenis_id = models.IntegerField(null=True, blank=True)
    subjenis = models.CharField(max_length=100, null=True, blank=True)
    unitpendahulu = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering    = ['id']

    def __str__(self):
        return self.nama