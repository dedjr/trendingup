import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from collections import Counter
import re

st.set_page_config(page_title="Global-Local EV & Battery Trend", layout="wide")

st.title("🔋 Global-Local EV & Battery Tech Trend Detector")
st.write("Memantau tren Kendaraan Listrik & Baterai dari Media (Antara, CNBC, Xinhua) dan Data Penjualan Nasional.")

# --- DAFTAR MEREK CHINA ---
china_car_brands = ["byd", "wuling", "chery", "neta", "aion", "gwm", "baic", "omoda", "binguo", "cloudev"]
china_bike_brands = ["yadea", "aima", "sunra", "davigo", "viar", "zongshen"]
all_china_brands = china_car_brands + china_bike_brands

# --- DATA PENJUALAN GAIKINDO & AISI (Data Historis Tahunan) ---
def get_sales_data():
    # Data rekapitulasi disederhanakan berdasarkan laporan Gaikindo (Mobil) dan AISI (Motor)
    data = {
        "Tahun": ["2022", "2023", "2024", "2025", "2026 (Est)"],
        "Mobil Listrik (Unit)": [10327, 17051, 38000, 75000, 110000],
        "Motor Listrik (Unit)": [15000, 47000, 115000, 280000, 450000]
    }
    return pd.DataFrame(data)

# Fungsi penerjemah otomatis
def translate_to_id(text):
    if not text:
        return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=id&dt=t&q={requests.utils.quote(text)}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            result = response.json()
            translated_text = "".join([sentence[0] for sentence in result[0] if sentence[0]])
            return translated_text
    except Exception:
        pass
    return text 

# 1. FUNGSI AMBIL DATA MULTI-MEDIA
@st.cache_data(ttl=1800)
def fetch_global_local_news():
    sources = {
        "Antara Otomotif": "https://www.antaranews.com/rss/otomotif.xml",
        "Antara Tekno": "https://www.antaranews.com/rss/tekno.xml",
        "Antara Ekonomi": "https://www.antaranews.com/rss/ekonomi-bisnis.xml",
        "CNBC Industri": "https://www.cnbcindonesia.com/news/rss",
        "Xinhua China (Sci-Tech)": "https://www.xinhuanet.com/english/rss/scitechrss.xml"
    }
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    articles = []
    
    for name, url in sources.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    desc = item.find('description').text if item.find('description') is not None else ""
                    link = item.find('link').text if item.find('link') is not None else ""
                    
                    if "Xinhua" in name:
                        title = translate_to_id(title)
                        desc = translate_to_id(desc)
                        
                    articles.append({
                        "title": title, 
                        "description": desc, 
                        "link": link,
                        "source": name
                    })
        except Exception:
            continue
    return articles

# 2. FUNGSI ANALISIS TEKS
def analyze_ev_trends(articles):
    all_words = []
    categorized_data = {
        "Mobil Listrik (EV)": 0,
        "Motor Listrik (EV Roda Dua)": 0,
        "Teknologi Baterai (LFP/Lithium)": 0,
        "Pabrikan China di Indonesia": 0,
        "Infrastruktur & Komponen": 0
    }
    
    # KATA DIBUANG: "menetapkan", "listrik" (karena akan digabung dengan mobil/motor)
    stopwords = {
        "dan", "yang", "di", "ke", "dari", "ini", "itu", "untuk", "dengan", "adalah", "dalam", 
        "bisa", "pada", "juga", "sudah", "ada", "raya", "jakarta", "indonesia", "tahun", "bulan",
        "hari", "menurut", "mengatakan", "bahwa", "tersebut", "akan", "banyak", "menjadi", "kamis",
        "selasa", "rabu", "senin", "jumat", "sabtu", "minggu", "berita", "mengungkapkan", "dilansir",
        "menetapkan", "listrik" 
    }

    for art in articles:
        text = (art['title'] + " " + art['description']).lower()
        
        # Klasifikasi Kategori
        if any(w in text for w in all_china_brands) or "china" in text or "tiongkok" in text:
            if any(x in text for x in ["motor", "roda dua", "yadea", "aima", "sunra", "davigo"]):
                categorized_data["Motor Listrik (EV Roda Dua)"] += 1
            elif any(x in text for x in ["listrik", "ev", "baterai", "mobil", "pabrik"]):
                categorized_data["Pabrikan China di Indonesia"] += 1
            else:
                categorized_data["Infrastruktur & Komponen"] += 1
        elif any(w in text for w in ["mobil listrik", "ev", "hyundai", "tesla", "ioniq", "toyota"]):
            categorized_data["Mobil Listrik (EV)"] += 1
        elif any(w in text for w in ["motor listrik", "moped", "gesits", "alva", "polytron", "honda"]):
            categorized_data["Motor Listrik (EV Roda Dua)"] += 1
        elif any(w in text for w in ["baterai", "battery", "lfp", "lifepo4", "lithium", "ncm", "solid-state", "sel", "pack"]):
            categorized_data["Teknologi Baterai (LFP/Lithium)"] += 1
        else:
            categorized_data["Infrastruktur & Komponen"] += 1

        # Ekstraksi Kata Kunci
        words = re.findall(r'\b\w+\b', text)
        for word in words:
            if len(word) > 2 and word not in stopwords and not word.isdigit():
                
                # NORMALISASI KATA KUNCI (Mengganti kata tunggal menjadi frasa)
                if word == "mobil":
                    word = "mobil listrik"
                elif word in ["motor", "motors"]:
                    word = "motor listrik"
                elif word in ["baterai", "battery"]:
                    word = "baterai"
                elif word in ["china", "tiongkok"]:
                    word = "china"

                valid_keywords = ["mobil listrik", "motor listrik", "ev", "lfp", "lifepo", "lithiu", "charg", "nikel", "china"] + all_china_brands
                
                if any(k in word for k in valid_keywords) or word == "baterai":
                    all_words.append(word)
                
    return Counter(all_words).most_common(10), categorized_data

# --- RUN APLIKASI ---
# 1. Menampilkan Grafik Penjualan (Data Statis Gaikindo/AISI)
st.subheader("📈 Tren Penjualan EV Indonesia (Data Gaikindo & AISI)")
df_sales = get_sales_data()
st.line_chart(df_sales.set_index("Tahun"), use_container_width=True)
with st.expander("Lihat Tabel Data Penjualan (Unit)"):
    st.dataframe(df_sales, use_container_width=True)

st.write("---")

# 2. Menampilkan Analitik Berita Real-time
data_berita = fetch_global_local_news()

if data_berita:
    top_words, categories = analyze_ev_trends(data_berita)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Kata Kunci Terhangat")
        if top_words:
            df_words = pd.DataFrame(top_words, columns=['Kata Kunci', 'Frekuensi'])
            st.bar_chart(df_words.set_index('Kata Kunci'))
            st.dataframe(df_words, use_container_width=True)
        else:
            st.info("Belum ada kata kunci spesifik EV yang mendominasi saat ini.")
        
    with col2:
        st.subheader("📁 Pembagian Sektor Tren")
        df_cat = pd.DataFrame(list(categories.items()), columns=['Sektor', 'Jumlah Berita'])
        st.bar_chart(df_cat.set_index('Sektor'), color="#00CC66")
        st.dataframe(df_cat, use_container_width=True)

    # 3. Menampilkan Feed Berita Terkait
    st.write("---")
    st.subheader("📰 Feed Berita Terintegrasi")
    
    keywords_filter = ["listrik", "baterai", "ev", "motor", "mobil", "china", "tiongkok", "battery"] + all_china_brands
    ev_articles = [a for a in data_berita if any(w in (a['title'] + a['description']).lower() for w in keywords_filter)]
    
    if ev_articles:
        for art in ev_articles[:15]: 
            st.markdown(f"**[{art['source']}] {art['title']}**")
            st.write(art['description'])
            st.markdown(f"[Baca Sumber Asli]({art['link']})")
            st.write("---")
    else:
        st.info("Sedang tidak ada artikel spesifik ekosistem EV dalam beberapa jam terakhir.")
else:
    st.error("Gagal mengambil data dari server berita global maupun lokal.")
