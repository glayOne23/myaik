from json import dumps

from apps.main.models import Jabatan, Lembaga
from apps.services.apigateway import apigateway


def sync_lembaga():
    '''
        Sinkron data lembaga dari SIHRD. Return (is_success, jumlah_data)
    '''
    multilembaga = apigateway.getLembaga()
    if not multilembaga.get('status'):
        return False, 0

    data = multilembaga.get('data', [])
    for lembaga in data:
        lembaga_obj, _ = Lembaga.objects.update_or_create(
            kode_lembaga=lembaga.get('uniid'),
            defaults={
                'nama': lembaga.get('nama'),
                'namasingkat': lembaga.get('namasingkat'),
                'jenis_id': lembaga.get('jenis_id'),
                'jenis': lembaga.get('jenis'),
                'subjenis_id': lembaga.get('subjenis_id'),
                'subjenis': lembaga.get('subjenis'),
            }
        )

        if superunit := Lembaga.objects.filter(kode_lembaga=lembaga.get('superunit')):
            superunit_obj = superunit.first()
            lembaga_obj.superunit = superunit_obj

        if lembaga.get('unitpendahulu'):
            unitpendahulu = []
            for unit in lembaga.get('unitpendahulu', []):
                unitpendahulu.append(unit.get('uniid'))
            lembaga_obj.unitpendahulu = dumps(unitpendahulu)

        lembaga_obj.save()

    return True, len(data)


def sync_jabatan():
    '''
        Sinkron data jabatan dari SIHRD. Return (is_success, jumlah_data)
    '''
    multijabatan = apigateway.getJabatan()
    if not multijabatan.get('status'):
        return False, 0

    data = multijabatan.get('data', [])
    for jabatan in data:
        jabatan_obj, _ = Jabatan.objects.update_or_create(
            kode_jabatan=jabatan.get('kode_jabatan'),
            defaults={
                'nama': jabatan.get('nama'),
                'eselon': jabatan.get('eselon'),
                'sks': jabatan.get('sks'),
                'uniid_penjabat': jabatan.get('uniid_penjabat'),
            }
        )

        if unit := Lembaga.objects.filter(kode_lembaga=jabatan.get('kode_lembaga')):
            unit_obj = unit.first()
            jabatan_obj.unit = unit_obj
            jabatan_obj.save()

    return True, len(data)
