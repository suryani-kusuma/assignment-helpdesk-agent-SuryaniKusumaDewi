
"""
Router — menentukan apakah query user membutuhkan RAG
(informasi/kebijakan) atau tool call (cek status tiket).
"""

import re

from app.rag import answer_from_knowledge_base
from app.tools import get_ticket_status


async def detect_intent(query: str) -> str:
    """
    Mengembalikan intent:
    - faq: pertanyaan informasi atau kebijakan
    - ticket_status: permintaan pengecekan tiket
    - unknown: query kosong
    """
    if not query or not query.strip():
        return "unknown"

    query_lower = query.lower()

    # Jika ada ID tiket, prioritaskan pengecekan tiket.
    if extract_ticket_id(query):
        return "ticket_status"

    ticket_keywords = [
        "status tiket",
        "cek tiket",
        "tiket saya",
        "ticket status",
        "check ticket",
    ]

    if any(keyword in query_lower for keyword in ticket_keywords):
        return "ticket_status"

    # Baseline: pertanyaan lainnya diarahkan ke RAG.
    return "faq"


def extract_ticket_id(query: str) -> str | None:
    """Mengambil ID dengan format TICKET-XXXX dari query."""
    match = re.search(r"\bTICKET-\d{4}\b", query, re.IGNORECASE)

    if match:
        return match.group(0).upper()

    return None


async def handle_query(query: str) -> dict:
    """
    Mendeteksi intent dan mengarahkan query ke komponen yang sesuai.
    """
    intent = await detect_intent(query)

    if intent == "unknown":
        return {
            "status": "error",
            "intent": "unknown",
            "data": "Silakan masukkan pertanyaan atau permintaan Anda.",
        }

    if intent == "ticket_status":
        ticket_id = extract_ticket_id(query)

        if not ticket_id:
            return {
                "status": "error",
                "intent": "ticket_status",
                "data": (
                    "Mohon sertakan ID tiket dengan format "
                    "TICKET-XXXX agar statusnya dapat diperiksa."
                ),
            }

        data = get_ticket_status(ticket_id)

        return {
            "status": "success",
            "intent": "ticket_status",
            "data": data,
        }

    if intent == "faq":
        data = await answer_from_knowledge_base(query)

        return {
            "status": "success",
            "intent": "faq",
            "data": data,
        }

    return {
        "status": "error",
        "intent": "unknown",
        "data": "Maaf, saya tidak memahami permintaan Anda.",
    }
