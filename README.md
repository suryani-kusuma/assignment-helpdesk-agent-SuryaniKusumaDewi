# IT Helpdesk Assistant - End-to-End RAG & AI Agent
## 1. Deskripsi Project
IT Helpdesk Assistant adalah aplikasi berbasis AI yang membantu karyawan memperoleh informasi terkait kebijakan dan panduan IT serta memeriksa status tiket bantuan IT.

Project ini dibuat sebagai bagian dari **AI Engineering Bootcamp — Assignment 4: End-to-End RAG & AI Agent Development / Cloud Deployment & Containerization for AI**.

Aplikasi mengintegrasikan dua kemampuan utama:

- **Retrieval-Augmented Generation (RAG):** menjawab pertanyaan informasi atau kebijakan berdasarkan knowledge base yang tersedia.

- **Workflow Routing dan Tool Call:** mengenali permintaan pengecekan status tiket dan mengambil data tiket secara langsung.

Seluruh workflow dibungkus dalam backend API menggunakan FastAPI dan dijalankan dalam container Docker.

## 2. Objective dan Problem Statement
Tim People & IT Operations menerima banyak pertanyaan berulang dari karyawan. Sebagian pertanyaan berkaitan dengan informasi umum yang dapat dijawab berdasarkan dokumen, sedangkan sebagian lainnya memerlukan pengambilan data spesifik.

Tujuan project ini adalah membangun backend API yang dapat membedakan kedua jenis permintaan tersebut dan mengarahkannya ke komponen yang sesuai.

### Jenis permintaan pengguna
**1. FAQ / Informasi**

Contoh: "Bagaimana cara reset password VPN perusahaan?"

Permintaan ini diproses melalui RAG. Sistem mencari informasi yang relevan dari knowledge base, kemudian menggunakan Gemini untuk menyusun jawaban berdasarkan konteks yang ditemukan.

**2. Pengecekan status tiket**

Contoh: "Cek status tiket TICKET-0001."

Permintaan ini diproses melalui tool call. Sistem mengambil data tiket berdasarkan ID dari file `mock_tickets.csv`, bukan menggunakan semantic search untuk menentukan status tiket.

## 3. Teknologi yang Digunakan
- Python

- FastAPI

- Google Gemini API

- FAISS untuk pencarian vektor

- Pandas untuk membaca data CSV

- Uvicorn sebagai ASGI server

- Docker untuk containerization

- Git dan GitHub untuk version control dan pengumpulan project

## 4. Struktur Project
```text

it-helpdesk-assignment/

├── app/

│   ├── main.py

│   ├── router.py

│   ├── rag.py

│   └── tools.py

├── data/

│   ├── it_helpdesk_knowledge_base.csv

│   └── mock_tickets.csv

├── .dockerignore

├── .env.example

├── .gitignore

├── Dockerfile

├── requirements.txt

├── README.md

├── test_error_handling.py

├── test_semantic_search.py

└── test_tools.py

```

## 5. Desain Workflow Aplikasi
Alur kerja aplikasi:

```text

User Query

    |

    v

FastAPI Endpoint (/ask)

    |

    v

Intent Detection (Router)

    |

    +-----------------------+

    |                       |

    v                       v

  FAQ Path             Ticket Status Path

    |                       |

    v                       v

Semantic Search        Extract Ticket ID

    |                       |

    v                       v

Retrieve Relevant      Read mock_tickets.csv

Knowledge Base              |

    |                       |

    v                       v

Gemini Generates       Return Ticket Information

Answer                      |

    |                       |

    +-----------+-----------+

                |

                v

       Structured Response

       status, intent, data

```

### Kriteria intent
- **`faq`:** pertanyaan informasi atau kebijakan yang diarahkan ke komponen RAG.

- **`ticket_status`:** permintaan pengecekan tiket yang dikenali melalui ID tiket atau keyword terkait tiket.

- **`unknown`:** input kosong atau hanya berisi spasi yang tidak dapat diproses sebagai permintaan.

Router menggunakan pendekatan berbasis keyword sebagai baseline. Saat ini, pertanyaan non-tiket umumnya diarahkan ke RAG, sehingga pertanyaan di luar cakupan belum memiliki intent khusus.

## 6. Implementasi RAG
RAG digunakan untuk menjawab pertanyaan berdasarkan informasi dalam `data/it_helpdesk_knowledge_base.csv`.

Tahapan proses:

1. Membaca knowledge base yang berisi 31 FAQ.

2. Mengubah teks menjadi embedding menggunakan Gemini Embedding API.

3. Membangun FAISS index untuk menyimpan dan mencari vektor.

4. Melakukan semantic search untuk menemukan FAQ yang paling relevan dengan pertanyaan pengguna.

5. Menggunakan hasil retrieval sebagai konteks bagi Gemini untuk menghasilkan jawaban.

Semantic search membantu menemukan informasi yang relevan berdasarkan kemiripan makna, meskipun pengguna menggunakan susunan kata yang berbeda dari pertanyaan dalam knowledge base.

## 7. Implementasi Tool Call
Fungsi `get_ticket_status()` pada `app/tools.py` digunakan untuk mengambil data tiket dari `data/mock_tickets.csv`.

Prosesnya:

1. Router mengenali permintaan pengecekan tiket.

2. Sistem mengekstrak ID tiket dari query pengguna.

3. Fungsi tool mencari ID tersebut di data tiket.

4. Jika ditemukan, aplikasi mengembalikan informasi tiket.

5. Jika tidak ditemukan, aplikasi mengembalikan pesan bahwa tiket tidak ditemukan.

Pendekatan ini memastikan informasi status tiket diambil dari sumber data, bukan dibuat berdasarkan jawaban generatif model.

## 8. Backend API
Aplikasi menyediakan endpoint berikut:
| Endpoint | Method | Fungsi |
|---|---|---|
| `/health` | GET | Memeriksa status aplikasi |
| `/ask` | POST | Memproses pertanyaan pengguna melalui router |

Endpoint `/ask` menerima query dan mengembalikan respons terstruktur dengan field:

- `status`: status pemrosesan permintaan.

- `intent`: intent yang terdeteksi oleh router.

- `data`: jawaban FAQ, informasi tiket, atau pesan terkait hasil pemrosesan.

Dokumentasi interaktif FastAPI tersedia melalui `/docs` ketika aplikasi berjalan.

### Error Handling

Endpoint `/ask` menggunakan penanganan error dasar untuk mengantisipasi kegagalan saat memproses permintaan. Jika terjadi exception yang tidak tertangani, aplikasi mengembalikan respons terstruktur dengan `status: error`, `intent: unknown`, dan pesan umum agar pengguna dapat mencoba kembali. Detail error dicatat di terminal untuk membantu debugging.

Untuk pengecekan tiket yang tidak ditemukan, aplikasi mengembalikan pesan informatif dari fungsi tool. Input kosong juga ditangani oleh router. Penanganan error ini merupakan mekanisme dasar dan belum membedakan setiap jenis kegagalan teknis secara spesifik.

## 9. Konfigurasi Environment Variables
Aplikasi menggunakan environment variables untuk menyimpan konfigurasi API key dan model.

File `.env.example` menyediakan contoh variabel yang dibutuhkan:

```dotenv

GEMINI_API_KEY=

GEMINI_MODEL=gemini-3.5-flash-lite

```

Jika file `.env` belum tersedia, salin `.env.example` menjadi `.env`, lalu isi `GEMINI_API_KEY` dengan API key milik sendiri.

File `.env` tidak boleh diunggah ke GitHub. File tersebut dikecualikan dari Git melalui `.gitignore` dan dari Docker build context melalui `.dockerignore`.

## 10. Menjalankan Aplikasi Secara Lokal
Pastikan Python dan dependencies tersedia.

### 10.1 Instalasi dependencies
Aktifkan virtual environment jika digunakan, kemudian jalankan:

```powershell

pip install -r requirements.txt

```

### 10.2 Konfigurasi environment
Salin file contoh konfigurasi:

```powershell

Copy-Item .env.example .env

```

Isi API key dan pastikan konfigurasi model sesuai dengan yang digunakan oleh aplikasi.

### 10.3 Menjalankan server
```powershell

python -m uvicorn app.main:app --reload

```

Aplikasi berjalan pada:

`http://127.0.0.1:8000`

Periksa status aplikasi:

```powershell

Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"

```

### 10.4 Menguji endpoint `/ask`
Contoh pengecekan status tiket:

```powershell

$body = @{
    query = "Cek status tiket TICKET-0001"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/ask" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

```

## 11. Menjalankan Aplikasi dengan Docker
Pastikan Docker Desktop aktif dan file `.env` tersedia di folder utama project.

### 11.1 Build image
```powershell

docker build -t it-helpdesk-assistant .

```

### 11.2 Menjalankan container
```powershell

docker run --env-file .env -p 8000:8000 --name it-helpdesk-container it-helpdesk-assistant

```

Aplikasi dapat diakses dari komputer melalui `http://127.0.0.1:8000`.

### 11.3 Menguji endpoint di Docker
Periksa health check:

```powershell

Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"

```

Uji FAQ dan pengecekan tiket melalui endpoint `/ask` menggunakan contoh perintah pada bagian sebelumnya.

## 12. Hasil Pengujian dan Observasi
Pengujian berikut telah dilakukan melalui endpoint `/ask` pada aplikasi yang berjalan di Docker.

| No. | Skenario | Query | Hasil |
|---|---|---|---|
| 1 | Tiket tersedia | `Cek status tiket TICKET-0001` | Berhasil. Intent `ticket_status`; informasi tiket dikembalikan. |
| 2 | Tiket tidak ditemukan | `Cek status tiket TICKET-9999` | Berhasil diproses. Aplikasi menyampaikan bahwa tiket tidak ditemukan. |
| 3 | Pertanyaan FAQ | `Bagaimana cara reset password VPN perusahaan?` | Berhasil. Intent `faq`; jawaban terkait reset password VPN dihasilkan. |
| 4 | Pertanyaan FAQ dengan ungkapan berbeda | `Saya lupa kata sandi VPN dan tidak bisa masuk` | Berhasil. Intent `faq`; sistem menghasilkan jawaban relevan melalui jalur RAG. |
| 5 | Pertanyaan di luar cakupan | `Tolong buatkan jadwal liburan ke Bali` | Aplikasi menyatakan bahwa informasi tersebut tidak tersedia dalam knowledge base. |

### Observasi hasil pengujian
- Endpoint `/health` mengembalikan `status: ok`.

- Permintaan pengecekan tiket diarahkan ke tool call dan data diambil dari CSV.

- ID tiket yang tidak tersedia ditangani dengan pesan informatif.

- Pertanyaan FAQ diarahkan ke RAG dan menghasilkan jawaban melalui Gemini.

- Pertanyaan dengan susunan kata berbeda tetap dapat memperoleh jawaban relevan melalui semantic search.

- Pertanyaan di luar cakupan belum dikenali sebagai intent terpisah. Router mengarahkannya ke RAG, sehingga sistem masih bergantung pada kemampuan retrieval dan respons model untuk menyatakan keterbatasan informasi.

### Automated Testing

Automated testing dilakukan menggunakan `pytest` untuk memeriksa beberapa fungsi utama aplikasi.

| File Test | Skenario | Hasil |
|---|---|---|
| `test_error_handling.py` | Memastikan endpoint `/ask` menangani simulasi error internal dengan respons terstruktur. | PASSED |
| `test_semantic_search.py` | Memastikan semantic search menghasilkan FAQ dengan informasi dan skor relevansi. | PASSED |
| `test_tools.py` | Memastikan fungsi pengecekan tiket menangani tiket yang tersedia dan tidak ditemukan. | 2 PASSED |

Seluruh 4 automated test berhasil dijalankan menggunakan perintah:

```powershell
python -m pytest -v
```

Pengujian ini melengkapi pengujian endpoint yang dilakukan sebelumnya. Cakupan automated test masih terbatas pada skenario yang telah didefinisikan dan belum mencakup seluruh kemungkinan kondisi aplikasi.

## 13. Keterbatasan Sistem
- Knowledge base dan data tiket masih menggunakan dataset CSV yang disediakan sebagai data simulasi.

- Router menggunakan pendekatan keyword sederhana dan belum menggunakan model klasifikasi intent khusus.

- Pertanyaan di luar cakupan belum memiliki intent khusus.

- Jawaban generatif dapat mengandung kesalahan penulisan atau informasi yang kurang tepat, sehingga kualitas jawaban perlu dievaluasi.

- FAISS index dibangun di memori saat aplikasi berjalan dan belum menggunakan penyimpanan indeks persisten.

- Aplikasi belum terhubung dengan sistem tiket perusahaan yang sebenarnya.

- Aplikasi dijalankan secara lokal menggunakan Docker dan belum di-deploy ke cloud, sesuai cakupan assignment.

## 14. Kesimpulan
IT Helpdesk Assistant berhasil mengintegrasikan Retrieval-Augmented Generation (RAG), semantic search menggunakan FAISS, Gemini API, tool call untuk pengecekan status tiket, dan backend API FastAPI.

Pengujian lokal menggunakan Docker menunjukkan bahwa aplikasi dapat menjalankan health check, menjawab pertanyaan FAQ, mengambil informasi tiket yang tersedia, menangani ID tiket yang tidak ditemukan, serta memberikan respons untuk pertanyaan di luar cakupan knowledge base.

Project ini mendemonstrasikan alur dasar pengembangan aplikasi AI end-to-end, mulai dari penerimaan query, penentuan intent, retrieval atau tool call, hingga menghasilkan respons melalui API yang dijalankan dalam container Docker.
