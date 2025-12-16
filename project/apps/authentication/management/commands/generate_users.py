from django.core.management.base import BaseCommand
from apps.services.apigateway import apigateway
from apps.services.utils import profilesync
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Generate users from the API'

    def handle(self, *args, **kwargs):
        try:
            datakaryawan = apigateway.getKaryawan()
            for karyawan in datakaryawan['data']:
                if not User.objects.filter(username=karyawan['uniid']).exists():
                    user, is_success = profilesync(karyawan['uniid'])
                    self.stdout.write(self.style.SUCCESS(f'generated user: {user.username}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Gagal generate users: {str(e)}'))