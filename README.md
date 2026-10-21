# Workflow Web Statistika Deskriptif

Aplikasi UTS Statistika berbasis Python dan Streamlit.

## Cara menjalankan
1. Pastikan Python 3.10 atau lebih baru terpasang.
2. Buka terminal/Command Prompt di folder proyek.
3. (Opsional, disarankan) Buat virtual environment:
   - Windows: `py -m venv .venv`
   - Windows: `.venv\\Scripts\\activate`
4. Instal dependensi:
   `pip install -r requirements.txt`
5. Jalankan aplikasi:
   `streamlit run app.py`
6. Browser akan membuka aplikasi lokal. Jika tidak terbuka otomatis, kunjungi alamat yang ditampilkan terminal, biasanya `http://localhost:8501`.

## Alur penggunaan
Dashboard → Unggah & Data → Analisis Statistik → Visualisasi → Ekspor Hasil.

## Catatan
- Format yang didukung: `.xlsx`, `.xls`, dan `.csv`.
- Kolom yang seluruh nilai terisinya dapat dikonversi ke angka akan tersedia sebagai variabel analisis.
- Nilai kosong/nonnumerik diabaikan saat perhitungan.
- Varians dan standar deviasi memakai rumus sampel (`ddof=1`).
