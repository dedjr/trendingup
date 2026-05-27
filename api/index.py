import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EV Market & Real Range Tracker", layout="wide")

st.title("🔋 Dasbor Market & Real Range EV")
st.write("Memantau sebaran merek motor listrik di Indonesia dan mengungkap jarak tempuh asli berdasarkan pengujian di YouTube.")

# --- 1. DATA MARKET SHARE MOTOR LISTRIK (Tetap Statis) ---
def get_market_share_data():
    data = {
        "Merek": ["Gesits", "Alva", "Polytron", "Uwinfly", "Yadea", "Lainnya"],
        "Unit Beredar": [25000, 15000, 12000, 45000, 20000, 18000]
    }
    return pd.DataFrame(data)

# --- 2. DATABASE DARI GOOGLE SHEETS ---
# Link sudah dikonversi ke format CSV agar terbaca oleh Pandas
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT_QqQI7h4687I-0r9z_JYeyIc_wtDcuH2PuOnmlgU9IZ8OMFENMSGGLWPsHZ0Z4IJz72O0rxXGMqgz/pub?output=csv"

@st.cache_data(ttl=600) # Data di-refresh setiap 10 menit
def get_range_data():
    return pd.read_csv(SHEET_URL)

# ==========================================
# --- TAMPILAN DASHBOARD ---
# ==========================================

# 1. GRAFIK MARKET SHARE
st.subheader("📊 Populasi Merek Motor Listrik di Indonesia")
df_market = get_market_share_data()
fig_pie = px.pie(df_market, values='Unit Beredar', names='Merek', hole=0.4)
fig_pie.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
st.caption("Sumber Data: Estimasi Populasi Unit Industri (AISI/Data Pasar 2026)")

st.write("---")

# 2. KOMPARASI JARAK TEMPUH & VALIDASI
st.subheader("🏁 Real Range vs Klaim Brosur (Data dari Google Sheets)")
try:
    df_range = get_range_data()
    tab_motor, tab_mobil = st.tabs(["🏍️ Motor", "🚗 Mobil"])

    def render_category_content(kategori, df_full, color_hex, icon):
        st.markdown(f"<h2 style='color: {color_hex}; margin-top: 0px;'>{icon} Kategori: {kategori} Listrik</h2>", unsafe_allow_html=True)
        
        # Filter berdasarkan kategori
        df_subset = df_full[df_full["Kategori"] == kategori].sort_values(by="Real YouTube (km)", ascending=False)
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            df_melt = df_subset.melt(id_vars=["Merek & Tipe"], value_vars=["Klaim Pabrik (km)", "Real YouTube (km)"], var_name="Jenis Data", value_name="Jarak (km)")
            fig = px.bar(df_melt, x="Jarak (km)", y="Merek & Tipe", color="Jenis Data", barmode="group",
                         orientation='h', color_discrete_map={"Klaim Pabrik (km)": "#3366CC", "Real YouTube (km)": "#00CC66"},
                         text_auto=True)
            fig.update_layout(xaxis_title="Jarak Tempuh (km)", yaxis_title=None, legend_title=None, dragmode=False)
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': False, 'doubleClick': False})

        with col2:
            df_display = df_subset[["Merek & Tipe", "Tipe Baterai", "Voltase (V)", "Kapasitas (Ah)"]].reset_index(drop=True)
            st.table(df_display)
        
        st.write("---")
        st.markdown(f"### ▶️ Validasi Video Pengujian {kategori}")
        cols = st.columns(4)
        for index, row in df_subset.reset_index().iterrows():
            model = row["Merek & Tipe"]
            query = f"test jarak tempuh asli {model} sampai habis".replace(" ", "+")
            with cols[index % 4]:
                st.markdown(f"📺 **[{model}](https://www.youtube.com/results?search_query={query})**")

    with tab_motor:
        render_category_content("Motor", df_range, "#FF4B4B", "🛵")
    with tab_mobil:
        render_category_content("Mobil", df_range, "#3366CC", "🚙")

except Exception as e:
    st.error("Gagal memuat data dari Google Sheets. Pastikan format kolom di Sheets sesuai dengan kode.")
