import time

from apps.services.apigateway import apigateway
from apps.services.sihrd_sync import sync_jabatan, sync_lembaga
from apps.services.utils import profilesync
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Sinkron data SIHRD (lembaga, jabatan) lalu profile sync semua karyawan. Dijalankan via cron tiap Sabtu 01:00.'

    def add_arguments(self, parser):
        parser.add_argument('--skip-lembaga', action='store_true', help='Lewati sinkron lembaga')
        parser.add_argument('--skip-jabatan', action='store_true', help='Lewati sinkron jabatan')
        parser.add_argument('--skip-profile', action='store_true', help='Lewati profile sync karyawan')

    def log(self, msg, style=None):
        line = f'[{timezone.now():%Y-%m-%d %H:%M:%S}] [sync_sihrd] {msg}'
        self.stdout.write(style(line) if style else line)

    def handle(self, *args, **options):
        started = time.monotonic()
        self.log('Mulai sinkron SIHRD')

        # lembaga dulu, karena jabatan & profile merujuk ke lembaga
        if not options['skip_lembaga']:
            self.run_step('lembaga', sync_lembaga)

        if not options['skip_jabatan']:
            self.run_step('jabatan', sync_jabatan)

        if not options['skip_profile']:
            self.sync_profiles()

        self.log(f'Selesai dalam {time.monotonic() - started:.0f} detik', self.style.SUCCESS)

    def run_step(self, name, func):
        try:
            is_success, total = func()
        except Exception as e:
            self.log(f'Gagal sinkron {name}: {e}', self.style.ERROR)
            return

        if is_success:
            self.log(f'Sinkron {name} berhasil: {total} data', self.style.SUCCESS)
        else:
            self.log(f'Gagal mengambil data {name} dari API Gateway', self.style.ERROR)

    def sync_profiles(self):
        try:
            datakaryawan = apigateway.getKaryawan()
        except Exception as e:
            self.log(f'Gagal mengambil data karyawan: {e}', self.style.ERROR)
            return

        if not datakaryawan.get('status'):
            self.log('Gagal mengambil data karyawan dari API Gateway', self.style.ERROR)
            return

        usernames = [k['uniid'] for k in datakaryawan.get('data', []) if k.get('uniid')]

        # karyawan lokal yang sudah tidak ada di list SIHRD tetap di-sync agar status-nya ikut terupdate
        sihrd_set = set(usernames)
        usernames += [
            u for u in User.objects.filter(profile__home_id__isnull=False).values_list('username', flat=True)
            if u not in sihrd_set
        ]

        total = len(usernames)
        self.log(f'Profile sync {total} karyawan')

        success, failed = 0, []
        for i, username in enumerate(usernames, start=1):
            try:
                _, is_success = profilesync(username)
            except Exception as e:
                is_success = False
                self.log(f'Error profile sync {username}: {e}', self.style.WARNING)

            if is_success:
                success += 1
            else:
                failed.append(username)

            if i % 200 == 0:
                self.log(f'Progress {i}/{total}')

        self.log(f'Profile sync selesai: {success} berhasil, {len(failed)} gagal', self.style.SUCCESS)
        if failed:
            self.log(f'Gagal: {", ".join(failed[:50])}{" ..." if len(failed) > 50 else ""}', self.style.WARNING)
