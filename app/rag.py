"""
Modul RAG — mengubah knowledge base menjadi embedding, menyimpannya ke FAISS,
melakukan semantic search, lalu menghasilkan jawaban menggunakan LLM.

Alur ini serupa dengan yang sudah dibangun di Assignment 3 (Semantic Search &
LLM Application) dan Sesi 11 (Building a Simple RAG System) — di assignment ini,
alur tersebut dibungkus menjadi fungsi yang dipanggil oleh router.py.
"""

import os
from pathlib import Path

import pandas as pd
import numpy as np
import faiss
from dotenv import load_dotenv
from google import genai  # sesuaikan dengan library Gemini API yang digunakan
from google.genai import types

# Membaca konfigurasi dari .env
load_dotenv()

# Menentukan lokasi project berdasarkan posisi file rag.py
BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_PATH = (BASE_DIR / "data" / "it_helpdesk_knowledge_base.csv")

# 🔧 TODO: muat knowledge base dan bangun index FAISS saat aplikasi startup
# (bukan di setiap request), agar lebih efisien. Pertimbangkan menggunakan
# FastAPI startup event atau lazy-loading dengan cache sederhana.

EMBEDDING_MODEL = "gemini-embedding-001"
GENERATION_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
EMBEDDING_DIMENSION = 768

_client = None
_index = None
_documents = None
_df = None

def _get_client():
    """Membuat Gemini client saat dibutuhkan."""
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY tidak ditemukan. "
                "Periksa file .env."
            )

        _client = genai.Client(api_key=api_key)

    return _client

def _get_embedding(text: str) -> np.ndarray:
    """Mengubah teks menjadi vektor embedding."""
    result = _get_client().models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSION
        ),
    )

    if not result.embeddings:
        raise RuntimeError("Embedding tidak berhasil dibuat.")

    return np.asarray(
        result.embeddings[0].values,
        dtype=np.float32,
    )


def build_index():
    """Membaca FAQ dan membangun index FAISS."""
    global _index, _documents, _df

    # Mencegah index dibangun berulang kali dalam proses yang sama.
    if _index is not None:
        return

    if not KNOWLEDGE_BASE_PATH.exists():
        raise FileNotFoundError(
            f"File tidak ditemukan: {KNOWLEDGE_BASE_PATH}"
        )

    df = pd.read_csv(KNOWLEDGE_BASE_PATH)

    required_columns = {"question", "answer"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Kolom CSV tidak tersedia: {missing_columns}"
        )

    df = df.dropna(subset=["question", "answer"]).copy()

    if df.empty:
        raise ValueError("Knowledge base kosong.")

    documents = []

    for _, row in df.iterrows():
        category = str(row.get("category", "General"))
        question = str(row["question"])
        answer = str(row["answer"])

        document = (
            f"Category: {category}\n"
            f"Question: {question}\n"
            f"Answer: {answer}"
        )

        documents.append(document)

    vectors = []

    for i, document in enumerate(documents, start=1):
        print(f"Membuat embedding FAQ {i}/{len(documents)}...")
        vectors.append(_get_embedding(document))

    matrix = np.vstack(vectors).astype(np.float32)

    # Normalisasi agar inner product dapat digunakan
    # sebagai ukuran cosine similarity.
    faiss.normalize_L2(matrix)

    index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)
    index.add(matrix)

    # Menyimpan hasil hanya setelah index berhasil dibuat.
    _index = index
    _documents = documents
    _df = df.reset_index(drop=True)

    print(f"Index FAISS siap: {_index.ntotal} FAQ.")



def semantic_search(query: str, top_k: int = 3):
    """Mencari FAQ yang paling relevan dengan pertanyaan."""
    if not query or not query.strip():
        raise ValueError("Query tidak boleh kosong.")

    if top_k < 1:
        raise ValueError("top_k harus minimal 1.")

    build_index()

    query_vector = _get_embedding(query).reshape(1, -1)
    faiss.normalize_L2(query_vector)

    k = min(top_k, _index.ntotal)
    scores, indices = _index.search(query_vector, k)

    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue

        row = _df.iloc[int(idx)]

        results.append({
            "faq_id": str(row.get("faq_id", "")),
            "category": str(row.get("category", "General")),
            "question": str(row["question"]),
            "answer": str(row["answer"]),
            "score": float(score),
            "document": _documents[int(idx)],
        })

    return results


async def answer_from_knowledge_base(query: str) -> str:
    """Mencari konteks FAQ dan menghasilkan jawaban Gemini."""
    results = semantic_search(query, top_k=3)

    if not results:
        return (
            "Maaf, informasi yang relevan belum ditemukan "
            "dalam knowledge base."
        )

    context = "\n\n".join(
        (
            f"FAQ {i}:\n"
            f"Category: {item['category']}\n"
            f"Question: {item['question']}\n"
            f"Answer: {item['answer']}"
        )
        for i, item in enumerate(results, start=1)
    )

    prompt = f"""
PERSONA:
Kamu adalah IT Helpdesk Assistant yang membantu karyawan.

TASK:
Jawab pertanyaan pengguna berdasarkan konteks knowledge base.

CONTEXT:
{context}

USER QUESTION:
{query}

FORMAT:
- Gunakan bahasa yang sama dengan pertanyaan pengguna.
- Berikan jawaban yang jelas dan mudah dipahami.
- Gunakan konteks sebagai sumber informasi.
- Jangan mengarang kebijakan atau fakta.
- Jika konteks tidak cukup, jelaskan bahwa informasi belum tersedia.
"""

    response = await _get_client().aio.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
    )

    answer = response.text

    if not answer or not answer.strip():
        raise RuntimeError("Gemini tidak menghasilkan jawaban.")

    return answer.strip()