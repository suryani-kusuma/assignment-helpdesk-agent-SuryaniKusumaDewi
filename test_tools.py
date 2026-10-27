
from app.tools import get_ticket_status

# Tes 1: tiket yang tersedia
print("=== Tes 1: Tiket ditemukan ===")
print(get_ticket_status("TICKET-0001"))

# Tes 2: tiket yang tidak tersedia
print("\n=== Tes 2: Tiket tidak ditemukan ===")
print(get_ticket_status("TICKET-9999"))
