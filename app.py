import streamlit as st
import random
import time
import os
import urllib.parse

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Edebiyat Ligi",
    page_icon="📱",
    layout="centered"
)

# ==========================================
# 👇 GOOGLE FORM LİNKİNİ BURAYA YAPIŞTIR 👇
# ==========================================
GOOGLE_FORM_LINKI = "https://docs.google.com/forms/d/e/1FAIpQLSd6x_NxAj58m8-5HAKpm6R6pmTvJ64zD-TETIPxF-wul5Muwg/viewform?usp=header"
# ==========================================

# --- CUMHURİYET VERİTABANI ---
@st.cache_data
def get_cumhuriyet_db():
    return {
        "Ömer Seyfettin": {"Hikaye": ["Kaşağı", "Ant", "Falaka", "Pembe İncili Kaftan", "Bomba", "Yüksek Ökçeler", "Gizli Mabed"], "Roman": ["Efruz Bey"]},
        "Ziya Gökalp": {"Şiir": ["Kızıl Elma", "Altın Işık", "Yeni Hayat"], "Fikir": ["Türkçülüğün Esasları"]},
        "Yakup Kadri Karaosmanoğlu": {"Roman": ["Yaban", "Kiralık Konak", "Sodom ve Gomore", "Nur Baba", "Ankara", "Panorama"], "Anı": ["Zoraki Diplomat"]},
        "Halide Edip Adıvar": {"Roman": ["Sinekli Bakkal", "Ateşten Gömlek", "Vurun Kahpeye", "Handan", "Tatarcık"]},
        "Reşat Nuri Güntekin": {"Roman": ["Çalıkuşu", "Yaprak Dökümü", "Yeşil Gece", "Acımak", "Miskinler Tekkesi"]},
        "Peyami Safa": {"Roman": ["Dokuzuncu Hariciye Koğuşu", "Fatih-Harbiye", "Yalnızız", "Matmazel Noraliya'nın Koltuğu"]},
        "Tarık Buğra": {"Roman": ["Küçük Ağa", "Osmancık", "İbişin Rüyası", "Firavun İmanı"]},
        "Sait Faik Abasıyanık": {"Hikaye": ["Semaver", "Sarnıç", "Lüzumsuz Adam", "Son Kuşlar", "Alemdağ'da Var Bir Yılan"]},
        "Sabahattin Ali": {"Roman": ["Kürk Mantolu Madonna", "Kuyucaklı Yusuf", "İçimizdeki Şeytan"], "Hikaye": ["Değirmen", "Kağnı"]},
        "Ahmet Hamdi Tanpınar": {"Roman": ["Huzur", "Saatleri Ayarlama Enstitüsü", "Sahnenin Dışındakiler"], "Deneme": ["Beş Şehir"]},
        "Necip Fazıl Kısakürek": {"Şiir": ["Çile", "Kaldırımlar", "Örümcek Ağı"], "Tiyatro": ["Bir Adam Yaratmak", "Reis Bey"]},
        "Nazım Hikmet": {"Şiir": ["Memleketimden İnsan Manzaraları", "Kuvayi Milliye Destanı", "Simavne Kadısı Oğlu Bedreddin"]},
        "Yaşar Kemal": {"Roman": ["İnce Memed", "Yer Demir Gök Bakır", "Ağrı Dağı Efsanesi", "Yılanı Öldürseler"]},
        "Orhan Pamuk": {"Roman": ["Kara Kitap", "Benim Adım Kırmızı", "Masumiyet Müzesi", "Cevdet Bey ve Oğulları"]},
        "Oğuz Atay": {"Roman": ["Tutunamayanlar", "Tehlikeli Oyunlar", "Bir Bilim Adamının Romanı"]},
        "Attila İlhan": {"Şiir": ["Ben Sana Mecburum", "Sisler Bulvarı", "Duvar"], "Roman": ["Kurtlar Sofrası"]},
        "Cemal Süreya": {"Şiir": ["Üvercinka", "Sevda Sözleri", "Göçebe"]},
        "Adalet Ağaoğlu": {"Roman": ["Ölmeye Yatmak", "Bir Düğün Gecesi", "Fikrimin İnce Gülü"]},
        "Orhan Kemal": {"Roman": ["Bereketli Topraklar Üzerinde", "Murtaza", "Eskici ve Oğulları", "Hanımın Çiftliği"]}
    }

# --- DİVAN VERİTABANI ---
@st.cache_data
def get_divan_db():
    return {
        "Fuzuli": {"Mesnevi": ["Leyla ile Mecnun", "Bengü Bade", "Sohbetü'l Esmar"], "Nesir/Mektup": ["Şikayetname", "Hadikatü's Süeda", "Rind ü Zahid"]},
        "Baki": {"Şiir": ["Kanuni Mersiyesi"], "Nesir": ["Fezail-i Mekke"]},
        "Nefi": {"Hiciv (Eleştiri)": ["Siham-ı Kaza"], "Mesnevi": ["Tuhfetü’l-Uşşak"]},
        "Nabi": {"Mesnevi (Öğüt)": ["Hayriye", "Hayrabad", "Surname"], "Gezi": ["Tuhfetü'l Haremeyn"]},
        "Şeyh Galip": {"Mesnevi": ["Hüsnü Aşk"]},
        "Şeyhi": {"Fabl/Hiciv": ["Harname"], "Mesnevi": ["Hüsrev ü Şirin"]},
        "Katip Çelebi": {"Bibliyografya": ["Keşfü'z Zunun"], "Coğrafya": ["Cihannüma"], "Deneme": ["Mizanü'l Hak"]},
        "Evliya Çelebi": {"Gezi": ["Seyahatname"]},
        "Ali Şir Nevai": {"Sözlük": ["Muhakemetü'l Lügateyn"], "Tezkire": ["Mecalisü'n Nefais"], "Mesnevi": ["Lisanü't Tayr"]},
        "Sinan Paşa": {"Süslü Nesir": ["Tazarruname", "Maarifname"]},
        "Mercimek Ahmet": {"Sade Nesir": ["Kabusname"]},
        "Gülşehri": {"Mesnevi": ["Mantıku't Tayr", "Felekname"]},
        "Aşık Paşa": {"Mesnevi": ["Garibname"]},
        "Süleyman Çelebi": {"Mesnevi": ["Vesiletü'n Necat (Mevlid)"]},
        "Ahmedi": {"Mesnevi": ["İskendername", "Cemşid ü Hurşid"]},
        "Hoca Dehhani": {"Destan": ["Selçuklu Şehnamesi"]},
        "Sehi Bey": {"Tezkire": ["Heşt Behişt"]},
        "Babürşah": {"Anı": ["Babürname"]},
        "Seydi Ali Reis": {"Gezi/Anı": ["Mir'atü'l Memalik"]},
        "Yirmisekiz Çelebi Mehmet": {"Sefaretname": ["Paris Sefaretnamesi"]},
        "Kaygusuz Abdal": {"Tasavvufi Nesir": ["Budalaname", "Muglataname", "Vücudname"]},
        "Eşrefoğlu Rumi": {"Tasavvuf": ["Müzekkin Nüfus"]},
        "Taşlıcalı Yahya": {"Mesnevi": ["Şah ü Geda", "Yusuf ü Züleyha"]},
        "Zati": {"Mesnevi": ["Şem ü Pervane"]},
        "Nergisi": {"Nesir": ["Nergisi Hamsesi"]},
        "Veysi": {"Nesir": ["Habname"]},
        "Keçecizade İzzet Molla": {"Mesnevi": ["Mihnet Keşan"]},
        "Enderunlu Fazıl": {"Mesnevi": ["Zenanname", "Hubanname"]},
        "Sünbülzade Vehbi": {"Sözlük/Mesnevi": ["Lütfiyye", "Tuhfe-i Vehbi"]}
    }

# --- MOBİL UYUMLU TASARIM (CSS) ---
oyun_deseni = "https://www.transparenttextures.com/patterns/cubes.png"

st.markdown(f"""
    <style>
    /* ARKA PLAN */
    .stApp {{
        background: linear-gradient(135deg, #ff9ff3, #ff6b6b, #51cf66);
        background-image: linear-gradient(135deg, rgba(255,159,243,0.8), rgba(255,107,107,0.8), rgba(81,207,102,0.8)), url("{oyun_deseni}");
        background-blend-mode: overlay;
        background-attachment: fixed;
        background-size: cover;
    }}
    
    html, body, p, div, label, h1, h2, h3, h6 {{
        color: #000000 !important;
        font-family: 'Segoe UI', sans-serif;
    }}
    
    /* Yan Menü */
    [data-testid="stSidebar"] {{
        background-color: #2d3436 !important;
        border-right: 4px solid #00cec9;
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    /* --- MOBİL OPTİMİZASYON KODLARI (RESPONSIVE) --- */
    @media (max-width: 768px) {{
        /* Başlıkları küçült */
        .creator-name {{ font-size: 16px !important; padding: 10px !important; letter-spacing: 1px !important; }}
        h1 {{ font-size: 24px !important; padding: 10px !important; }}
        
        /* Menü kartlarını sıkıştır */
        .menu-card {{ padding: 20px !important; }}
        .menu-title {{ font-size: 22px !important; }}
        
        /* Soru kartını ekrana yay */
        .question-card {{ padding: 15px !important; margin-bottom: 15px !important; }}
        .question-text {{ font-size: 24px !important; }}
        
        /* Şıkların yazı boyutunu ayarla */
        .stRadio label p {{ font-size: 16px !important; }}
        
        /* Logo ve başlığı ortala */
        [data-testid="stColumn"] {{ text-align: center !important; }}
        [data-testid="stImage"] {{ margin: 0 auto !important; }}
    }}

    /* Ana Menü Kartları */
    .menu-card {{
        background-color: rgba(255, 255, 255, 0.95);
        padding: 40px;
        border-radius: 25px;
        text-align: center;
        border: 4px solid #2d3436;
        cursor: pointer;
        transition: all 0.2s;
        margin-bottom: 20px;
        box-shadow: 0 8px 0px #d63031;
    }}
    .menu-card:hover {{
        transform: translateY(-5px);
        background-color: #ffffff;
    }}
    .menu-title {{
        font-size: 30px;
        font-weight: 900;
        color: #d63031;
        text-transform: uppercase;
    }}
    
    /* Butonlar */
    .stButton button {{
        background-color: #d63031 !important;
        color: white !important;
        border-radius: 15px !important;
        font-weight: 900 !important;
        border: 3px solid #000 !important;
        box-shadow: 0 5px 0 #000 !important;
        font-size: 18px !important;
        width: 100%; /* Mobilde tam genişlik */
    }}
    .stButton button:active {{
        box-shadow: 0 0 0 #000 !important;
        transform: translateY(5px);
    }}

    /* Özel Kaydet Butonu */
    .kaydet-btn {{
        display: block;
        background-color: #00b894;
        color: white;
        padding: 15px;
        text-align: center;
        border-radius: 15px;
        text-decoration: none;
        font-weight: 900;
        font-size: 20px;
        border: 3px solid #006266;
        box-shadow: 0 5px 0 #006266;
        margin-top: 20px;
    }}
    
    /* Soru Kartı */
    .question-card {{
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 25px;
        border: 4px solid #2d3436;
        box-shadow: 0 8px 0px #2d3436;
        text-align: center;
        margin-bottom: 25px;
    }}

    /* Şıkların Kutusu */
    .stRadio {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 15px;
        border-radius: 20px;
        border: 3px solid #2d3436;
    }}

    /* İsim Tabelası */
    .creator-name {{
        background-color: #2d3436;
        color: #00cec9 !important;
        text-align: center;
        padding: 15px;
        font-weight: 900;
        font-size: 22px;
        border-radius: 15px;
        letter-spacing: 3px;
        margin-bottom: 25px;
        border: 3px solid #fff;
        box-shadow: 0 8px 0px rgba(0,0,0,0.4);
        text-transform: uppercase;
    }}
    
    /* Mobil Skor Paneli */
    .mobile-score {{
        background-color: rgba(255,255,255,0.9);
        padding: 10px;
        border-radius: 15px;
        border: 3px solid #2d3436;
        text-align: center;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-around;
        font-weight: bold;
        font-size: 18px;
    }}
    
    h1 {{
        background-color: rgba(255,255,255,0.8);
        padding: 10px 20px;
        border-radius: 20px;
        display: inline-block;
        border: 4px solid #2d3436;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'kategori' not in st.session_state:
    st.session_state.kategori = None 
if 'xp' not in st.session_state:
    st.session_state.xp = 0
if 'soru_sayisi' not in st.session_state:
    st.session_state.soru_sayisi = 0
if 'mevcut_soru' not in st.session_state:
    st.session_state.mevcut_soru = None
if 'cevap_verildi' not in st.session_state:
    st.session_state.cevap_verildi = False

# --- SORU ÜRETME ---
def yeni_soru_uret():
    if st.session_state.kategori == "CUMHURİYET":
        db = get_cumhuriyet_db()
    else:
        db = get_divan_db()

    yazarlar = list(db.keys())
    secilen_yazar = random.choice(yazarlar)
    turlar = list(db[secilen_yazar].keys())
    secilen_tur = random.choice(turlar)
    eserler = db[secilen_yazar][secilen_tur]
    secilen_eser = random.choice(eserler)
    
    yanlis_yazarlar = random.sample([y for y in yazarlar if y != secilen_yazar], 3)
    siklar = yanlis_yazarlar + [secilen_yazar]
    random.shuffle(siklar)
    
    st.session_state.cevap_verildi = False
    
    return {
        "eser": secilen_eser,
        "tur": secilen_tur,
        "dogru_cevap": secilen_yazar,
        "siklar": siklar
    }

# --- ANA UYGULAMA AKIŞI ---

# 1. LOGO VE İSİM
st.markdown('<div class="creator-name">👑 ALPEREN SÜNGÜ 👑</div>', unsafe_allow_html=True)

col_logo, col_title = st.columns([1, 2])
with col_logo:
    resim_adi = "background.jpg" 
    if os.path.exists(resim_adi):
        st.image(resim_adi, width=130) # Mobilde çok yer kaplamasın diye küçülttük
    else:
        st.info("Logo")

with col_title:
    st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
    if st.session_state.kategori:
        baslik = f"{st.session_state.kategori}<br>EDEBİYATI"
    else:
        baslik = "EDEBİYAT<br>LİGİ"
    st.markdown(f'<h1 style="color:#2d3436 !important; font-weight:900; text-align:center;">{baslik}</h1>', unsafe_allow_html=True)

# 2. MOBİL SKOR TABLOSU (Sayfanın en tepesinde görünsün)
level = (st.session_state.soru_sayisi // 5) + 1
if st.session_state.kategori:
    st.markdown(f"""
    <div class="mobile-score">
        <span style="color:#d63031;">⭐ Level {level}</span>
        <span style="color:#00cec9;">💎 {st.session_state.xp} XP</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 3. MENÜ EKRANI
if st.session_state.kategori is None:
    st.markdown("<div style='background-color:rgba(255,255,255,0.9); padding:15px; border-radius:20px; border:3px solid #2d3436; box-shadow: 5px 5px 0 rgba(0,0,0,0.1);'><h3 style='text-align:center; margin:0; font-weight:bold;'>🎮 Lütfen Yarışmak İstediğin Alanı Seç:</h3></div>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="menu-card">
            <div style="font-size:50px;">🇹🇷</div>
            <div class="menu-title">CUMHURİYET</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("SEÇ: CUMHURİYET", use_container_width=True):
            st.session_state.kategori = "CUMHURİYET"
            st.session_state.xp = 0
            st.session_state.soru_sayisi = 0
            st.session_state.mevcut_soru = yeni_soru_uret()
            st.rerun()

    with col2:
        st.markdown("""
        <div class="menu-card">
            <div style="font-size:50px;">📜</div>
            <div class="menu-title">DİVAN</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("SEÇ: DİVAN", use_container_width=True):
            st.session_state.kategori = "DİVAN"
            st.session_state.xp = 0
            st.session_state.soru_sayisi = 0
            st.session_state.mevcut_soru = yeni_soru_uret()
            st.rerun()

# 4. OYUN EKRANI
else:
    soru = st.session_state.mevcut_soru
    
    # YAN MENÜ (Masaüstü için detaylı, mobilde gizli kalabilir çünkü yukarıya skor koyduk)
    with st.sidebar:
        st.header("🏆 OYUN DURUMU")
        st.metric("⭐ Level", f"{level}")
        st.metric("💎 Puan (XP)", f"{st.session_state.xp}")
        
        st.markdown("---")
        
        # Google Form Butonu
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:10px; font-weight:bold; color:white;">
            SKORUNU LİSTEYE EKLE:
        </div>
        <a href="{GOOGLE_FORM_LINKI}" target="_blank" class="kaydet-btn">
           📝 SKORU KAYDET
        </a>
        <div style="font-size:12px; margin-top:5px; color:#bdc3c7; text-align:center;">
            (Mod: {st.session_state.kategori} | Puan: {st.session_state.xp})
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("⬅️ MENÜYE DÖN"):
            st.session_state.kategori = None 
            st.session_state.xp = 0
            st.rerun()

    # SORU ALANI
    st.progress((st.session_state.soru_sayisi % 5) * 20)

    st.markdown(f"""
    <div class="question-card">
        <div style="color:#636e72; font-weight:bold; font-size:16px;">GÖREV: {soru['tur']}</div>
        <div style="font-size:26px; font-weight:900; color:#d63031; margin: 15px 0; text-transform:uppercase; text-shadow: 2px 2px 0px rgba(0,0,0,0.1);">✨ {soru['eser']} ✨</div>
        <div style="font-size:18px; font-weight:bold;">Bu eser kime aittir?</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        cevap = st.radio("Seçim:", soru['siklar'], label_visibility="collapsed")
    with col2:
        st.write("") 
        st.write("")
        kontrol_buton = st.button("YANITLA 🚀", type="primary", use_container_width=True)

    if kontrol_buton:
        if not st.session_state.cevap_verildi:
            if cevap == soru['dogru_cevap']:
                st.session_state.xp += 100
                st.success("MÜKEMMEL! +100 XP 🎯")
                st.balloons()
            else:
                st.error(f"YANLIŞ! Doğru: {soru['dogru_cevap']} 💔")
                st.session_state.xp = max(0, st.session_state.xp - 20)
            
            st.session_state.soru_sayisi += 1
            st.session_state.cevap_verildi = True
            time.sleep(1)
            st.session_state.mevcut_soru = yeni_soru_uret()
            st.rerun()