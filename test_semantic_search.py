
from app.rag import semantic_search

query = "Saya tidak bisa masuk VPN karena lupa kata sandi"

print("Pertanyaan:", query)
print("\nHasil pencarian FAQ:")

results = semantic_search(query)

for result in results:
    print("FAQ:", result["question"])
    print("Skor:", round(result["score"], 3))
    print("-" * 40)
