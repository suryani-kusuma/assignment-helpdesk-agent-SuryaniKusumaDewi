from app.rag import semantic_search


def test_semantic_search_returns_results():
    query = "Saya tidak bisa masuk VPN karena lupa kata sandi"

    results = semantic_search(query)

    # Pastikan hasil pencarian tidak kosong.
    assert len(results) > 0

    # Pastikan hasil memiliki informasi yang diperlukan.
    first_result = results[0]

    assert "question" in first_result
    assert "answer" in first_result
    assert "score" in first_result

    # Pastikan skor relevansi berupa angka.
    assert isinstance(first_result["score"], float)
