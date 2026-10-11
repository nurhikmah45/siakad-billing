"""Konfigurasi 12-Factor (Faktor III) dengan validasi Pydantic Settings.

Nilai dibaca dari environment variable (prioritas tertinggi) lalu berkas
``.env``. Jika ada nilai wajib yang hilang atau tidak valid, aplikasi langsung
gagal saat start (fail-fast) dengan pesan galat yang jelas.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Pengaturan aplikasi yang type-safe dan tervalidasi."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )

    app_env: Literal["development", "staging", "production", "testing"] = (
        "development"
    )
    app_port: int = Field(default=8000, ge=1, le=65535)
    debug: bool = True

    # Wajib: tidak punya default -> fail-fast jika hilang
    database_url: str = Field(min_length=1)
    payment_api_key: SecretStr

    payment_gateway_url: str = "https://sandbox.bank.uinam.ac.id/api/v1"
    wa_gateway_url: str = "https://api.whatsapp-sim.local"
    wa_auth_token: SecretStr = SecretStr("dummy_wa_token_dev")

    @field_validator("payment_gateway_url", "wa_gateway_url")
    @classmethod
    def _validate_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("URL harus diawali http:// atau https://")
        return value.rstrip("/")

    @field_validator("payment_api_key")
    @classmethod
    def _validate_api_key(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("PAYMENT_API_KEY tidak boleh kosong")
        return value

    @model_validator(mode="after")
    def _validate_production(self) -> AppSettings:
        if self.app_env == "production":
            if self.debug:
                raise ValueError("DEBUG harus false saat APP_ENV=production")
            if not self.payment_gateway_url.startswith("https://"):
                raise ValueError(
                    "PAYMENT_GATEWAY_URL harus https:// saat APP_ENV=production"
                )
        return self


@lru_cache
def get_settings() -> AppSettings:
    """Ambil settings (di-cache). Panggil ``get_settings.cache_clear()`` di test."""
    return AppSettings()  # type: ignore[call-arg]
