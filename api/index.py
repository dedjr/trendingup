import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="EV Sales & Real Range Tracker", layout="wide")

st.title("🔋 Dasbor Penjualan Bulanan & Real Range EV")
st.write("Memantau tren penjualan bulanan dan mengungkap jarak tempuh asli kendaraan listrik berdasarkan pengujian di YouTube.")

# --- 1. DATA PENJUALAN BULANAN (Silakan update angkanya setiap bulan) ---
def get_monthly_sales_data():
    data = {
        "Bulan": ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Ags", "Sep", "Okt", "Nov", "Des"],
        "Mobil Listrik": [1200, 1500, 2100, 1800, 2500, 3100, 3400, 4200, 4100, 4800, 5200, 6000],
        "Motor Listrik": [3500, 4100, 5000, 4800, 6200, 7500, 8100, 9500, 9200, 10500, 11200, 13000]
    }
    return pd.DataFrame(data)

# --- 2. DATABASE JARAK TEMPUH (KLAIM VS REAL YOUTUBE) ---
def get_range_data():
    # Angka Real YouTube diambil dari rata-rata reviewer otomotif Indonesia
    data = [
        {"Merek & Tipe": "Wuling Air EV Long Range", "Kategori": "Mobil", "Klaim Pabrik (km)": 300, "Real YouTube (km)": 230},
        {"Merek & Tipe": "Wuling Binguo 410km", "Kategori": "Mobil", "Klaim Pabrik (km)": 410, "Real YouTube (km)": 340},
        {"Merek & Tipe": "Hyundai Ioniq 5 Signature", "Kategori": "Mobil", "Klaim Pabrik (km)": 451, "Real YouTube (km)": 390},
        {"Merek & Tipe": "BYD Atto 3 Extended", "Kategori": "Mobil", "Klaim Pabrik (km)": 480, "Real YouTube (km)": 410},
        {"Merek & Tipe": "Neta V", "Kategori": "Mobil", "Klaim Pabrik (km)": 401, "Real YouTube (km)": 310},
        {"Merek & Tipe": "Omoda E5", "Kategori": "Mobil", "Klaim Pabrik (km)": 430, "Real YouTube (km)": 370},
        {"Merek & Tipe": "Alva One", "Kategori": "Motor", "Klaim Pabrik (km)": 70, "Real YouTube (km)": 50},
        {"Merek & Tipe": "Alva Cervo (2 Baterai)", "Kategori": "Motor", "Klaim Pabrik (km)": 125, "Real YouTube (km)": 95},
        {"Merek & Tipe": "Polytron Fox R", "Kategori": "Motor", "Klaim Pabrik (km)": 130, "Real YouTube (km)": 100},
        {"Merek & Tipe": "Gesits G1", "Kategori": "Motor", "Klaim Pabrik (km)": 50, "Real YouTube (km)": 38},
        {"Merek & Tipe": "Uwinfly T3", "Kategori": "Motor", "Klaim Pabrik (km)": 60, "Real YouTube (km)": 45},
        {"Merek & Tipe": "Honda EM1 e:", "Kategori": "Motor", "Klaim Pabrik (km)": 41, "Real YouTube (km)": 32},
        {"Merek & Tipe": "Yadea T9", "Kategori": "Motor", "Klaim Pabrik (km)": 100, "Real YouTube (km)": 75}
    ]
    return pd.DataFrame(data)

# ==========================================
# --- TAMPILAN DASHBOARD ---
# ==========================================

# 1. GRAFIK PENJUALAN BULANAN
st.subheader("📈 Tren Penjualan EV Bulanan")
df_sales = get_monthly_sales_data()
st.line_chart(df_sales.set_index("Bulan"), use_container_width=True)

st.write("---")

# 2. KOMPARASI JARAK TEMPUH (KLAIM VS REAL)
st.subheader("🏁 Real Range vs Klaim Brosur (Berdasarkan YouTube)")
st.write("Data ini dikompilasi dari hasil pengujian *real-world* hingga baterai habis oleh para *reviewer* di YouTube.")

df_range = get_range_data()

# Filter Interaktif
kategori_filter = st.radio("Pilih Kategori Kendaraan:", ["Semua", "Mobil", "Motor"], horizontal=True)
if kategori_filter != "Semua":
    df_range = df_range[df_range["Kategori"] == kategori_filter]

col1, col2 = st.columns([1, 1.2])

with col1:
    # Tabel Data
    st.dataframe(df_range.drop(columns=["Kategori"]), use_container_width=True, hide_index=True)

with col2:
    # Visualisasi Bar Chart Perbandingan
    chart_data = df_range.set_index("Merek & Tipe")[["Klaim Pabrik (km)", "Real YouTube (km)"]]
    st.bar_chart(chart_data, color=["#FF4B4B", "#00CC66"], use_container_width=True)

st.write("---")

# 3. LINK PENCARIAN YOUTUBE OTOMATIS
st.subheader("▶️ Validasi Video Pengujian di YouTube")
st.write("Klik merek di bawah ini untuk langsung mencari video pengetesan jarak tempuhnya:")

cols = st.columns(4)
for index, row in df_range.iterrows():
    model = row["Merek & Tipe"]
    # Membuat query pencarian otomatis ke YouTube
    query = f"test jarak tempuh asli {model} sampai habis".replace(" ", "+")
    youtube_url = f"https://www.youtube.com/results?search_query={query}"
    
    with cols[index % 4]:
        st.markdown(f"📺 **[{model}]({youtube_url})**")

