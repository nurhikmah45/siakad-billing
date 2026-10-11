"""Demo cepat: ``uv run python -m siakad_billing``."""

from decimal import Decimal

from siakad_billing.billing_core import BillingManager
from siakad_config import get_settings


def main() -> None:
    manager = BillingManager(get_settings())
    print(manager.status_lingkungan())
    hasil = manager.proses_pembayaran("60900124119", Decimal("2500000"))
    print(hasil.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
