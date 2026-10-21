import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Statistika Deskriptif", page_icon="📊", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.6rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background: #f4f7fb; border: 1px solid #e5eaf2; padding: 14px; border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Statistika Deskriptif")
st.caption("Aplikasi interaktif untuk mengolah dataset dan merangkum statistik deskriptif.")

with st.sidebar:
    st.header("Navigasi")
    halaman = st.radio("Pilih halaman", ["Dashboard", "Unggah & Data", "Analisis Statistik", "Visualisasi", "Ekspor Hasil"])
    st.divider()
    st.caption("Format: Excel (.xlsx, .xls) dan CSV (.csv)")

if "df" not in st.session_state:
    st.session_state.df = None
if "hasil" not in st.session_state:
    st.session_state.hasil = None
if "variabel" not in st.session_state:
    st.session_state.variabel = []

def read_file(uploaded):
    name = uploaded.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded)
    return pd.read_excel(uploaded)

def hitung_statistik(df, kolom, pilih):
    rows = []
    for col in kolom:
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        row = {"Variabel": col}
        if "Jumlah data (N)" in pilih: row["N"] = int(s.count())
        if "Minimum" in pilih: row["Minimum"] = s.min() if len(s) else np.nan
        if "Maksimum" in pilih: row["Maksimum"] = s.max() if len(s) else np.nan
        if "Mean" in pilih: row["Mean"] = s.mean() if len(s) else np.nan
        if "Median" in pilih: row["Median"] = s.median() if len(s) else np.nan
        if "Modus" in pilih:
            modes = s.mode()
            row["Modus"] = ", ".join(map(str, modes.tolist())) if len(modes) else "Tidak ada"
        if "Varians" in pilih: row["Varians"] = s.var(ddof=1) if len(s) > 1 else np.nan
        if "Standar deviasi" in pilih: row["Standar deviasi"] = s.std(ddof=1) if len(s) > 1 else np.nan
        if "Kuartil (Q1, Q2, Q3)" in pilih:
            row["Q1"] = s.quantile(.25) if len(s) else np.nan
            row["Q2"] = s.quantile(.50) if len(s) else np.nan
            row["Q3"] = s.quantile(.75) if len(s) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)

if halaman == "Dashboard":
    st.subheader("Selamat datang!")
    st.write("Ikuti alur sederhana untuk mendapatkan ringkasan statistik dari data kamu.")
    c1, c2, c3 = st.columns(3)
    c1.metric("1", "Unggah data")
    c2.metric("2", "Pilih variabel")
    c3.metric("3", "Analisis & ekspor")
    st.markdown("### Workflow")
    st.markdown("""
    **Unggah dataset → Periksa tabel → Pilih variabel numerik → Pilih statistik → Lihat hasil dan grafik → Unduh laporan**
    """)
    st.info("Mulai dari halaman **Unggah & Data** di menu sebelah kiri.")
    st.markdown("### Fitur")
    st.write("- Membaca file Excel dan CSV")
    st.write("- Pratinjau data serta informasi data kosong")
    st.write("- Menghitung N, minimum, maksimum, mean, median, modus, varians, standar deviasi, dan kuartil")
    st.write("- Histogram dan boxplot")
    st.write("- Ekspor ringkasan ke CSV atau Excel")

elif halaman == "Unggah & Data":
    st.subheader("Unggah dataset")
    uploaded = st.file_uploader("Pilih file Excel atau CSV", type=["xlsx", "xls", "csv"])
    if uploaded is not None:
        try:
            df = read_file(uploaded)
            st.session_state.df = df
            st.session_state.hasil = None
            st.success(f"Dataset berhasil dimuat: {df.shape[0]} baris × {df.shape[1]} kolom.")
        except Exception as e:
            st.error(f"File gagal dibaca. Periksa format file. Detail: {e}")
    df = st.session_state.df
    if df is not None:
        st.markdown("### Pratinjau data")
        st.dataframe(df.head(100), use_container_width=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Jumlah baris", f"{df.shape[0]:,}")
        c2.metric("Jumlah kolom", f"{df.shape[1]:,}")
        c3.metric("Sel kosong", f"{int(df.isna().sum().sum()):,}")
        with st.expander("Ringkasan data kosong per kolom"):
            missing = df.isna().sum().rename("Jumlah kosong").to_frame()
            missing["Persentase (%)"] = (df.isna().mean() * 100).round(2)
            st.dataframe(missing, use_container_width=True)
    else:
        st.warning("Unggah dataset terlebih dahulu untuk melihat tabel.")

elif halaman == "Analisis Statistik":
    st.subheader("Analisis statistik deskriptif")
    df = st.session_state.df
    if df is None:
        st.warning("Unggah dataset terlebih dahulu di halaman **Unggah & Data**.")
    else:
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        # Tambahkan kolom numerik yang tersimpan sebagai teks jika seluruh nilai nonkosong bisa dikonversi.
        for col in df.columns:
            if col not in numeric_cols:
                converted = pd.to_numeric(df[col], errors="coerce")
                if df[col].notna().sum() > 0 and converted.notna().sum() == df[col].notna().sum():
                    numeric_cols.append(col)
        if not numeric_cols:
            st.error("Tidak ditemukan variabel numerik pada dataset.")
        else:
            variabel = st.multiselect("Pilih variabel yang dianalisis", numeric_cols, default=numeric_cols[:1])
            opsi = ["Jumlah data (N)", "Minimum", "Maksimum", "Mean", "Median", "Modus",
                    "Varians", "Standar deviasi", "Kuartil (Q1, Q2, Q3)"]
            pilihan = st.multiselect("Pilih ukuran statistik", opsi, default=opsi)
            if st.button("Hitung statistik", type="primary", disabled=not variabel or not pilihan):
                st.session_state.variabel = variabel
                st.session_state.hasil = hitung_statistik(df, variabel, pilihan)
            if st.session_state.hasil is not None:
                st.markdown("### Hasil analisis")
                st.dataframe(st.session_state.hasil, use_container_width=True, hide_index=True)
                st.caption("Varians dan standar deviasi menggunakan sampel (ddof = 1). Data kosong atau nilai nonnumerik diabaikan untuk perhitungan.")
            else:
                st.info("Pilih variabel dan ukuran statistik, lalu klik **Hitung statistik**.")

elif halaman == "Visualisasi":
    st.subheader("Visualisasi data")
    df = st.session_state.df
    if df is None:
        st.warning("Unggah dataset terlebih dahulu di halaman **Unggah & Data**.")
    else:
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        for col in df.columns:
            if col not in numeric_cols:
                converted = pd.to_numeric(df[col], errors="coerce")
                if df[col].notna().sum() > 0 and converted.notna().sum() == df[col].notna().sum():
                    numeric_cols.append(col)
        if not numeric_cols:
            st.error("Tidak ditemukan variabel numerik untuk divisualisasikan.")
        else:
            col = st.selectbox("Pilih variabel", numeric_cols)
            values = pd.to_numeric(df[col], errors="coerce").dropna()
            if values.empty:
                st.warning("Variabel ini tidak memiliki nilai numerik yang bisa ditampilkan.")
            else:
                tab1, tab2 = st.tabs(["Histogram", "Boxplot"])
                with tab1:
                    fig, ax = plt.subplots()
                    ax.hist(values, bins="auto", edgecolor="black")
                    ax.set_title(f"Histogram {col}")
                    ax.set_xlabel(col)
                    ax.set_ylabel("Frekuensi")
                    st.pyplot(fig)
                    plt.close(fig)
                with tab2:
                    fig, ax = plt.subplots()
                    ax.boxplot(values, vert=True)
                    ax.set_title(f"Boxplot {col}")
                    ax.set_ylabel(col)
                    st.pyplot(fig)
                    plt.close(fig)
            st.caption("Grafik dibuat dari nilai numerik; nilai kosong diabaikan.")

elif halaman == "Ekspor Hasil":
    st.subheader("Ekspor ringkasan")
    hasil = st.session_state.hasil
    if hasil is None:
        st.warning("Jalankan perhitungan terlebih dahulu di halaman **Analisis Statistik**.")
    else:
        st.dataframe(hasil, use_container_width=True, hide_index=True)
        csv_bytes = hasil.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ Unduh hasil CSV", data=csv_bytes, file_name="hasil_statistika_deskriptif.csv", mime="text/csv")
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            hasil.to_excel(writer, index=False, sheet_name="Ringkasan Statistik")
        st.download_button("⬇️ Unduh hasil Excel", data=output.getvalue(), file_name="hasil_statistika_deskriptif.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.caption("File yang diunduh berisi tabel ringkasan statistik yang sedang ditampilkan.")
