import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app

client = TestClient(app)


def test_ask_handles_internal_error():
    with patch(
        "app.main.handle_query",
        new_callable=AsyncMock,
        side_effect=RuntimeError("Simulated test error"),
    ):
        response = client.post(
            "/ask",
            json={"query": "Tes error handling"},
        )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "error"
    assert result["intent"] == "unknown"
    assert "kendala" in result["data"].lower()