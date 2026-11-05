#!/bin/sh
set -e

# cron menjalankan job dengan environment kosong, jadi simpan env container
# (DB_*, API_GATEWAY_*, dst) agar bisa di-load oleh CRONTAB_COMMAND_PREFIX
CRON_ENV_FILE="${CRON_ENV_FILE:-/home/app/webapp/.cron_env}"
export -p > "$CRON_ENV_FILE"
chmod 600 "$CRON_ENV_FILE"

# daftarkan CRONJOBS dari settings.py lalu jalankan daemon cron
# (gagal setup cron tidak boleh menghentikan web app)
python manage.py crontab remove > /dev/null 2>&1 || true
if python manage.py crontab add && cron; then
    echo "[entrypoint] cron aktif:" && python manage.py crontab show
else
    echo "[entrypoint] WARNING: gagal mengaktifkan cron, sync SIHRD terjadwal tidak berjalan" >&2
fi

exec "$@"
