
"""
Modul Tools — fungsi untuk mengambil data tiket secara langsung
dari mock_tickets.csv.
"""

from pathlib import Path

import pandas as pd

# Mengacu pada folder data di root project.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MOCK_TICKETS_PATH = PROJECT_ROOT / "data" / "mock_tickets.csv"


def get_ticket_status(ticket_id: str) -> str:
    """
    Mencari tiket berdasarkan ticket_id.

    Jika ditemukan, kembalikan informasi tiket.
    Jika tidak ditemukan, kembalikan pesan informatif.
    """
    try:
        # 1. Membaca data tiket dari file CSV.
        tickets = pd.read_csv(MOCK_TICKETS_PATH, dtype={"ticket_id": str})

        # 2. Membersihkan spasi dan membandingkan ID tiket.
        tickets["ticket_id"] = tickets["ticket_id"].str.strip()
        ticket_id = ticket_id.strip().upper()

        # 3. Mencari tiket yang sesuai.
        result = tickets[
            tickets["ticket_id"].str.upper() == ticket_id
        ]

        # 4. Jika tiket tidak ditemukan.
        if result.empty:
            return (
                f"Tiket {ticket_id} tidak ditemukan. "
                "Silakan periksa kembali ID tiket Anda."
            )

        # 5. Mengambil data dari baris tiket yang ditemukan.
        ticket = result.iloc[0]

        subject = ticket["subject"]
        status = ticket["status"]
        last_update = ticket["last_update"]

        # 6. Menyusun jawaban untuk pengguna.
        return (
            f"Informasi tiket {ticket_id}:\n"
            f"Subjek: {subject}\n"
            f"Status: {status}\n"
            f"Terakhir diperbarui: {last_update}"
        )

    except FileNotFoundError:
        return (
            "Data tiket tidak dapat ditemukan. "
            "Silakan hubungi administrator."
        )

    except Exception as e:
        return f"Terjadi kesalahan saat mencari tiket: {e}"
