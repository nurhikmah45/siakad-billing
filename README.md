# SIAKAD Billing Service

Modul billing UKT SIAKAD (FST UIN Alauddin Makassar) sebagai repositori
**reproducible**: dependensi terkunci, konfigurasi 12-Factor tervalidasi, dan
lulus *Fresh Clone Test*.

Tugas Pekan 5, Pemrograman Lanjut (Sub-CPMK 3.1).

## Struktur

```text
.
├── .env.example            # template konfigurasi publik (di-commit)
├── .gitignore              # memblokir .env, .venv, *.db, cache
├── .python-version
├── pyproject.toml          # manifest PEP 621 + dependency group dev
├── uv.lock                 # lockfile (di-commit)
├── src/
│   ├── siakad_config/      # Pydantic Settings (12-Factor)
│   └── siakad_billing/     # logika billing
├── tests/
└── scripts/fresh_clone_test.sh
```

## Cara menjalankan

Prasyarat: [uv](https://docs.astral.sh/uv/) dan Git.

```bash
git clone <URL-REPO> siakad-billing
cd siakad-billing
uv sync --frozen              # install persis sesuai uv.lock
cp .env.example .env          # Windows PowerShell: Copy-Item .env.example .env
uv run pytest -q
uv run python -m siakad_billing
```

## Konfigurasi (12-Factor)

Semua konfigurasi dibaca dari environment variable (prioritas) atau `.env`,
divalidasi oleh `pydantic-settings` di `src/siakad_config/settings.py`.

| Variabel | Wajib | Default | Validasi |
|---|---|---|---|
| `APP_ENV` | tidak | `development` | development / staging / production / testing |
| `APP_PORT` | tidak | `8000` | integer 1-65535 |
| `DEBUG` | tidak | `true` | bool; harus `false` di production |
| `DATABASE_URL` | **ya** | - | tidak boleh kosong |
| `PAYMENT_API_KEY` | **ya** | - | tidak boleh kosong, disimpan sebagai `SecretStr` |
| `PAYMENT_GATEWAY_URL` | tidak | sandbox kampus | http(s); https di production |
| `WA_GATEWAY_URL` | tidak | simulator lokal | http(s) |
| `WA_AUTH_TOKEN` | tidak | dummy | `SecretStr` |

Variabel wajib yang hilang membuat aplikasi langsung gagal saat start
(*fail-fast*).

## The Fresh Clone Test

Dilakukan oleh **rekan berpasangan** di mesinnya sendiri:

```bash
git clone <URL-REPO> && cd siakad-billing
uv sync --frozen
cp .env.example .env
uv run ruff check .
uv run pytest -q
```

Atau otomatis: `bash scripts/fresh_clone_test.sh <URL-REPO>`.

### Lembar hasil (diisi rekan penguji)

| Item | Hasil |
|---|---|
| Nama penguji / tanggal | |
| OS & versi Python | |
| `uv sync --frozen` berhasil | ☐ ya ☐ tidak |
| `pytest` lulus semua | ☐ ya ☐ tidak |
| Catatan / kendala | |

## Workflow Git

Commit memakai [Conventional Commits](https://www.conventionalcommits.org/):
`feat`, `fix`, `docs`, `test`, `chore`, `build`, `ci`.

```bash
git commit -m "feat(billing): tambah validasi nominal"
```

Memperbarui dependensi: ubah `pyproject.toml`, jalankan `uv lock`, lalu commit
`pyproject.toml` bersama `uv.lock`.
