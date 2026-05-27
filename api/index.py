import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EV Sales & Real Range Tracker", layout="wide")

st.title("🔋 Dasbor Penjualan Bulanan & Real Range EV")
st.write("Memantau tren penjualan bulanan dan mengungkap jarak tempuh asli kendaraan listrik berdasarkan pengujian di YouTube.")

# --- 1. DATA PENJUALAN BULANAN ---
def get_monthly_sales_data():
    data = {
        "Bulan": ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Ags", "Sep", "Okt", "Nov", "Des"],
        "Mobil Listrik": [1200, 1500, 2100, 1800, 2500, 3100, 3400, 4200, 4100, 4800, 5200, 6000],
        "Motor Listrik": [3500, 4100, 5000, 4800, 6200, 7500, 8100, 9500, 9200, 10500, 11200, 13000]
    }
    return pd.DataFrame(data)

# --- 2. DATABASE JARAK TEMPUH & SPESIFIKASI BATERAI ---
def get_range_data():
    data = [
        # Data Mobil
        {"Merek & Tipe": "Wuling Air EV Long", "Kategori": "Mobil", "Klaim Pabrik (km)": 300, "Real YouTube (km)": 230, "Tipe Baterai": "LFP", "Voltase (V)": "115", "Kapasitas (Ah)": "232"},
        {"Merek & Tipe": "Wuling Binguo", "Kategori": "Mobil", "Klaim Pabrik (km)": 410, "Real YouTube (km)": 340, "Tipe Baterai": "LFP", "Voltase (V)": "319", "Kapasitas (Ah)": "100"},
        {"Merek & Tipe": "Hyundai Ioniq 5", "Kategori": "Mobil", "Klaim Pabrik (km)": 451, "Real YouTube (km)": 390, "Tipe Baterai": "Li-ion NMC", "Voltase (V)": "697", "Kapasitas (Ah)": "111"},
        {"Merek & Tipe": "BYD Atto 3", "Kategori": "Mobil", "Klaim Pabrik (km)": 480, "Real YouTube (km)": 410, "Tipe Baterai": "LFP (Blade)", "Voltase (V)": "403", "Kapasitas (Ah)": "150"},
        {"Merek & Tipe": "Neta V", "Kategori": "Mobil", "Klaim Pabrik (km)": 401, "Real YouTube (km)": 310, "Tipe Baterai": "LFP", "Voltase (V)": "385", "Kapasitas (Ah)": "105"},
        {"Merek & Tipe": "Omoda E5", "Kategori": "Mobil", "Klaim Pabrik (km)": 430, "Real YouTube (km)": 370, "Tipe Baterai": "LFP", "Voltase (V)": "347", "Kapasitas (Ah)": "175"},
        
        # Data Motor
        {"Merek & Tipe": "Alva One", "Kategori": "Motor", "Klaim Pabrik (km)": 70, "Real YouTube (km)": 50, "Tipe Baterai": "Lithium", "Voltase (V)": "60", "Kapasitas (Ah)": "45"},
        {"Merek & Tipe": "Alva Cervo", "Kategori": "Motor", "Klaim Pabrik (km)": 125, "Real YouTube (km)": 95, "Tipe Baterai": "Lithium", "Voltase (V)": "73.8", "Kapasitas (Ah)": "48"},
        {"Merek & Tipe": "Polytron Fox R", "Kategori": "Motor", "Klaim Pabrik (km)": 130, "Real YouTube (km)": 100, "Tipe Baterai": "LFP", "Voltase (V)": "72", "Kapasitas (Ah)": "52"},
        {"Merek & Tipe": "Gesits G1", "Kategori": "Motor", "Klaim Pabrik (km)": 50, "Real YouTube (km)": 38, "Tipe Baterai": "Li-NMC", "Voltase (V)": "72", "Kapasitas (Ah)": "20"},
        {"Merek & Tipe": "Uwinfly T3", "Kategori": "Motor", "Klaim Pabrik (km)": 60, "Real YouTube (km)": 45, "Tipe Baterai": "SLA (Aki)", "Voltase (V)": "60", "Kapasitas (Ah)": "20"},
        {"Merek & Tipe": "Honda EM1 e:", "Kategori": "Motor", "Klaim Pabrik (km)": 41, "Real YouTube (km)": 32, "Tipe Baterai": "Lithium-ion", "Voltase (V)": "50.2", "Kapasitas (Ah)": "29.4"},
        {"Merek & Tipe": "Yadea T9", "Kategori": "Motor", "Klaim Pabrik (km)": 100, "Real YouTube (km)": 75, "Tipe Baterai": "Graphene", "Voltase (V)": "72", "Kapasitas (Ah)": "38"}
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

# 2. KOMPARASI JARAK TEMPUH & VALIDASI (DIPISAH BERDASARKAN TAB)
st.subheader("🏁 Real Range vs Klaim Brosur (Berdasarkan YouTube)")

df_range = get_range_data()

# Membuat Tab UI
tab_mobil, tab_motor = st.tabs(["🚗 Mobil", "🏍️ Motor"])

# --- FUNGSI HELPER UNTUK MERENDER ISI TAB ---
def render_category_content(kategori, df_full, color_hex, icon):
    # 1. INJEKSI HTML UNTUK JUDUL BESAR & BERWARNA
    st.markdown(
        f"<h2 style='color: {color_hex}; margin-top: 0px;'>{icon} Kategori: {kategori} Listrik</h2>", 
        unsafe_allow_html=True
    )
    
    # 2. FILTER & SORTING DATA (Dari Jarak Tempuh Terbesar ke Terkecil)
    df_subset = df_full[df_full["Kategori"] == kategori].sort_values(by="Real YouTube (km)", ascending=False)
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        df_melt = df_subset.melt(id_vars=["Merek & Tipe"], 
                                 value_vars=["Klaim Pabrik (km)", "Real YouTube (km)"], 
                                 var_name="Jenis Data", value_name="Jarak (km)")
        
        # MENGUBAH GRAFIK MENJADI HORIZONTAL
        fig = px.bar(df_melt, x="Jarak (km)", y="Merek & Tipe", color="Jenis Data", barmode="group",
                     orientation='h',
                     color_discrete_map={"Klaim Pabrik (km)": "#3366CC", "Real YouTube (km)": "#00CC66"},
                     text_auto=True)
        
        fig.update_layout(
            xaxis_title="Jarak Tempuh (km)", 
            yaxis_title=None, 
            legend_title=None
        )
        
        fig.update_yaxes(autorange="reversed")
        
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # 3. SETTING TABEL SPESIFIKASI BATERAI (RATA KIRI)
        # Menghapus kolom kategori & angka km, hanya menampilkan data teknis baterai
        df_display = df_subset[["Merek & Tipe", "Tipe Baterai", "Voltase (V)", "Kapasitas (Ah)"]].reset_index(drop=True)
        
        styled_df = df_display.style.set_properties(**{'text-align': 'left'})\
                                    .set_table_styles([{'selector': 'th', 'props': [('text-align', 'left')]}])
        
        st.dataframe(styled_df, use_container_width=True)
    
    st.write("---")
    
    # Bagian Validasi Link YouTube
    st.markdown(f"### ▶️ Validasi Video Pengujian {kategori}")
    cols = st.columns(4)
    for index, row in df_subset.reset_index().iterrows():
        model = row["Merek & Tipe"]
        query = f"test jarak tempuh asli {model} sampai habis".replace(" ", "+")
        youtube_url = f"https://www.youtube.com/results?search_query={query}"
        
        with cols[index % 4]:
            st.markdown(f"📺 **[{model}]({youtube_url})**")

# --- MENGISI KONTEN MASING-MASING TAB ---
with tab_mobil:
    render_category_content("Mobil", df_range, "#3366CC", "🚙")

with tab_motor:
    render_category_content("Motor", df_range, "#FF4B4B", "🛵")
