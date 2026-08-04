# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this app is

**MyAIK** ("PRESENSI AIK TERINTEGRASI SIHRD") is a Django 5 attendance-tracking system for Universitas Muhammadiyah Surakarta (UMS). It records employee attendance (`Presensi`) at recurring institutional meetings/events (`Pertemuan`) such as "Kajian Tarjih", "Kajian Qiyamul Lail", and "Webinar", grouped by `TipePertemuan`. It is built from `project-base`, an internal UMS Django starter template shared across multiple UMS apps (see README.md for the template's generic conventions).

All identity data (name, NIP, homebase/institution, employment status) is sourced from an external HR system, **SIHRD**, via an internal API Gateway — this app does not manage employee master data itself, it mirrors it into `Profile` on demand.

## Commands

Run everything from `project/` (where `manage.py` lives) unless noted.

```bash
# Local venv setup
python -m venv env && env/scripts/activate   # or source env/bin/activate on *nix
python -m pip install -r requirements.txt

# .env setup: copy .env_dev to .env and fill in DB / CAS / API_GATEWAY / API_STAR / EMAIL / WABLAS values

cd project
python manage.py makemigrations
python manage.py makemigrations authentication
python manage.py makemigrations main
python manage.py migrate

# Seed required fixtures (group + groupdetails are load-bearing for admin/user role checks)
python manage.py loaddata group
python manage.py loaddata groupdetails

python manage.py collectstatic --noinput   # required when DEBUG=False
python manage.py runserver
```

Docker (local, with Postgres):
```bash
docker compose up -d --build     # see docker-compose.yml "LOCAL" section; the "SERVER" section at the top is commented-out prod config
```

There is no configured test runner beyond Django's default (`apps.py: tests.py` per app are present but effectively empty scaffolding) — use `python manage.py test` if adding tests.

CI/CD is Jenkins (`Jenkinsfile`), building/pushing a Docker image to UMS's GitLab registry with commit-message-driven version bumps (`--mc`/`--fc`/default = major/feature/minor). No linting step is configured in CI.

## Architecture

### Apps (`project/apps/`)

- **`services`** — cross-cutting infrastructure, not a feature app: SIHRD `apigateway.py` (JWT-token client, token cached to `token/<name>.json`), `apistar.py` (student data API), `apiwhatsapp.py` (WABLAS), `utils.py` (`profilesync` — the core user-sync routine, `setsession`, `split_full_name`), `decorators.py` (`group_required`, `throttle_requests`, `ajax_required`), `djangocas.py` (custom CAS login/backend), `cetak_pdf.py`/`stream_pdf.py` (xhtml2pdf rendering), `context_processors.py` (injects global settings + pending-`Pertemuan` count into every template), `hijack.py`.
- **`authentication`** — login/signup/CAS SSO, `Profile` (1:1 with `User`, holds `nip`/`home_id`/`homebase`/`kepegawaian`/`status` mirrored from SIHRD) and `GroupDetails` (adds a display alias to Django's `Group`).
- **`landingpage`** — public home page, custom 404 handler.
- **`main`** — the actual attendance app: `Category`, `Setting` (singleton-style site settings), `Lembaga` (institution/unit tree, self-referential via `superunit`, synced from SIHRD), `Jabatan` (position, synced from SIHRD), and the core trio in `models/m_aik.py`: `TipePertemuan` → `Pertemuan` → `Presensi` (unique together on `pertemuan`+`peserta`).

### Identity model: CAS login vs. SIHRD sync

Users authenticate via UMS's central CAS SSO (`django_cas_ng` + `apps.services.djangocas.CustomCASBackend`). On **first** CAS login, `CustomCASBackend.configure_user` calls `profilesync(user)`, which:
1. `get_or_create`s the local `User` by username.
2. Calls `apigateway.getProfile(username)` (SIHRD "umar/v3/profil" endpoint) — if the person is an employee, fills in `Profile` fields (`nip`, `home_id`, `homebase`, `kepegawaian`, `status`, ...).
3. If not an employee, falls back to `apistar` (student API) instead.
4. Saves `User` + `Profile`.

`profilesync` is also called directly (outside CAS login) any time a `User` needs to be resolved/created from just a username/NIP — notably during Excel attendance import (see below) and admin "sync profile" actions. **This makes it a hot path that can trigger external HTTP calls from inside request handlers**, including bulk-import loops.

Group membership (`admin` vs regular user) drives authorization via `in_grup()` / `AdminRequiredMixin` (`main/views/base.py`) rather than Django's `is_staff`/`is_superuser`. `AdminRequiredMixin` and `CustomTemplateBaseMixin` (which also sets template-level flags like `datatables`/`select2` per-view) are the base mixins nearly every admin view class in `main/views/*.py` composes from.

### Attendance domain model

- `TipePertemuan` — a meeting category (e.g. "Kajian Tarjih"), optionally certificate-eligible (`has_sertifikat`).
- `Pertemuan` — a single scheduled meeting/event under a `TipePertemuan`, with `mulai`/`akhir` (event window) and separate `presensi_mulai`/`presensi_akhir` (attendance-taking window) — a user can only self-check-in (`UserPresensiCreateView`) between those bounds. Can carry a certificate template (`sertifikat` file + `sertifikat_position` JSON for stamping name/NIP coordinates) rendered via `stream_sertifikat_pdf`.
- `Presensi` — one attendance record per `(pertemuan, peserta)`, created either by the user themself, by an admin (`AdminPresensiCreateView`), or via bulk Excel import.

### Excel import paths (`main/views/presensi.py`, `main/views/pertemuan.py`)

There are two distinct bulk-import flows for `Presensi`, both admin-only, both wrapped in a single `transaction.atomic()` for the whole file and processed **row-by-row synchronously inside the request**, using `openpyxl.load_workbook(..., data_only=True)` (not `read_only=True`):

- **`AdminPresensiExcelImportV2View`** (`admin.presensi.excel_import`) — imports raw Google-Forms-style attendance export rows (`Timestamp, Email address, Nama, Status, NIK, "<Kajian> ke:", Kesimpulan, ...`). Per row it resolves the user via `get_or_sync_user` (username/NIP lookup, falling back to `profilesync` → external API call), `get_or_create`s the `Pertemuan` by `(tipe_pertemuan, judul)`, and `update_or_create`s the `Presensi`. User lookups are memoized in a local dict per request, but the `Pertemuan.get_or_create` is **not** memoized — it re-queries per row even though a file typically has very few distinct meeting titles.
- **`AdminPresensiTotalExcelImportView`** (`admin.presensi.total_excel_import`) — imports a different, wide-format "total counts per NIP per year" sheet (hardcoded to `Sheet1`, hardcoded column indices, hardcoded institutional filters like `'Kajian Qiyamul Lail'`/`'Webinar'`/`'Kajian Tarjih'` and year `2025`) and back-fills `Presensi` rows without real timestamps ("Auto import dari total Excel 2025").
- `AdminPertemuanExcelImportView` (`main/views/pertemuan.py`) does a similar per-row `openpyxl` import for `Pertemuan` records themselves.

Because these imports are synchronous, unbounded (no batching/chunking, no bulk_create), and can each trigger network calls to the SIHRD API gateway per unknown user, **large files are prone to request-timeout failures** (default gunicorn sync worker timeout is 30s, and `Dockerfile`'s `CMD`/`docker-compose.yml` don't override it). Any fix for import performance should look at: memoizing `Pertemuan` lookups per file (like the `user_cache`), presence-checking users before the loop instead of per-row `profilesync`, batching DB writes (`bulk_create`/`bulk_update`), running the import outside the request/worker timeout window (background task, chunked AJAX, or `--timeout` increase paired with a management command), and adding explicit `requests` timeouts in `apps/services/apigateway.py` (currently unset, so a slow SIHRD response can stall a worker indefinitely).

### REST API (`main/api/`)

A small DRF API under `/presensi-myaik/v1/` (see `project/urls.py`) exposes read-only per-user attendance totals (`PresensiUserListAPIView`, `PresensiUserTotalListAPIView`) for external consumption ("api untuk di gateway" — i.e. meant to be called by the SIHRD gateway/other systems, not the app's own frontend). Auth is DRF `BasicAuthentication`/`SessionAuthentication`; custom exception handling and pagination live in `apps/services/api/`.

### Templates & frontend

Server-rendered Django templates using the **Ace Admin** template (vendored under `project/static/template/`), Bootstrap 4, `crispy_forms`, DataTables, Select2. `CustomTemplateBaseMixin.get_context_data` toggles which of these asset bundles a given page includes. PDF exports (certificates, attendance recap) go through `xhtml2pdf` via `apps/services/cetak_pdf.py`/`stream_pdf.py`, not a headless browser.

### Config / environment

Settings (`project/project/settings.py`) are entirely `django-decouple`-driven from `.env` (`.env_dev` is the template to copy). Key non-obvious settings: `USE_TZ = False` (naive datetimes throughout — see the `if settings.USE_TZ` branching in the Excel import when normalizing timestamps), `AUTHENTICATION_BACKENDS` stacks `AllowAllUsersModelBackend` + `ModelBackend` + the custom CAS backend, and `API_GATEWAY_*`/`API_STAR_*`/`API_WHATSAPP_*` are all optional integrations that degrade gracefully (checked with `hasattr`/truthiness) if unset.
