import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from collections import Counter
import re

st.set_page_config(page_title="Trending News Detector", layout="wide")

st.title("📊 Trending News Detector & Categorizer")
st.write("Aplikasi pelacak tren berita terkini menggunakan analisis teks sederhana.")

# 1. FUNGSI AMBIL DATA (Scraping via RSS Feed)
@st.cache_data(ttl=1800) # Simpan cache selama 30 menit agar web cepat
def fetch_news():
    url = "https://www.liputan6.com/feed/rss"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            articles = []
            for item in root.findall('.//item'):
                title = item.find('title').text if item.find('title') is not None else ""
                desc = item.find('description').text if item.find('description') is not None else ""
                link = item.find('link').text if item.find('link') is not None else ""
                articles.append({"title": title, "description": desc, "link": link})
            return articles
    except Exception as e:
        st.error(f"Gagal mengambil data: {e}")
    return []

# 2. FUNGSI ANALISIS TEKS (By Word & Category)
def analyze_trends(articles):
    all_words = []
    categorized_data = {"Politik/Hukum": 0, "Ekonomi/Bisnis": 0, "Teknologi": 0, "Hiburan/Gaya Hidup": 0, "Lainnya": 0}
    
    # Stopwords dasar Bahasa Indonesia untuk dibuang
    stopwords = {"dan", "yang", "di", "ke", "dari", "ini", "itu", "untuk", "dengan", "adalah", "dalam", "bisa", "pada", "juga", "sudah", "ada"}

    for art in articles:
        text = (art['title'] + " " + art['description']).lower()
        
        # Klasifikasi Kategori Sederhana (Rule-Based)
        if any(w in text for w in ["polisi", "kpk", "sidang", "hukum", "politik", "mencore", "pemilu", "dpr"]):
            categorized_data["Politik/Hukum"] += 1
        elif any(w in text for w in ["saham", "rupiah", "ekonomi", "bisnis", "harga", "pasar", "investasi", "inflasi"]):
            categorized_data["Ekonomi/Bisnis"] += 1
        elif any(w in text for w in ["ai", "gadget", "hp", "teknologi", "aplikasi", "internet", "game"]):
            categorized_data["Teknologi"] += 1
        elif any(w in text for w in ["artis", "film", "konser", "gaya hidup", "bintang", "fashion", "kuliner"]):
            categorized_data["Hiburan/Gaya Hidup"] += 1
        else:
            categorized_data["Lainnya"] += 1

        # Ekstraksi Kata
        words = re.findall(r'\b\w+\b', text)
        for word in words:
            if len(word) > 3 and word not in stopwords and not word.isdigit():
                all_words.append(word)
                
    return Counter(all_words).most_common(10), categorized_data

# --- RUN APLIKASI ---
data_berita = fetch_news()

if data_berita:
    top_words, categories = analyze_trends(data_berita)
    
    # Layout Kolom di Streamlit
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Top 10 Trending Words Hari Ini")
        df_words = pd.DataFrame(top_words, columns=['Kata', 'Frekuensi'])
        st.bar_chart(df_words.set_index('Kata'))
        st.dataframe(df_words, use_container_width=True)
        
    with col2:
        st.subheader("📁 Distribusi Kategori Berita")
        df_cat = pd.DataFrame(list(categories.items()), columns=['Kategori', 'Jumlah Berita'])
        st.bar_chart(df_cat.set_index('Kategori'), color="#FF4B4B")
        st.dataframe(df_cat, use_container_width=True)

    # Menampilkan Berita Asli
    st.write("---")
    st.subheader("📰 Feed Berita Terkini yang Dianalisis")
    for i, art in enumerate(data_berita[:5]): # Tampilkan 5 teratas
        st.markdown(f"**[{art['title']}]({art['link']})**")
        st.write(art['description'])
        st.write("---")
else:
    st.error("Gagal mengambil data berita atau feed sedang kosong.")

# Trik agar Vercel tidak eror membaca fungsi top-level
app = None


