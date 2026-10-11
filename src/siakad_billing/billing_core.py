"""Logika inti billing UKT SIAKAD.

``BillingManager`` menerima ``AppSettings`` lewat dependency injection sehingga
kode yang sama berjalan di local, staging, maupun production.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from siakad_config.settings import AppSettings


class PembayaranUKT(BaseModel):
    nim: str
    nominal: Decimal
    status: str
    gateway_url: str


class BillingManager:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    def proses_pembayaran(
        self, nim: str, nominal: Decimal | int | str
    ) -> PembayaranUKT:
        if not nim or not nim.strip():
            raise ValueError("NIM tidak boleh kosong!")

        jumlah = Decimal(str(nominal))
        if jumlah <= 0:
            raise ValueError("Nominal pembayaran harus lebih besar dari 0!")

        return PembayaranUKT(
            nim=nim.strip(),
            nominal=jumlah,
            status="SUCCESS",
            gateway_url=f"{self.settings.payment_gateway_url}/charges",
        )

    def status_lingkungan(self) -> str:
        return (
            f"Sistem berjalan di lingkungan [{self.settings.app_env.upper()}] "
            f"pada port {self.settings.app_port} (Debug: {self.settings.debug})"
        )
