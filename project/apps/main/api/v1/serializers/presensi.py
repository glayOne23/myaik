from apps.main.models import Pertemuan, Presensi, TipePertemuan
from rest_framework import serializers


class PresensiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presensi
        fields = (
            '__all__'
        )
        depth = 1
        read_only_fields = ('id',)


class PresensiTotalSerializer(serializers.ModelSerializer):
    total_presensi = serializers.IntegerField(read_only=True)
    total_pertemuan = serializers.IntegerField(read_only=True)
    persentasi = serializers.FloatField(read_only=True)

    class Meta:
        model = TipePertemuan
        fields = (
            'nama',
            'total_pertemuan',
            'total_presensi',
            'persentasi',
        )
