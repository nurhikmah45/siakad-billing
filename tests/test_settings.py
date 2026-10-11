from decimal import Decimal

import pytest
from pydantic import ValidationError

from siakad_billing.billing_core import BillingManager
from siakad_config.settings import AppSettings

ENV_KEYS = [
    "APP_ENV", "APP_PORT", "DEBUG", "DATABASE_URL", "PAYMENT_GATEWAY_URL",
    "PAYMENT_API_KEY", "WA_GATEWAY_URL", "WA_AUTH_TOKEN",
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def make(**kw):
    base = {"database_url": "sqlite:///:memory:", "payment_api_key": "k"}
    base.update(kw)
    return AppSettings(_env_file=None, **base)


def test_load_valid_settings_from_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_PORT", "9000")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    monkeypatch.setenv("PAYMENT_API_KEY", "prod_secret")
    monkeypatch.setenv("PAYMENT_GATEWAY_URL", "https://bank.uinam.ac.id/api/")
    cfg = AppSettings(_env_file=None)
    assert cfg.app_env == "production"
    assert cfg.app_port == 9000
    assert cfg.debug is False
    assert cfg.payment_gateway_url == "https://bank.uinam.ac.id/api"
    assert cfg.payment_api_key.get_secret_value() == "prod_secret"


def test_fail_fast_missing_database_url(monkeypatch):
    monkeypatch.setenv("PAYMENT_API_KEY", "x")
    with pytest.raises(ValidationError) as exc:
        AppSettings(_env_file=None)
    assert "database_url" in str(exc.value).lower()


def test_fail_fast_missing_api_key(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///x.db")
    with pytest.raises(ValidationError) as exc:
        AppSettings(_env_file=None)
    assert "payment_api_key" in str(exc.value).lower()


@pytest.mark.parametrize("port", ["abc", "0", "70000"])
def test_invalid_port(port):
    with pytest.raises(ValidationError):
        make(app_port=port)


def test_invalid_app_env():
    with pytest.raises(ValidationError):
        make(app_env="prod-ish")


def test_invalid_gateway_url():
    with pytest.raises(ValidationError):
        make(payment_gateway_url="ftp://salah")


def test_production_rejects_debug_true():
    with pytest.raises(ValidationError):
        make(app_env="production", debug=True)


def test_secret_not_leaked_in_repr():
    cfg = make(payment_api_key="rahasia123")
    assert "rahasia123" not in repr(cfg)


def test_env_example_is_loadable(tmp_path):
    """Pastikan .env.example valid sebagai konfigurasi (inti Fresh Clone Test)."""
    from pathlib import Path

    example = Path(__file__).resolve().parent.parent / ".env.example"
    cfg = AppSettings(_env_file=example)
    assert cfg.app_env == "development"


def test_billing_with_injected_settings():
    cfg = make(app_env="testing", payment_gateway_url="https://mock-bank.local")
    trx = BillingManager(cfg).proses_pembayaran("60900124119", Decimal("3500000"))
    assert trx.status == "SUCCESS"
    assert trx.nominal == Decimal("3500000")
    assert trx.gateway_url == "https://mock-bank.local/charges"


@pytest.mark.parametrize("nominal", [0, -50000])
def test_billing_rejects_non_positive(nominal):
    with pytest.raises(ValueError, match="lebih besar dari 0"):
        BillingManager(make()).proses_pembayaran("60900124119", nominal)


def test_billing_rejects_empty_nim():
    with pytest.raises(ValueError, match="NIM"):
        BillingManager(make()).proses_pembayaran("  ", 1000)
