import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from collections import Counter
import re

st.set_page_config(page_title="EV Trend & Issue Radar", layout="wide")

st.title("🔋 EV Market Trend & Critical Issue Radar")
st.write("Memantau tren pasar, penjualan, dan mendeteksi isu kritis (kebakaran/sparepart) pada seluruh merek EV di Indonesia.")

# --- 1. DAFTAR MEREK SUPER LENGKAP (INDONESIA) ---
car_brands = [
    "wuling", "byd", "hyundai", "ioniq", "kona", "chery", "omoda", "neta", 
    "aion", "gwm", "baic", "mg", "morris garages", "dfsk", "seres", "vinfast", 
    "kia", "ev6", "ev9", "tesla", "toyota", "bz4x", "binguo", "cloudev"
]
bike_brands = [
    "gesits", "alva", "polytron", "volta", "smoot", "selis", "rakata", "united", 
    "tangkas", "uwinfly", "yadea", "aima", "sunra", "davigo", "viar", "zongshen", "honda em1"
]
all_brands = car_brands + bike_brands

# --- 2. KATA KUNCI ISU KRITIS (KEBAKARAN & SPAREPART) ---
issue_keywords = [
    "terbakar", "kebakaran", "meledak", "api", "hangus", 
    "sparepart", "suku cadang", "komponen", "langka", "sulit", 
    "inden", "recall", "rusak", "keluhan", "bengkel", "baterai drop"
]

# --- 3. DATA PENJUALAN ---
def get_sales_data():
    data = {
        "Tahun": ["2022", "2023", "2024", "2025", "2026 (Est)"],
        "Mobil Listrik (Unit)": [10327, 17051, 38000, 75000, 110000],
        "Motor Listrik (Unit)": [15000, 47000, 115000, 280000, 450000]
    }
    return pd.DataFrame(data)

# Fungsi Terjemahan
def translate_to_id(text):
    if not text: return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=id&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return "".join([s[0] for s in res.json()[0] if s[0]])
    except: pass
    return text 

# FUNGSI AMBIL DATA BERITA
@st.cache_data(ttl=1800)
def fetch_global_local_news():
    sources = {
        "Antara Otomotif": "https://www.antaranews.com/rss/otomotif.xml",
        "Antara Tekno": "https://www.antaranews.com/rss/tekno.xml",
        "CNBC Industri": "https://www.cnbcindonesia.com/news/rss",
        "Xinhua China": "https://www.xinhuanet.com/english/rss/scitechrss.xml"
    }
    headers = {'User-Agent': 'Mozilla/5.0'}
    articles = []
    
    for name, url in sources.items():
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                for item in root.findall('.//item'):
                    t = item.find('title').text or ""
                    d = item.find('description').text or ""
                    l = item.find('link').text or ""
                    if "Xinhua" in name:
                        t = translate_to_id(t)
                        d = translate_to_id(d)
                    articles.append({"title": t, "description": d, "link": l, "source": name})
        except: continue
    return articles

# FUNGSI ANALISIS TEKS
def analyze_trends(articles):
    all_words = []
    critical_issues_found = []
    
    stopwords = {"dan", "yang", "di", "ke", "dari", "ini", "itu", "untuk", "dengan", "adalah", "dalam", "bisa", "pada", "juga", "sudah", "ada", "indonesia", "tahun", "menetapkan", "listrik"}

    for art in articles:
        text = (art['title'] + " " + art['description']).lower()
        
        # DETEKSI ISU KRITIS (Apakah ada kata merek DAN kata masalah/isu?)
        has_brand = any(b in text for b in all_brands)
        has_issue = any(i in text for i in issue_keywords)
        
        if has_brand and has_issue:
            critical_issues_found.append(art)

        # Hitung kata kunci
        words = re.findall(r'\b\w+\b', text)
        for w in words:
            if len(w) > 2 and w not in stopwords and not w.isdigit():
                if w == "mobil": w = "mobil listrik"
                elif w in ["motor", "motors"]: w = "motor listrik"
                elif w in ["baterai", "battery"]: w = "baterai"
                
                valid = ["mobil listrik", "motor listrik", "ev", "lfp", "lithium", "sparepart", "terbakar"] + all_brands
                if any(k in w for k in valid) or w == "baterai":
                    all_words.append(w)
                
    return Counter(all_words).most_common(12), critical_issues_found

# --- RUN APLIKASI ---
# 1. Grafik Penjualan
st.subheader("📈 Tren Penjualan EV (Gaikindo & AISI)")
st.line_chart(get_sales_data().set_index("Tahun"), use_container_width=True)

st.write("---")
data_berita = fetch_global_local_news()

if data_berita:
    top_words, critical_issues = analyze_trends(data_berita)
    
    # 2. RADAR ISU KRITIS (Tampil paling atas jika ada masalah!)
    if critical_issues:
        st.error(f"🚨 **PERINGATAN: Ditemukan {len(critical_issues)} berita mengenai Isu Kritis (Kebakaran / Kelangkaan Sparepart) pada EV!**")
        with st.expander("Buka Detail Isu Kritis", expanded=True):
            for art in critical_issues[:5]:
                st.markdown(f"**[{art['source']}] {art['title']}**")
                st.write(art['description'])
                st.markdown(f"[Baca Selengkapnya]({art['link']})")
                st.write("---")
    else:
        st.success("✅ Terpantau Aman: Tidak ada laporan terbaru mengenai kebakaran EV atau krisis sparepart dari media saat ini.")

    # 3. Dasbor Tren Umum
    st.subheader("🔥 Top 12 Merek & Kata Kunci Terhangat")
    if top_words:
        df_words = pd.DataFrame(top_words, columns=['Kata Kunci', 'Frekuensi'])
        st.bar_chart(df_words.set_index('Kata Kunci'))
    
    st.write("---")
    st.subheader("📰 Feed Berita Ekosistem EV Terkini")
    ev_articles = [a for a in data_berita if any(w in (a['title'] + a['description']).lower() for w in ["listrik", "baterai", "ev", "sparepart"] + all_brands)]
    
    if ev_articles:
        for art in ev_articles[:10]: 
            st.markdown(f"**[{art['source']}] {art['title']}**")
            st.markdown(f"[Link Sumber]({art['link']})")
            st.write("---")
else:
    st.error("Gagal mengambil data dari server berita.")
