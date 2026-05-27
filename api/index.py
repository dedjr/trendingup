import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EV Market & Real Range Tracker", layout="wide")

st.title("🔋 Dasbor Market & Real Range EV")
st.write("Memantau sebaran merek motor listrik di Indonesia dan mengungkap jarak tempuh asli berdasarkan pengujian di YouTube.")

# --- 1. DATA MARKET SHARE MOTOR LISTRIK ---
def get_market_share_data():
    data = {
        "Merek": ["Gesits", "Alva", "Polytron", "Uwinfly", "Yadea", "Lainnya"],
        "Unit Beredar": [25000, 15000, 12000, 45000, 20000, 18000]
    }
    return pd.DataFrame(data)

# --- 2. DATABASE JARAK TEMPUH & SPESIFIKASI BATERAI ---
def get_range_data():
    data = [
        # Data Mobil
        {"Merek & Tipe": "Wuling Air EV Long", "Kategori": "Mobil", "Klaim Pabrik (km)": 300, "Real YouTube (km)": 230, "Tipe Baterai": "LFP", "Voltase (V)": "115.2", "Kapasitas (Ah)": "232"},
        {"Merek & Tipe": "Wuling Binguo", "Kategori": "Mobil", "Klaim Pabrik (km)": 410, "Real YouTube (km)": 340, "Tipe Baterai": "LFP", "Voltase (V)": "319.2", "Kapasitas (Ah)": "100"},
        {"Merek & Tipe": "Hyundai Ioniq 5", "Kategori": "Mobil", "Klaim Pabrik (km)": 451, "Real YouTube (km)": 390, "Tipe Baterai": "Li-ion NMC", "Voltase (V)": "697", "Kapasitas (Ah)": "111"},
        {"Merek & Tipe": "BYD Atto 3", "Kategori": "Mobil", "Klaim Pabrik (km)": 480, "Real YouTube (km)": 410, "Tipe Baterai": "LFP (Blade)", "Voltase (V)": "403.2", "Kapasitas (Ah)": "150"},
        {"Merek & Tipe": "Neta V", "Kategori": "Mobil", "Klaim Pabrik (km)": 401, "Real YouTube (km)": 310, "Tipe Baterai": "LFP", "Voltase (V)": "385", "Kapasitas (Ah)": "105"},
        {"Merek & Tipe": "Omoda E5", "Kategori": "Mobil", "Klaim Pabrik (km)": 430, "Real YouTube (km)": 370, "Tipe Baterai": "LFP", "Voltase (V)": "347", "Kapasitas (Ah)": "175"},
        
        # Data Motor
        {"Merek & Tipe": "Alva One", "Kategori": "Motor", "Klaim Pabrik (km)": 70, "Real YouTube (km)": 50, "Tipe Baterai": "Lithium", "Voltase (V)": "60", "Kapasitas (Ah)": "45"},
        {"Merek & Tipe": "Alva Cervo", "Kategori": "Motor", "Klaim Pabrik (km)": 125, "Real YouTube (km)": 95, "Tipe Baterai": "Li-NMC", "Voltase (V)": "73.8", "Kapasitas (Ah)": "48"},
        {"Merek & Tipe": "Polytron Fox R", "Kategori": "Motor", "Klaim Pabrik (km)": 130, "Real YouTube (km)": 100, "Tipe Baterai": "LFP", "Voltase (V)": "76.8", "Kapasitas (Ah)": "52"},
        {"Merek & Tipe": "Gesits G1", "Kategori": "Motor", "Klaim Pabrik (km)": 50, "Real YouTube (km)": 38, "Tipe Baterai": "Li-NMC", "Voltase (V)": "72", "Kapasitas (Ah)": "20"},
        {"Merek & Tipe": "Uwinfly T3", "Kategori": "Motor", "Klaim Pabrik (km)": 60, "Real YouTube (km)": 45, "Tipe Baterai": "SLA", "Voltase (V)": "60", "Kapasitas (Ah)": "20"},
        {"Merek & Tipe": "Honda EM1 e:", "Kategori": "Motor", "Klaim Pabrik (km)": 41, "Real YouTube (km)": 32, "Tipe Baterai": "Li-ion", "Voltase (V)": "50.2", "Kapasitas (Ah)": "26.1"},
        {"Merek & Tipe": "Yadea T9", "Kategori": "Motor", "Klaim Pabrik (km)": 100, "Real YouTube (km)": 75, "Tipe Baterai": "Graphene", "Voltase (V)": "72", "Kapasitas (Ah)": "38"}
    ]
    return pd.DataFrame(data)

# ==========================================
# --- TAMPILAN DASHBOARD ---
# ==========================================

# 1. GRAFIK MARKET SHARE MOTOR
st.subheader("📊 Populasi Merek Motor Listrik di Indonesia")
df_market = get_market_share_data()
fig_pie = px.pie(df_market, values='Unit Beredar', names='Merek', hole=0.4)
fig_pie.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
st.caption("Sumber Data: Estimasi Populasi Unit Industri (AISI/Data Pasar 2026)")

st.write("---")

# 2. KOMPARASI JARAK TEMPUH & VALIDASI
st.subheader("🏁 Real Range vs Klaim Brosur (Berdasarkan YouTube)")
df_range = get_range_data()
tab_motor, tab_mobil = st.tabs(["🏍️ Motor", "🚗 Mobil"])

def render_category_content(kategori, df_full, color_hex, icon):
    st.markdown(f"<h2 style='color: {color_hex}; margin-top: 0px;'>{icon} Kategori: {kategori} Listrik</h2>", unsafe_allow_html=True)
    
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
        styled_df = df_display.style.set_properties(**{'text-align': 'left'})\
                                    .set_table_styles([{'selector': 'th', 'props': [('text-align', 'left')]}])
        st.table(styled_df)
    
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
