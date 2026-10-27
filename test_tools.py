
from app.tools import get_ticket_status


def test_get_ticket_status_existing_ticket():
    result = get_ticket_status("TICKET-0001")

    # Pastikan tiket ditemukan.
    assert result is not None

    # Pastikan hasil berisi informasi tiket.
    assert "TICKET-0001" in str(result)


def test_get_ticket_status_missing_ticket():
    result = get_ticket_status("TICKET-9999")

    # Pastikan aplikasi memberikan informasi tiket tidak ditemukan.
    assert result is not None
    assert "tidak ditemukan" in str(result).lower()