import streamlit as st
import random
import time
import os
import base64
import json
from datetime import datetime
from collections import Counter

# --- 1. SAYFA AYARLARI ---
st.set_page_config(
    page_title="Edebiyat Ligi",
    page_icon="📚",
    layout="centered"
)

# --- URL (BENİ HATIRLA) SİSTEMİ ---
try:
    query_params = st.query_params
    url_user = query_params.get("oyuncu", None)
except:
    url_user = None

# DOSYA TANIMLARI
SKOR_DOSYASI = "skorlar.json"
ADMIN_DUYURU_DOSYASI = "admin_duyuru.json"
GELEN_KUTUSU_DOSYASI = "gelen_mesajlar.json"
OZEL_MESAJ_DOSYASI = "ozel_mesajlar.json"
RAPOR_DOSYASI = "oyuncu_raporlari.json"

# --- 2. GÜVENLİ BAŞLANGIÇ ---
defaults = {
    'page': "MENU",
    'kategori': None,
    'xp': 0,
    'soru_sayisi': 0,
    'mevcut_soru': None,
    'cevap_verildi': False,
    'sema_hoca_kizdi': False,
    'sanat_aciklama': "",
    'calisma_yazar': None,
    'soru_bitti': False,
    'kullanici_adi': url_user if url_user else "",
    'rastgele_bilgi': None,
    'son_duyuru_zamani': 0.0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

if url_user and not st.session_state.kullanici_adi:
    st.session_state.kullanici_adi = url_user

# --- 3. VERİ YÖNETİM SİSTEMLERİ ---

# A) SKOR SİSTEMİ
def skorlari_yukle():
    if not os.path.exists(SKOR_DOSYASI): return {}
    try:
        with open(SKOR_DOSYASI, "r", encoding="utf-8") as f:
            data = json.load(f)
            new_data = {}
            for k, v in data.items():
                if isinstance(v, int): new_data[k] = {"puan": v, "zaman": 0}
                else: new_data[k] = v
            return new_data
    except: return {}

def skoru_guncelle_ve_kaydet(kullanici, puan_degisimi):
    if not kullanici or kullanici == "Misafir": return 0
    try:
        veriler = skorlari_yukle()
        mevcut_veri = veriler.get(kullanici, {"puan": 0, "zaman": 0})
        yeni_puan = max(0, mevcut_veri["puan"] + puan_degisimi)
        veriler[kullanici] = {"puan": yeni_puan, "zaman": time.time()}
        with open(SKOR_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(veriler, f, ensure_ascii=False, indent=4)
        return yeni_puan
    except: return 0

def admin_puan_degistir(kullanici, yeni_puan):
    try:
        veriler = skorlari_yukle()
        if kullanici in veriler:
            eski_zaman = veriler[kullanici].get("zaman", 0)
            veriler[kullanici] = {"puan": int(yeni_puan), "zaman": eski_zaman}
            with open(SKOR_DOSYASI, "w", encoding="utf-8") as f:
                json.dump(veriler, f, ensure_ascii=False, indent=4)
            return True
    except: return False

# B) RAPORLAMA SİSTEMİ
def raporlari_yukle():
    if not os.path.exists(RAPOR_DOSYASI): return {}
    try:
        with open(RAPOR_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def rapor_kaydet(kullanici, soru_metni, verilen_cevap, dogru_mu, dogru_cevap, kategori, konu_basligi):
    if not kullanici or kullanici == "Misafir": return
    try:
        raporlar = raporlari_yukle()
        if kullanici not in raporlar:
            raporlar[kullanici] = {
                "toplam_cozulen": 0, "dogru_sayisi": 0, "yanlis_sayisi": 0, 
                "son_gorulme": "", "hatalar": [], 
                "yanlis_analiz_kategori": {}, "yanlis_analiz_konu": {}
            }
        
        user_data = raporlar[kullanici]
        user_data["toplam_cozulen"] += 1
        user_data["son_gorulme"] = datetime.now().strftime("%d-%m %H:%M:%S")
        
        if dogru_mu:
            user_data["dogru_sayisi"] += 1
        else:
            user_data["yanlis_sayisi"] += 1
            if kategori in user_data.get("yanlis_analiz_kategori", {}): user_data["yanlis_analiz_kategori"][kategori] += 1
            else: 
                if "yanlis_analiz_kategori" not in user_data: user_data["yanlis_analiz_kategori"] = {}
                user_data["yanlis_analiz_kategori"][kategori] = 1
            
            if konu_basligi:
                if konu_basligi in user_data.get("yanlis_analiz_konu", {}): user_data["yanlis_analiz_konu"][konu_basligi] += 1
                else: 
                    if "yanlis_analiz_konu" not in user_data: user_data["yanlis_analiz_konu"] = {}
                    user_data["yanlis_analiz_konu"][konu_basligi] = 1

            hata_kaydi = {"kategori": kategori, "konu": konu_basligi, "soru": soru_metni, "yanlis_cevap": verilen_cevap, "dogru_cevap": dogru_cevap, "zaman": datetime.now().strftime("%H:%M")}
            user_data["hatalar"].append(hata_kaydi)
            if len(user_data["hatalar"]) > 30: user_data["hatalar"] = user_data["hatalar"][-30:]
        
        with open(RAPOR_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(raporlar, f, ensure_ascii=False, indent=4)
    except: pass

# C) DİĞER DOSYA İŞLEMLERİ
def admin_duyuru_oku():
    if not os.path.exists(ADMIN_DUYURU_DOSYASI): return None
    try:
        with open(ADMIN_DUYURU_DOSYASI, "r", encoding="utf-8") as f: return json.load(f)
    except: return None
def admin_duyuru_yaz(mesaj):
    with open(ADMIN_DUYURU_DOSYASI, "w", encoding="utf-8") as f:
        json.dump({"mesaj": mesaj, "zaman": time.time()}, f, ensure_ascii=False)
def mesajlari_yukle():
    if not os.path.exists(GELEN_KUTUSU_DOSYASI): return []
    try:
        with open(GELEN_KUTUSU_DOSYASI, "r", encoding="utf-8") as f: return json.load(f)
    except: return []
def mesaj_gonder(gonderen, mesaj):
    mevcut = mesajlari_yukle()
    mevcut.append({"gonderen": gonderen, "mesaj": mesaj, "tarih": datetime.now().strftime("%d-%m %H:%M")})
    with open(GELEN_KUTUSU_DOSYASI, "w", encoding="utf-8") as f: json.dump(mevcut, f, ensure_ascii=False, indent=4)
def mesajlari_temizle():
    with open(GELEN_KUTUSU_DOSYASI, "w", encoding="utf-8") as f: json.dump([], f)
def kisiye_ozel_mesaj_gonder(alici, mesaj):
    if not os.path.exists(OZEL_MESAJ_DOSYASI): veriler = {}
    else:
        try:
            with open(OZEL_MESAJ_DOSYASI, "r", encoding="utf-8") as f: veriler = json.load(f)
        except: veriler = {}
    veriler[alici] = mesaj
    with open(OZEL_MESAJ_DOSYASI, "w", encoding="utf-8") as f: json.dump(veriler, f, ensure_ascii=False)
def kisiye_ozel_mesaj_kontrol(kullanici):
    if not kullanici or not os.path.exists(OZEL_MESAJ_DOSYASI): return
    try:
        with open(OZEL_MESAJ_DOSYASI, "r", encoding="utf-8") as f: veriler = json.load(f)
        if kullanici in veriler:
            mesaj = veriler[kullanici]
            st.markdown(f"""<div style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:999990;display:flex;justify-content:center;align-items:center;"><div style="background:#c62828;color:white;padding:40px;border-radius:20px;border:6px solid #ffeb3b;text-align:center;width:400px;box-shadow:0 0 50px rgba(255,235,59,0.5);"><div style="font-size:60px;">💌</div><h2 style="color:white;margin:10px 0;">SANA MESAJ VAR!</h2><hr style="border-color:#ffeb3b;"><p style="font-size:22px;font-weight:bold;color:#ffeb3b;">{mesaj}</p></div></div>""", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("""<style>div[data-testid="stButton"] > button {position:relative; z-index:999999; border:3px solid white !important; background-color:#ffeb3b !important; color:#c62828 !important;}</style>""", unsafe_allow_html=True)
                if st.button("MESAJI OKUDUM VE KAPAT ❎", key="popup_kapat"):
                    del veriler[kullanici]
                    with open(OZEL_MESAJ_DOSYASI, "w", encoding="utf-8") as f: json.dump(veriler, f, ensure_ascii=False)
                    st.rerun()
            st.stop()
    except: pass

# --- 4. CSS STİLLERİ ---
sidebar_color = "#1b3a1a"
card_bg_color = "#2e5a27"
text_color_cream = "#fffbe6"
red_warning_color = "#c62828"
input_bg_color = "#3e7a39"
bg_image_url = "https://e0.pxfuel.com/wallpapers/985/844/desktop-wallpaper-booknerd-book-and-background-literature.jpg"

st.markdown(f"""
    <style>
    .stApp {{ background-image: url("{bg_image_url}"); background-size: cover; background-attachment: fixed; }}
    html, body, p, div, label, h1, h2, h3, h4, h6, span {{ font-family: 'Segoe UI', sans-serif; color: {text_color_cream} !important; }}
    .stTextInput input {{ background-color: {input_bg_color} !important; color: white !important; border: 2px solid white !important; text-align: center; font-weight: bold; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_color} !important; border-right: 4px solid #3e7a39; }}
    .question-card, .stRadio, .menu-card, .bio-box, .duyuru-wrapper {{ background-color: {card_bg_color} !important; border: 3px solid #3e7a39; border-radius: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.5); padding: 20px; margin-bottom: 15px; text-align: center; }}
    .eser-icerik-kutusu, .kavram-box {{ background-color: #1b5e20 !important; color: white !important; padding: 15px; border-radius: 10px; border: 2px solid #ffeb3b !important; margin-top: 5px; opacity: 1 !important; text-align: left; }}
    .menu-card:hover {{ transform: scale(1.05); transition: 0.2s; }}
    .duyuru-wrapper {{ border: 2px solid #ffeb3b; padding: 10px 15px; margin-bottom: 15px; display: flex; align-items: center; justify-content: center; gap: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.4); flex-wrap: wrap; }}
    .mini-leaderboard {{ background-color: rgba(27, 94, 32, 0.95); border-radius: 10px; padding: 10px; margin-bottom: 20px; border: 1px solid #aed581; text-align: center; display: flex; justify-content: space-around; align-items: center; font-size: 14px; flex-wrap: wrap; }}
    .leader-item {{ margin: 5px; font-weight: bold; color: #fffbe6; }}
    div[data-testid="stToast"] {{ background-color: #1b5e20 !important; color: white !important; border: 2px solid #ffeb3b !important; font-weight: bold !important; font-size: 16px !important; }}
    .stButton button {{ background-color: #d84315 !important; color: white !important; border-radius: 15px !important; font-weight: 900 !important; border: 2px solid #fff !important; width: 100%; }}
    .creator-name {{ background-color: {card_bg_color}; color: #ffeb3b !important; text-align: center; padding: 10px; font-weight: 900; font-size: 20px; border-radius: 15px; margin-bottom: 20px; border: 3px solid #3e7a39; box-shadow: 0 8px 0px rgba(0,0,0,0.4); text-transform: uppercase; }}
    .mobile-score {{ background-color: {card_bg_color}; padding: 10px; border-radius: 15px; border: 3px solid #3e7a39; text-align: center; margin-bottom: 15px; display: flex; justify-content: space-around; font-weight: bold; font-size: 18px; color: {text_color_cream} !important; }}
    .sanat-aciklama {{ background-color: {card_bg_color}; color: {text_color_cream} !important; border-left: 6px solid #ffeb3b; padding: 20px; margin-top: 20px; font-size: 18px; border-radius: 10px; }}
    .sema-hoca-fixed-wrapper {{ position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 99999; animation: shake 0.5s; box-shadow: 0 0 100px rgba(0,0,0,0.9); border-radius: 20px; overflow: hidden; border: 6px solid white; }}
    .sema-hoca-alert-box-body {{ background-color: {red_warning_color}; color: white; text-align: center; padding: 30px; padding-bottom: 40px; }}
    .sema-hoca-alert-box-body button {{ background-color: white !important; color: {red_warning_color} !important; border: 2px solid {red_warning_color} !important; font-weight: bold !important; margin-top: 20px; position: relative !important; z-index: 100000; }}
    .random-info-box {{ background-color: #1a237e !important; border: 4px solid #ffeb3b; color: white !important; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; animation: fadeIn 0.5s; box-shadow: 0 0 20px rgba(255, 235, 59, 0.5); }}
    .streamlit-expanderHeader {{ color: #ffeb3b !important; font-weight: bold; }}
    @keyframes shake {{ 0% {{ transform: translate(-50%, -50%) rotate(0deg); }} 25% {{ transform: translate(-50%, -50%) rotate(5deg); }} 50% {{ transform: translate(-50%, -50%) rotate(0eg); }} 75% {{ transform: translate(-50%, -50%) rotate(-5deg); }} 100% {{ transform: translate(-50%, -50%) rotate(0deg); }} }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
    """, unsafe_allow_html=True)

# --- SCRIPT BAŞI KONTROLLER ---
duyuru = admin_duyuru_oku()
if duyuru and duyuru["zaman"] > st.session_state.son_duyuru_zamani:
    st.toast(duyuru["mesaj"], icon="📢")
    st.session_state.son_duyuru_zamani = duyuru["zaman"]

if st.session_state.kullanici_adi:
    kisiye_ozel_mesaj_kontrol(st.session_state.kullanici_adi)

# --- SES ---
def get_audio_html(sound_type):
    if sound_type == "dogru":
        audio_url = "https://cdn.pixabay.com/audio/2021/08/04/audio_bb630cc098.mp3"
    else:
        audio_url = "https://cdn.pixabay.com/audio/2021/08/04/audio_88447e769f.mp3"
    return f"""<audio autoplay="true" style="display:none;"><source src="{audio_url}" type="audio/mp3"></audio>"""

# ======================================================
# 5. EKSİKSİZ VERİTABANLARI
# ======================================================
@st.cache_data
def get_game_db(kategori):
    if kategori == "CUMHURİYET":
        return {
            "Ömer Seyfettin": {"Hikaye": ["Kaşağı", "Ant", "Falaka", "Pembe İncili Kaftan", "Bomba", "Yüksek Ökçeler", "Gizli Mabed", "Başını Vermeyen Şehit", "Perili Köşk", "Bahar ve Kelebekler", "Harem", "Yalnız Efe", "Ferman", "Diyet", "Topuz", "Kurumuş Ağaçlar"], "Roman": ["Efruz Bey"]},
            "Ziya Gökalp": {"Şiir": ["Kızıl Elma", "Altın Işık", "Yeni Hayat"], "Fikir": ["Türkçülüğün Esasları", "Türkleşmek İslamlaşmak Muasırlaşmak", "Türk Medeniyeti Tarihi"]},
            "Yakup Kadri Karaosmanoğlu": {"Roman": ["Yaban", "Kiralık Konak", "Sodom ve Gomore", "Nur Baba", "Ankara", "Panorama", "Bir Sürgün", "Hep O Şarkı", "Hüküm Gecesi"], "Anı": ["Zoraki Diplomat", "Anamın Kitabı", "Gençlik ve Edebiyat Hatıraları", "Politikada 45 Yıl", "Vatan Yolunda"]},
            "Halide Edip Adıvar": {"Roman": ["Sinekli Bakkal", "Ateşten Gömlek", "Vurun Kahpeye", "Handan", "Tatarcık", "Yolpalas Cinayeti", "Kalp Ağrısı", "Zeyno'nun Oğlu", "Yeni Turan", "Sonsuz Panayır", "Döner Ayna"], "Anı": ["Mor Salkımlı Ev", "Türk'ün Ateşle İmtihanı"]},
            "Reşat Nuri Güntekin": {"Roman": ["Çalıkuşu", "Yaprak Dökümü", "Yeşil Gece", "Acımak", "Miskinler Tekkesi", "Dudaktan Kalbe", "Akşam Güneşi", "Kavak Yelleri", "Damga", "Bir Kadın Düşmanı", "Değirmen", "Gizli El", "Eski Hastalık", "Kan Davası"]},
            "Peyami Safa": {"Roman": ["Dokuzuncu Hariciye Koğuşu", "Fatih-Harbiye", "Yalnızız", "Matmazel Noraliya'nın Koltuğu", "Bir Tereddüdün Romanı", "Sözde Kızlar", "Mahşer", "Canan", "Biz İnsanlar", "Şimşek"]},
            "Tarık Buğra": {"Roman": ["Küçük Ağa", "Osmancık", "İbişin Rüyası", "Firavun İmanı", "Yağmur Beklerken", "Dönemeçte", "Gençliğim Eyvah", "Yalnızlar", "Siyah Kehribar"]},
            "Sait Faik Abasıyanık": {"Hikaye": ["Semaver", "Sarnıç", "Lüzumsuz Adam", "Son Kuşlar", "Alemdağ'da Var Bir Yılan", "Şahmerdan", "Mahalle Kahvesi", "Havada Bulut", "Kumpanya", "Az Şekerli", "Tüneldeki Çocuk"]},
            "Sabahattin Ali": {"Roman": ["Kürk Mantolu Madonna", "Kuyucaklı Yusuf", "İçimizdeki Şeytan"], "Hikaye": ["Değirmen", "Kağnı", "Ses", "Yeni Dünya", "Sırça Köşk", "Kamyon"]},
            "Ahmet Hamdi Tanpınar": {"Roman": ["Huzur", "Saatleri Ayarlama Enstitüsü", "Sahnenin Dışındakiler", "Mahur Beste", "Aydaki Kadın"], "Deneme": ["Beş Şehir", "Yaşadığım Gibi"]},
            "Necip Fazıl Kısakürek": {"Şiir": ["Çile", "Kaldırımlar", "Örümcek Ağı", "Ben ve Ötesi"], "Tiyatro": ["Bir Adam Yaratmak", "Reis Bey", "Tohum", "Para", "Sabır Taşı", "Ahşap Konak", "Yunus Emre"]},
            "Nazım Hikmet": {"Şiir": ["Memleketimden İnsan Manzaraları", "Kuvayi Milliye Destanı", "Simavne Kadısı Oğlu Bedreddin", "835 Satır", "Jokond ile Si-Ya-U", "Benerci Kendini Niçin Öldürdü", "Taranta Babu'ya Mektuplar"]},
            "Yaşar Kemal": {"Roman": ["İnce Memed", "Yer Demir Gök Bakır", "Ağrı Dağı Efsanesi", "Yılanı Öldürseler", "Orta Direk", "Teneke", "Demirciler Çarşısı Cinayeti", "Binboğalar Efsanesi", "Çakırcalı Efe", "Ölmez Otu", "Yusufçuk Yusuf"]},
            "Orhan Pamuk": {"Roman": ["Kara Kitap", "Benim Adım Kırmızı", "Masumiyet Müzesi", "Cevdet Bey ve Oğulları", "Sessiz Ev", "Kar", "Beyaz Kale", "Yeni Hayat", "Kafamda Bir Tuhaflık", "Kırmızı Saçlı Kadın"]},
            "Oğuz Atay": {"Roman": ["Tutunamayanlar", "Tehlikeli Oyunlar", "Bir Bilim Adamının Romanı", "Eylembilim"], "Hikaye": ["Korkuyu Beklerken"], "Tiyatro": ["Oyunlarla Yaşayanlar"]},
            "Attila İlhan": {"Şiir": ["Ben Sana Mecburum", "Sisler Bulvarı", "Duvar", "Yağmur Kaçağı", "Elde Var Hüzün", "Bela Çiçeği", "Yasak Sevişmek"], "Roman": ["Kurtlar Sofrası", "Sokaktaki Adam", "Bıçağın Ucu", "Sırtlan Payı", "Dersaadet'te Sabah Ezanları"]},
            "Cemal Süreya": {"Şiir": ["Üvercinka", "Sevda Sözleri", "Göçebe", "Beni Öp Sonra Doğur Beni", "Uçurumda Açan", "Sıcak Nal", "Güz Bitiği"]},
            "Adalet Ağaoğlu": {"Roman": ["Ölmeye Yatmak", "Bir Düğün Gecesi", "Fikrimin İnce Gülü", "Yüksek Gerilim", "Ruh Üşümesi", "Hayır", "Yazsonu", "Üç Beş Kişi"]},
            "Orhan Kemal": {"Roman": ["Bereketli Topraklar Üzerinde", "Murtaza", "Eskici ve Oğulları", "Hanımın Çiftliği", "Cemile", "Baba Evi", "Avare Yıllar", "Gurbet Kuşları", "Devlet Kuşu", "Vukuat Var", "Gavurun Kızı"]},
            "Kemal Tahir": {"Roman": ["Devlet Ana", "Yorgun Savaşçı", "Esir Şehrin İnsanları", "Rahmet Yolları Kesti", "Köyün Kamburu", "Yol Ayrımı", "Kurt Kanunu", "Bozkırdaki Çekirdek", "Sağırdere"]},
            "Refik Halit Karay": {"Hikaye": ["Memleket Hikayeleri", "Gurbet Hikayeleri"], "Roman": ["Sürgün", "Bugünün Saraylısı", "Yezidin Kızı", "Nilgün", "Çete", "Anahtar", "İstanbul'un İçyüzü"]},
            "Mehmet Akif Ersoy": {"Şiir": ["Safahat"]},
            "Yahya Kemal Beyatlı": {"Şiir": ["Kendi Gök Kubbemiz", "Eski Şiirin Rüzgarıyla"], "Nesir": ["Aziz İstanbul", "Eğil Dağlar", "Siyasi Hikayeler"]},
            "Faruk Nafiz Çamlıbel": {"Şiir": ["Han Duvarları", "Çoban Çeşmesi", "Dinle Neyden", "Gönülden Gönüle"], "Tiyatro": ["Akın", "Canavar", "Yayla Kartalı"]},
            "Memduh Şevket Esendal": {"Roman": ["Ayaşlı ve Kiracıları", "Vassaf Bey"], "Hikaye": ["Otlakçı", "Mendil Altında", "Temiz Sevgiler", "Ev Ona Yakıştı"]},
            "Orhan Veli Kanık": {"Şiir": ["Garip", "Vazgeçemediğim", "Destan Gibi", "Yenisi", "Karşı"]},
            "Cahit Sıtkı Tarancı": {"Şiir": ["Otuz Beş Yaş", "Düşten Güzel", "Ömrümde Sükut", "Ziya'ya Mektuplar"]},
            "Ahmet Muhip Dıranas": {"Şiir": ["Fahriye Abla", "Serenad", "Olvido", "Kar"], "Tiyatro": ["Gölgeler", "O Böyle İstemezdi"]},
            "Ziya Osman Saba": {"Şiir": ["Sebil ve Güvercinler", "Geçen Zaman", "Nefes Almak"], "Hikaye": ["Mesut İnsanlar Fotoğrafhanesi", "Değişen İstanbul"]},
            "Arif Damar": {"Şiir": ["Günden Güne", "İstanbul Bulutu", "Kedi Aklı", "Saat Sekizi Geç Vurdu"]},
            "Ferit Edgü": {"Roman": ["Hakkari'de Bir Mevsim (O)", "Kimse"], "Hikaye": ["Bir Gemide", "Çığlık", "Doğu Öyküleri", "Eylülün Gölgesinde Bir Yazdı"]},
            "Enis Behiç Koryürek": {"Şiir": ["Miras", "Güneşin Ölümü"], "Destan": ["Gemiciler"]},
            "Behçet Necatigil": {"Şiir": ["Kapalı Çarşı", "Evler", "Çevre", "Divançe", "Eski Toprak", "Yaz Dönemi"]},
            "Hilmi Yavuz": {"Şiir": ["Bakış Kuşu", "Bedreddin Üzerine Şiirler", "Doğu Şiirleri", "Gizemli Şiirler", "Zaman Şiirleri"]},
            "Cahit Külebi": {"Şiir": ["Adamın Biri", "Rüzgar", "Atatürk Kurtuluş Savaşı'nda", "Yeşeren Otlar", "Süt", "Türk Mavisi"]},
            "Fazıl Hüsnü Dağlarca": {"Şiir": ["Havaya Çizilen Dünya", "Çocuk ve Allah", "Üç Şehitler Destanı", "Çakırın Destanı", "Toprak Ana"]},
            "Salah Birsel": {"Deneme": ["Kahveler Kitabı", "Ah Beyoğlu Vah Beyoğlu", "Boğaziçi Şıngır Mıngır", "Sergüzeşt-i Nono Bey"], "Şiir": ["Dünya İşleri"]},
            "Oktay Rifat": {"Şiir": ["Perçemli Sokak", "Karga ile Tilki", "Aşık Merdiveni", "Elleri Var Özgürlüğün", "Yaşayıp Ölmek"]},
            "Melih Cevdet Anday": {"Şiir": ["Rahatı Kaçan Ağaç", "Kolları Bağlı Odysseus", "Telgrafhane", "Teknenin Ölümü", "Göçebe Denizin Üstünde"]},
            "Yusuf Atılgan": {"Roman": ["Aylak Adam", "Anayurt Oteli", "Canistan"]},
            "Haldun Taner": {"Tiyatro": ["Keşanlı Ali Destanı", "Gözlerimi Kaparım Vazifemi Yaparım", "Sersem Kocanın Kurnaz Karısı"], "Hikaye": ["Şişhaneye Yağmur Yağıyordu", "On İkiye Bir Var", "Yalıda Sabah", "Sancho'nun Sabah Yürüyüşü"]},
            "Sezai Karakoç": {"Şiir": ["Monna Rosa", "Körfez", "Hızırla Kırk Saat", "Şahdamar", "Taha'nın Kitabı", "Gül Muştusu"]},
            "Turgut Uyar": {"Şiir": ["Göğe Bakma Durağı", "Dünyanın En Güzel Arabistanı", "Tütünler Islak", "Divan", "Kayayı Delen İncir"]},
            "Edip Cansever": {"Şiir": ["Yerçekimli Karanfil", "Masa Da Masaymış", "İkindi Üstü", "Dirlik Düzenlik", "Tragedyalar", "Ben Ruhi Bey Nasılım"]},
            "Ece Ayhan": {"Şiir": ["Bakışsız Bir Kedi Kara", "Yort Savul", "Kinar Hanımın Denizleri", "Devlet ve Tabiat", "Sivil Şiirler"]},
            "Falih Rıfkı Atay": {"Anı": ["Çankaya", "Zeytindağı", "Ateş ve Güneş"], "Gezi": ["Deniz Aşırı", "Taymis Kıyıları", "Tuna Kıyıları", "Bizim Akdeniz"]},
            "Nurullah Ataç": {"Deneme": ["Günlerin Getirdiği", "Karalama Defteri", "Sözden Söze", "Okuruma Mektuplar", "Prospero ile Caliban"]},
            "Ahmet Kutsi Tecer": {"Şiir": ["Orada Bir Köy Var Uzakta"], "Tiyatro": ["Koçyiğit Köroğlu", "Köşebaşı", "Satılık Ev", "Bir Pazar Günü"]},
            "Fakir Baykurt": {"Roman": ["Yılanların Öcü", "Kaplumbağalar", "Tırpan", "Irazca'nın Dirliği", "Onuncu Köy"]},
            "Latife Tekin": {"Roman": ["Sevgili Arsız Ölüm", "Berci Kristin Çöp Masalları", "Gece Dersleri", "Buzdan Kılıçlar"]},
            "Mehmet Rauf": {"Roman": ["Eylül", "Genç Kız Kalbi", "Karanfil ve Yasemin", "Halas"], "Hikaye": ["Son Emel", "Aşıkane"]},
            "Hüseyin Rahmi Gürpınar": {"Roman": ["Şıpsevdi", "Mürebbiye", "Kuyruklu Yıldız Altında Bir İzdivaç", "Gulyabani", "Cadı", "İffet", "Metres"]}
        }
    
    elif kategori == "SERVET-İ FÜNUN":
        return {
            "Tevfik Fikret": {"Şiir": ["Rübab-ı Şikeste", "Haluk'un Defteri", "Rübabın Cevabı", "Şermin", "Tarih-i Kadim", "Doksan Beşe Doğru"], "Manzum Hikaye": ["Balıkçılar", "Nesrin", "Ramaksan", "Hasta Çocuk"]},
            "Cenap Şahabettin": {"Şiir": ["Tamat", "Elhan-ı Şita"], "Gezi": ["Hac Yolunda", "Avrupa Mektupları", "Suriye Mektupları", "Afaq-ı Irak"], "Tiyatro": ["Yalan", "Körebe", "Küçükbeyler"], "Özdeyiş": ["Tiryaki Sözleri"]},
            "Halit Ziya Uşaklıgil": {"Roman": ["Mai ve Siyah", "Aşk-ı Memnu", "Kırık Hayatlar", "Nemide", "Bir Ölünün Defteri", "Ferdi ve Şürekası", "Sefile", "Nesl-i Ahir"], "Hikaye": ["İzmir Hikayeleri", "Bir Şi'r-i Hayal", "Bir Yazın Tarihi", "Solgun Demet", "Aşka Dair", "Onu Beklerken"], "Anı": ["Kırk Yıl", "Saray ve Ötesi", "Bir Acı Hikaye"]},
            "Mehmet Rauf": {"Roman": ["Eylül", "Genç Kız Kalbi", "Karanfil ve Yasemin", "Halas", "Böğürtlen", "Son Yıldız", "Kan Damlası", "Define"], "Hikaye": ["Son Emel", "Aşıkane", "İhtizar", "Kadın İsterse", "Pervaneler gibi"], "Mensur Şiir": ["Siyah İnciler"]},
            "Hüseyin Cahit Yalçın": {"Roman": ["Nadide", "Hayal İçinde"], "Hikaye": ["Hayat-ı Muhayyel", "Niçin Aldatırlarmış", "Hayat-ı Hakikiye Sahneleri"], "Eleştiri": ["Kavgalarım"]},
            "Süleyman Nazif": {"Şiir": ["Gizli Figanlar", "Firak-ı Irak", "Batarya ile Ateş", "Malta Geceleri"], "Nesir": ["Çal Çoban Çal", "Tarihin Yılan Hikayesi"]},
            "Ahmet Hikmet Müftüoğlu": {"Hikaye": ["Haristan ve Gülistan", "Çağlayanlar"], "Roman": ["Gönül Hanım"]},
            "Hüseyin Suat Yalçın": {"Tiyatro": ["Kirli Çamaşırlar", "Çürük Temel", "Kayseri Gülleri", "Şehbal yahut İstibdadın Son Perdesi"], "Mizah": ["Gave-i Zalim (Takma adıyla)"]},
            "Ali Ekrem Bolayır": {"Şiir": ["Zilal-i İlham", "Vicdan Alevleri", "Ordunun Defteri", "Şiir Demeti"]},
            "Faik Ali Ozansoy": {"Şiir": ["Fani Teselliler", "Temasil", "Elhan-ı Vatan"]},
            "Celal Sahir Erozan": {"Şiir": ["Beyaz Gölgeler", "Buhran", "Siyah Kitap"]}
        }

    elif kategori == "TANZİMAT":
        return {
            "Namık Kemal": {"Roman": ["İntibah", "Cezmi"], "Tiyatro": ["Vatan Yahut Silistre", "Gülnihal", "Akif Bey", "Zavallı Çocuk", "Kara Bela", "Celaleddin Harzemşah"], "Eleştiri": ["Tahrib-i Harabat", "Takip"], "Tarih": ["Osmanlı Tarihi", "Kanije"]},
            "Şinasi": {"Tiyatro": ["Şair Evlenmesi"], "Şiir": ["Müntehabat-ı Eş'ar"], "Derleme": ["Durub-ı Emsal-i Osmaniye"], "Makale": ["Tercüman-ı Ahval Mukaddimesi"]},
            "Ziya Paşa": {"Şiir": ["Eş'ar-ı Ziya"], "Antoloji": ["Harabat"], "Hiciv": ["Zafername"], "Anı": ["Defter-i Amal"], "Tercüme": ["Rüya", "Engizisyon Tarihi"]},
            "Ahmet Mithat Efendi": {"Roman": ["Felatun Bey ile Rakım Efendi", "Hasan Mellah", "Hüseyin Fellah", "Paris'te Bir Türk", "Henüz On Yedi Yaşında", "Dürdane Hanım", "Müşahedat", "Esaret"], "Hikaye": ["Letaif-i Rivayat", "Kıssadan Hisse"]},
            "Şemsettin Sami": {"Roman": ["Taaşşuk-ı Talat ve Fitnat"], "Sözlük": ["Kamus-ı Türki", "Kamus-ı Fransevi"], "Ansiklopedi": ["Kamus'ul Alam"], "Tiyatro": ["Besa yahut Ahde Vefa", "Gave", "Seydi Yahya"]},
            "Ahmet Vefik Paşa": {"Tiyatro (Çeviri/Uyarlama)": ["Zor Nikah", "Zoraki Tabip", "Azarya", "Tabib-i Aşk", "Meraki"], "Sözlük": ["Lehçe-i Osmani"], "Tarih": ["Şecere-i Türk Çevirisi"]},
            "Recaizade Mahmut Ekrem": {"Roman": ["Araba Sevdası"], "Şiir": ["Zemzeme", "Name-i Seher", "Yadigâr-ı Şebâb", "Pejmürde", "Nijad Ekrem"], "Tiyatro": ["Afife Anjelik", "Atala", "Vuslat", "Çok Bilen Çok Yanılır"], "Eleştiri": ["Takdir-i Elhan", "Talim-i Edebiyat"]},
            "Abdülhak Hamit Tarhan": {"Şiir": ["Makber", "Sahra", "Ölü", "Hacle", "Bunlar O'dur", "Divaneliklerim yahut Belde"], "Tiyatro": ["Eşber", "Finten", "Macera-yı Aşk", "Sabr u Sebat", "İçli Kız", "Duhter-i Hindu", "Tarık", "İbn-i Musa"]},
            "Samipaşazade Sezai": {"Roman": ["Sergüzeşt"], "Hikaye": ["Küçük Şeyler"], "Tiyatro": ["Şir"]},
            "Nabizade Nazım": {"Roman": ["Karabibik (Uzun Hikaye)", "Zehra"], "Hikaye": ["Yadigarlarım", "Haspa", "Zavallı Kız", "Bir Hatıra", "Sevda", "Hala Güzel"]},
            "Muallim Naci": {"Şiir": ["Ateşpare", "Şerare", "Füruzan", "Sünbüle"], "Anı": ["Ömer'in Çocukluğu"], "Sözlük": ["Lugat-i Naci"], "Eleştiri": ["Demdeme"]},
            "Direktör Ali Bey": {"Tiyatro": ["Ayyar Hamza", "Kokona Yatıyor", "Misafir-i İstiskal"], "Mizah": ["Lehçetü'l Hakayık"], "Gezi": ["Seyahat Jurnali"]},
            "Akif Paşa": {"Anı": ["Tabsıra"], "Şiir": ["Adem Kasidesi"]},
            "Sadullah Paşa": {"Şiir": ["Ondokuzuncu Asır Manzumesi"]},
            "Mizancı Murat": {"Roman": ["Turfanda mı Yoksa Turfa mı"]}
        }

    else: # DİVAN
        return {
            "Fuzuli": {"Mesnevi": ["Leyla ile Mecnun", "Bengü Bade", "Sohbetü'l Esmar"], "Nesir": ["Şikayetname", "Hadikatü's Süeda", "Rind ü Zahid"]},
            "Baki": {"Şiir": ["Kanuni Mersiyesi", "Baki Divanı"], "Nesir": ["Fezail-i Mekke"]},
            "Nefi": {"Hiciv": ["Siham-ı Kaza"], "Mesnevi": ["Tuhfetü’l-Uşşak"]},
            "Nabi": {"Mesnevi": ["Hayriye", "Hayrabad", "Surname"], "Gezi": ["Tuhfetü'l Haremeyn"]},
            "Şeyh Galip": {"Mesnevi": ["Hüsnü Aşk"]},
            "Şeyhi": {"Fabl": ["Harname"], "Mesnevi": ["Hüsrev ü Şirin"]},
            "Katip Çelebi": {"Bibliyografya": ["Keşfü'z Zunun"], "Coğrafya": ["Cihannüma"], "Tarih": ["Fezleke", "Takvimü't Tevarih"]},
            "Evliya Çelebi": {"Gezi": ["Seyahatname"]},
            "Ali Şir Nevai": {"Sözlük": ["Muhakemetü'l Lügateyn"], "Tezkire": ["Mecalisü'n Nefais"], "Mesnevi": ["Lisanü't Tayr", "Ferhad ü Şirin"]},
            "Sinan Paşa": {"Süslü Nesir": ["Tazarruname", "Maarifname"]},
            "Mercimek Ahmet": {"Sade Nesir": ["Kabusname"]},
            "Süleyman Çelebi": {"Mesnevi": ["Vesiletü'n Necat (Mevlid)"]},
            "Ahmedi": {"Mesnevi": ["İskendername", "Cemşid ü Hurşid"]},
            "Babürşah": {"Anı": ["Babürname"]},
            "Seydi Ali Reis": {"Gezi": ["Mir'atü'l Memalik", "Kitabül Muhit"]},
            "Yirmisekiz Çelebi Mehmet": {"Sefaretname": ["Paris Sefaretnamesi"]},
            "Gülşehri": {"Mesnevi": ["Mantıku't Tayr", "Felekname"]},
            "Kaygusuz Abdal": {"Nesir": ["Budalaname", "Muglataname", "Gevhername"]},
            "Aşık Paşa": {"Mesnevi": ["Garibname"]},
            "Hoca Dehhani": {"Destan": ["Selçuklu Şehnamesi"]},
            "Kadı Burhaneddin": {"Şiir": ["Tuyuğlar"]},
            "Nedim": {"Şiir": ["Şarkı Formu", "Nedim Divanı"]},
            "Nergisi": {"Nesir": ["Nergisi Hamsesi"]},
            "Veysi": {"Nesir": ["Habname"]},
            "Karacaoğlan": {"Şiir": ["Koşma", "Semai", "Varsağı"]},
            "Pir Sultan Abdal": {"Şiir": ["Nefesler", "Şathiyeler"]},
            "Eşrefoğlu Rumi": {"Tasavvuf": ["Müzekkin Nüfus"]},
            "Taşlıcalı Yahya": {"Mesnevi": ["Şah ü Geda", "Yusuf ü Züleyha"]},
            "Zati": {"Mesnevi": ["Şem ü Pervane"]}
        }

@st.cache_data
def get_ozet_db():
    return [
        {"yazar": "Namık Kemal", "roman": "İntibah", "ozet": "Ali Bey, mirasyedi bir gençtir. Mahpeyker adlı hafif meşrep bir kadına aşık olur. Dilaşub adlı cariye ile Mahpeyker arasında kalır. **Özellik:** Türk edebiyatının ilk edebi romanıdır."},
        {"yazar": "Namık Kemal", "roman": "Cezmi", "ozet": "II. Selim döneminde İran'la yapılan savaşları ve Cezmi'nin kahramanlıklarını anlatır. **Özellik:** Türk edebiyatının ilk tarihi romanıdır."},
        {"yazar": "Recaizade Mahmut Ekrem", "roman": "Araba Sevdası", "ozet": "Bihruz Bey, alafrangalık özentisi, mirasyedi bir gençtir. Periveş adlı kadını soylu sanır. **Özellik:** Yanlış batılılaşmayı işleyen ilk realist romandır."},
        {"yazar": "Samipaşazade Sezai", "roman": "Sergüzeşt", "ozet": "Kafkasya'dan kaçırılıp İstanbul'a getirilen esir kız Dilber'in acıklı hikayesi. Dilber, Celal Bey'e aşık olur ama Nil Nehri'ne atlayarak intihar eder. **Özellik:** Esaret konusunu işleyen, romantizmden realizme geçiş eseridir."},
        {"yazar": "Halit Ziya Uşaklıgil", "roman": "Mai ve Siyah", "ozet": "Ahmet Cemil'in şair olma hayalleri (Mai) ile hayatın acı gerçekleri (Siyah) arasındaki çatışma anlatılır. **Özellik:** Batılı anlamda (teknik olarak kusursuz) ilk romandır."},
        {"yazar": "Halit Ziya Uşaklıgil", "roman": "Aşk-ı Memnu", "ozet": "Bihter, Adnan Bey ile evlenir ancak Behlül ile yasak aşk yaşar. Firdevs Hanım, Nihal ve Beşir diğer karakterlerdir. **Özellik:** Türk edebiyatının en başarılı realist romanıdır."},
        {"yazar": "Mehmet Rauf", "roman": "Eylül", "ozet": "Suat, Süreyya ve Necip arasındaki yasak aşkı anlatan, olaydan çok psikolojik tahlillere dayanan eserdir. **Özellik:** İlk psikolojik romandır."},
        {"yazar": "Hüseyin Rahmi Gürpınar", "roman": "Şıpsevdi", "ozet": "Meftun Bey, alafranga züppe bir tiptir. Zengin Kasım Efendi'nin kızı Edibe ile parası için evlenmek ister. **Özellik:** Yanlış batılılaşmayı mizahi bir dille eleştirir."},
        {"yazar": "Yakup Kadri Karaosmanoğlu", "roman": "Yaban", "ozet": "Ahmet Celal, bir Anadolu köyüne yerleşir. Köylü onu düşman ve 'Yaban' olarak görür. **Özellik:** Aydın-Halk çatışmasını işleyen ilk tezli romandır."},
        {"yazar": "Yakup Kadri Karaosmanoğlu", "roman": "Kiralık Konak", "ozet": "Naim Efendi (Gelenek), Servet Bey (Yozlaşma) ve Seniha (Köklerinden kopuş) üzerinden üç nesil arasındaki çatışmayı anlatır. **Özellik:** Kuşak çatışmasını en iyi işleyen romandır."},
        {"yazar": "Yakup Kadri Karaosmanoğlu", "roman": "Sodom ve Gomore", "ozet": "Mütareke dönemi İstanbul'unda işgalcilerle işbirliği yapan yozlaşmış çevreleri anlatır. Leyla ve Necdet baş karakterlerdir."},
        {"yazar": "Reşat Nuri Güntekin", "roman": "Çalıkuşu", "ozet": "Feride, Kamran'a küsüp Anadolu'da öğretmenlik yapar. **Özellik:** İdealist öğretmen tipini Anadolu'ya sevdiren romandır."},
        {"yazar": "Reşat Nuri Güntekin", "roman": "Yeşil Gece", "ozet": "Öğretmen Şahin Efendi'nin softalarla ve yobazlıkla mücadelesini anlatır. **Özellik:** İrtica ile mücadeleyi anlatan tezli bir romandır."},
        {"yazar": "Reşat Nuri Güntekin", "roman": "Yaprak Dökümü", "ozet": "Ali Rıza Bey ve ailesinin yanlış batılılaşma ve ahlaki çöküş nedeniyle dağılmasını anlatır. Toplumsal değişimi işler."},
        {"yazar": "Halide Edip Adıvar", "roman": "Sinekli Bakkal", "ozet": "Rabia ve Peregrini aşkı üzerinden II. Abdülhamit dönemi İstanbul'unu ve Doğu-Batı sentezini anlatır. **Özellik:** Töre romanı özelliği taşır."},
        {"yazar": "Halide Edip Adıvar", "roman": "Vurun Kahpeye", "ozet": "Aliye Öğretmen'in Anadolu'da yobaz Hacı Fettah ve işbirlikçiler tarafından linç edilmesini anlatır. **Özellik:** Kurtuluş Savaşı'nı işleyen önemli romanlardandır."},
        {"yazar": "Halide Edip Adıvar", "roman": "Ateşten Gömlek", "ozet": "Ayşe, Peyami ve İhsan'ın Anadolu'ya geçip Milli Mücadele'ye katılmasını anlatır. **Özellik:** Kurtuluş Savaşı üzerine yazılan ilk romandır."},
        {"yazar": "Peyami Safa", "roman": "Dokuzuncu Hariciye Koğuşu", "ozet": "Hasta bir çocuğun bacağındaki kemik veremi ve Nüzhet'e olan aşkı. **Özellik:** Otobiyografik özellikler taşıyan psikolojik romandır."},
        {"yazar": "Peyami Safa", "roman": "Fatih-Harbiye", "ozet": "Neriman'ın Fatih (Doğu) ile Harbiye (Batı) arasında kalışını, Şinasi ve Macit üzerinden anlatır. Doğu-Batı çatışması işlenir."},
        {"yazar": "Ahmet Hamdi Tanpınar", "roman": "Saatleri Ayarlama Enstitüsü", "ozet": "Hayri İrdal ve Halit Ayarcı üzerinden Türk toplumunun modernleşme ironisi anlatılır. **Özellik:** Doğu-Batı ikilemini ironik dille anlatan postmodern bir eserdir."},
        {"yazar": "Ahmet Hamdi Tanpınar", "roman": "Huzur", "ozet": "Mümtaz ve Nuran aşkı, İstanbul sevgisi ve II. Dünya Savaşı huzursuzluğu işlenir. **Özellik:** Bilinç akışı tekniğinin kullanıldığı, şiirsel üsluplu romandır."},
        {"yazar": "Oğuz Atay", "roman": "Tutunamayanlar", "ozet": "Turgut Özben, intihar eden arkadaşı Selim Işık'ın izini sürer. Küçük burjuva aydınının dramını anlatır. **Özellik:** Türk edebiyatının ilk postmodern romanıdır."},
        {"yazar": "Orhan Pamuk", "roman": "Kara Kitap", "ozet": "Galip, kayıp karısı Rüya'yı ve Celal'i İstanbul sokaklarında arar. **Özellik:** Şeyh Galip'in Hüsn ü Aşk'ına göndermeler içeren postmodern bir romandır."},
        {"yazar": "Yaşar Kemal", "roman": "İnce Memed", "ozet": "Abdi Ağa'nın zulmüne başkaldıran Memed'in dağa çıkıp eşkıya olmasını ve köylü haklarını savunmasını anlatır. **Özellik:** Eşkıyalık ve başkaldırı temasını işleyen destansı romandır."},
        {"yazar": "Sabahattin Ali", "roman": "Kürk Mantolu Madonna", "ozet": "Raif Efendi'nin Almanya'da Maria Puder ile yaşadığı hüzünlü aşk ve sonrasında içine kapanışı anlatılır. Yalnızlık ve yabancılaşma temalıdır."},
        {"yazar": "Sabahattin Ali", "roman": "Kuyucaklı Yusuf", "ozet": "Yusuf'un ailesinin öldürülmesi, Kaymakam tarafından evlat edinilmesi ve Muazzez'e olan aşkı anlatılır. **Özellik:** Kasaba gerçekçiliğini işleyen ilk önemli romandır."},
        {"yazar": "Yusuf Atılgan", "roman": "Anayurt Oteli", "ozet": "Otel katibi Zebercet'in yalnızlığı ve psikolojik çöküşü. Gecikmeli Ankara treniyle gelen kadını bekler. **Özellik:** Yabancılaşma konusunu işleyen modernist bir eserdir."},
        {"yazar": "Adalet Ağaoğlu", "roman": "Ölmeye Yatmak", "ozet": "Aysel'in bir otel odasında intiharı düşünürken geçmişiyle hesaplaşması. Cumhuriyet dönemi aydınının sorgulamasını içerir."},
        {"yazar": "Ferit Edgü", "roman": "Hakkari'de Bir Mevsim", "ozet": "Bir öğretmenin Hakkari'nin Pirkanis köyündeki yalnızlığı ve köylülerle iletişimi (O adlı roman). **Özellik:** Küçürek öykü tekniğine yakın, varoluşçu bir romandır."},
        {"yazar": "Kemal Tahir", "roman": "Devlet Ana", "ozet": "Osmanlı'nın kuruluşunu, Ertuğrul Gazi ve Osman Bey üzerinden anlatan tarihi romandır. **Özellik:** Batılılaşmaya karşı yerli bir roman dili oluşturma çabasıdır."},
        {"yazar": "Kemal Tahir", "roman": "Yorgun Savaşçı", "ozet": "Milli Mücadele dönemini Cehennem Yüzbaşı Cemil üzerinden anlatan tarihi roman. İttihatçıların mücadelesi işlenir."},
        {"yazar": "Tarık Buğra", "roman": "Küçük Ağa", "ozet": "İstanbullu Hoca'nın Kuvayi Milliye karşıtlığından, Akşehir'de bilinçlenerek Milli Mücadele destekçisine dönüşmesi. **Özellik:** Milli Mücadele'ye insan psikolojisi üzerinden bakan romandır."},
        {"yazar": "Orhan Kemal", "roman": "Bereketli Topraklar Üzerinde", "ozet": "Çukurova'ya çalışmaya giden üç arkadaşın (İflahsızın Yusuf, Köse Hasan, Pehlivan Ali) dramı. **Özellik:** İşçi sınıfının sorunlarını anlatan toplumcu gerçekçi bir eserdir."},
        {"yazar": "Nabizade Nazım", "roman": "Zehra", "ozet": "Zehra'nın kocası Suphi'ye olan hastalıklı kıskançlığı ve ailenin çöküşü anlatılır. **Özellik:** İlk psikolojik roman denemesidir."},
        {"yazar": "Nabizade Nazım", "roman": "Karabibik", "ozet": "Antalya'nın Kaş ilçesinde geçer. Karabibik'in tarlasını sürmek için öküz alma çabası anlatılır. **Özellik:** İlk köy romanıdır."},
        {"yazar": "Şemsettin Sami", "roman": "Taaşşuk-ı Talat ve Fitnat", "ozet": "Talat ve Fitnat'ın aşkı, görücü usulü evliliğin sakıncaları anlatılır. **Özellik:** İlk yerli romandır."},
        {"yazar": "Yusuf Atılgan", "roman": "Aylak Adam", "ozet": "C. adlı karakterin İstanbul sokaklarında 'B'yi (aradığı kadını) araması ve topluma yabancılaşması. **Özellik:** Modernist Türk romanının en önemli örneklerindendir."},
        {"yazar": "Latife Tekin", "roman": "Sevgili Arsız Ölüm", "ozet": "Köyden kente göç eden bir ailenin batıl inançlarla dolu fantastik hikayesi. **Özellik:** Büyülü gerçekçilik akımının Türk edebiyatındaki önemli örneğidir."}
    ]

# GENİŞLETİLMİŞ SÖZ SANATLARI VERİTABANI (YAZARLAR EKLENDİ VE ÇEŞİTLENDİRİLDİ)
@st.cache_data
def get_sanatlar_db():
    return [
        {"sanat": "Teşbih (Benzetme)", "beyit": "Cennet gibi güzel vatanım...", "aciklama": "Burada vatan (benzeyen), cennete (benzetilen) benzetilmiştir. 'Gibi' edatı kullanılmıştır.", "yazar": "Anonim"},
        {"sanat": "İstiare (Eğretileme)", "beyit": "Şakaklarıma kar mı yağdı ne var? / Benim mi Allahım bu çizgili yüz?", "aciklama": "Beyaz saç 'kar'a benzetilmiş ama sadece kar söylenmiş.", "yazar": "Cahit Sıtkı Tarancı"},
        {"sanat": "Tezat (Zıtlık)", "beyit": "Ağlarım hatıra geldikçe gülüştüklerimiz.", "aciklama": "Ağlamak ve gülüşmek zıt eylemlerdir.", "yazar": "Mahmut Ekrem"},
        {"sanat": "Hüsnü Talil (Güzel Neden)", "beyit": "Güzel şeyler düşünelim diye / Yemyeşil oluvermiş ağaçlar", "aciklama": "Ağaçların yeşermesi güzel düşünmeye bağlanmış.", "yazar": "Melih Cevdet Anday"},
        {"sanat": "Telmih (Hatırlatma)", "beyit": "Gökyüzünde İsa ile, Tur dağında Musa ile / Elindeki asâ ile, çağırayım Mevlâm seni", "aciklama": "Peygamber kıssalarına gönderme.", "yazar": "Yunus Emre"},
        {"sanat": "Tecahülü Arif (Bilmezlik)", "beyit": "Göz gördü gönül sevdi seni ey yüzü mahım / Kurbanın olam var mı benim bunda günahım?", "aciklama": "Şair aşık olduğunu bildiği halde bilmezden geliyor.", "yazar": "Nahifi"},
        {"sanat": "Mübalağa (Abartma)", "beyit": "Bir ah çeksem dağı taşı eritir / Gözüm yaşı değirmeni yürütür", "aciklama": "Gözyaşıyla değirmen yürütmek imkansız bir abartıdır.", "yazar": "Karacaoğlan"},
        {"sanat": "İntak (Konuşturma)", "beyit": "Ben ki toz kanatlı bir kelebeğim / Minicik gövdeme yüklü Kafdağı", "aciklama": "Kelebek konuşturulmuştur.", "yazar": "Cahit Külebi"},
        {"sanat": "Tevriye (İki Anlamlılık)", "beyit": "Bu kadar letafet çünkü sende var / Beyaz gerdanında bir de ben gerek", "aciklama": "'Ben' kelimesi hem kişi hem vücut lekesi.", "yazar": "Nedim"},
        {"sanat": "Teşhis (Kişileştirme)", "beyit": "Haliç'te bir vapuru vurdular dört kişi / Demirlemişti eli kolu bağlıydı ağlıyordu", "aciklama": "Vapura insani özellikler (eli kolu bağlı olmak, ağlamak) verilmiştir.", "yazar": "Attila İlhan"},
        {"sanat": "Rücu (Geri Dönüş)", "beyit": "Erbab-ı teşair çoğalıp şair azaldı / Yok öyle değil, şairin ancak adı kaldı", "aciklama": "Şair önce bir söz söyleyip sonra 'yok öyle değil' diyerek fikrini değiştirmiş gibi yapıyor.", "yazar": "Muallim Naci"},
        {"sanat": "Tezil (Şaka/Alay)", "beyit": "Benim şiirim böyledir işte / Okuyanlar olur hep birer işte", "aciklama": "Ciddi bir konuyu alaya alarak veya şaka yollu anlatma sanatı.", "yazar": "Anonim"},
        {"sanat": "Leff ü Neşr", "beyit": "Gönlümde ateş, gözümde yaşlar / Biri yakar, biri boğar", "aciklama": "Ateş-yakar, yaş-boğar simetrisi.", "yazar": "Anonim"},
        {"sanat": "Terdid", "beyit": "Dişin mi ağrıyor, çek kurtul / Başın mı ağrıyor, bir çeyreğe iki aspirin / Verem misin, üzülme, onun da çaresi var / Ölür gidersin", "aciklama": "Beklenmedik sonla bitirme.", "yazar": "Orhan Veli Kanık"},
        {"sanat": "İktibas", "beyit": "Zalimin zulmü varsa, mazlumun Allah'ı var / 'İnnallahe meassabirin' dedi", "aciklama": "Ayet alıntısı.", "yazar": "Anonim"},
        {"sanat": "İrsal-i Mesel", "beyit": "Balık baştan kokar bunu bilmemek / Seyrani gafilin ahmaklığıdır", "aciklama": "Atasözü kullanma.", "yazar": "Seyrani"},
        {"sanat": "Cinas", "beyit": "Niçin kondun a bülbül kapımdaki asmaya / Ben yarimden vazgeçmem götürseler asmaya", "aciklama": "Asma (bitki) - Asma (idam).", "yazar": "Anonim (Mani)"},
        {"sanat": "Kinaye", "beyit": "Bulamadım dünyada gönüle mekan / Nerde bir gül bitse etrafı diken", "aciklama": "Hem gerçek (gülün dikeni) hem mecaz (güzelliğin yanında sıkıntı olması) anlamı kastedilmiş.", "yazar": "Sümmani"},
        {"sanat": "Tariz", "beyit": "Bir yetim görünce döktür dişini / Bozmaya çabala halkın işini / Günde yüz adamın vur kır başını", "aciklama": "Söylenenin tam tersini kastederek kişiyi iğneleme sanatı.", "yazar": "Neyzen Tevfik"},
        {"sanat": "Tekrir", "beyit": "Kaldırımlar, çilekeş yalnızların annesi / Kaldırımlar, içimde yaşamış bir insandır", "aciklama": "'Kaldırımlar' kelimesi tekrar edilerek ahenk sağlanmış.", "yazar": "Necip Fazıl Kısakürek"},
        {"sanat": "Mübalağa", "beyit": "Merkez-i hakkaatsın girye-i cihan / Bütün dünya ağlasa, ben gülmem", "aciklama": "Bütün dünyanın ağlaması imkansız bir abartıdır.", "yazar": "Namık Kemal"},
        {"sanat": "Tenasüp", "beyit": "Aramazdık gece mehtabı yüzün parlarken / Bir uzak yıldıza benzerdi güneş sen varken", "aciklama": "Gece, mehtap, yıldız, güneş birbiriyle uyumlu kelimelerdir.", "yazar": "Faruk Nafiz Çamlıbel"},
        {"sanat": "Telmih", "beyit": "Ne büyüksün ki kanın kurtarıyor tevhidi / Bedr'in aslanları ancak bu kadar şanlı idi", "aciklama": "Bedir Savaşı'na ve İslam tarihine gönderme yapılmış.", "yazar": "Mehmet Akif Ersoy"},
        {"sanat": "İstifham", "beyit": "Kim bu cennet vatanın uğruna olmaz ki feda?", "aciklama": "Cevap bekleme amacı gütmeden soru sorma sanatı.", "yazar": "Mehmet Akif Ersoy"},
        {"sanat": "Nida", "beyit": "Ey mavi göklerin beyaz ve kızıl süsü!", "aciklama": "Seslenme sanatı.", "yazar": "Arif Nihat Asya"},
        {"sanat": "Seci", "beyit": "İlahi, kabul senden, ret senden / Şifa senden, dert senden", "aciklama": "Düzyazıda veya şiirde cümle sonlarında yapılan iç kafiye.", "yazar": "Sinan Paşa"},
        {"sanat": "Aliterasyon", "beyit": "Eylülde melul oldu gönül soldu da lale / Bir kaküle meyletti gönül geldi bu hale", "aciklama": "'L' harfinin sık tekrarıyla ahenk sağlanmış.", "yazar": "Edip Ayel"},
        {"sanat": "Asonans", "beyit": "Neysen sen, nefes sen, neylersin neyi / Neyzensen, nefessen neylersin neyi", "aciklama": "'E' sesinin sık tekrarıyla ahenk sağlanmış.", "yazar": "Anonim"},
        {"sanat": "Hüsnü Talil", "beyit": "Sen gelince güller açar bahçemde / Sen gidince solar bütün çiçekler", "aciklama": "Çiçeklerin açması veya solması sevgilinin gelişine/gidişine bağlanmış.", "yazar": "Anonim"},
        {"sanat": "Teşbih-i Beliğ", "beyit": "Selvi boylum, elma yanaklım", "aciklama": "Sadece benzeyen ve benzetilen unsurlar kullanılmış (Güzel benzetme).", "yazar": "Anonim"},
        {"sanat": "Mecaz-ı Mürsel", "beyit": "Bütün İstanbul sokağa döküldü", "aciklama": "İstanbul (Şehir) söylenip içindeki halk kastedilmiş.", "yazar": "Anonim"},
        {"sanat": "Kinaye", "beyit": "Dadaloğlu'm der ki belim büküldü / Gözümün cevheri yere döküldü", "aciklama": "Bel bükülmesi hem yaşlılık (gerçek) hem çaresizlik (mecaz) anlamında.", "yazar": "Dadaloğlu"},
        {"sanat": "Tariz", "beyit": "Yiyin efendiler yiyin, bu han-ı iştiha sizin", "aciklama": "Yiyin derken aslında 'yemeyin, sömürmeyin' demek istiyor.", "yazar": "Tevfik Fikret"},
        {"sanat": "Tevriye", "beyit": "Gül yağını eller sürünür çatlasa bülbül", "aciklama": "El (organ) ve El (yabancı) anlamı bir arada.", "yazar": "Nevres-i Kadim"},
        {"sanat": "Leff ü Neşr", "beyit": "Bakışların kor ateş, sözlerin buz gibi / Biri yakar derinden, biri üşütür", "aciklama": "Ateş-yakar, buz-üşütür kelimeleri simetrik.", "yazar": "Anonim"},
        {"sanat": "Rücu", "beyit": "Zaman gelir ki cihan içre ins ü can kalmaz / Değil değil, zemin kalır, zaman kalmaz", "aciklama": "Önce bir şey söyleyip sonra vazgeçip başka bir şey söyleme.", "yazar": "Ziya Paşa"},
        {"sanat": "İstifham", "beyit": "Hangi çılgın bana zincir vuracakmış? Şaşarım!", "aciklama": "Soru sorarak duyguyu güçlendirme.", "yazar": "Mehmet Akif Ersoy"},
        {"sanat": "Tedric", "beyit": "Geçsin günler, haftalar, aylar, mevsimler, yıllar", "aciklama": "Kavramların dereceli olarak sıralanması.", "yazar": "Enis Behiç Koryürek"},
        {"sanat": "Akis", "beyit": "Gamzen ciğerim deldi / Deldi ciğerim gamzen", "aciklama": "Sözün ters çevrilerek tekrar edilmesi.", "yazar": "Ali Şir Nevai"},
        {"sanat": "İştikak", "beyit": "Dünyada sevilmiş ve seven nafile bekler", "aciklama": "Sevmek kökünden türeyen kelimelerin bir arada kullanılması.", "yazar": "Yahya Kemal Beyatlı"},
        {"sanat": "Cinas", "beyit": "Kısmetindir gezdiren yer yer seni / Arşa çıksan akıbet yer yer seni", "aciklama": "Yer (Mekan) - Yer (Yemek fiili).", "yazar": "İbni Kemal"},
        {"sanat": "Telmih", "beyit": "Gökyüzünde İsa ile / Tur dağında Musa ile", "aciklama": "Peygamberlere gönderme.", "yazar": "Yunus Emre"},
        {"sanat": "Mübalağa", "beyit": "Aşkınla tutuştu gönül, yandı kül oldu / Gözyaşım sel oldu, aktı göl oldu", "aciklama": "Abartılı anlatım.", "yazar": "Aşık Veysel"},
        {"sanat": "Teşbih", "beyit": "Aslan gibi yiğitler, kükrerdi cephede / Düşmana korku salar, titretirdi her yerde", "aciklama": "Yiğitler aslana benzetilmiş.", "yazar": "Anonim"}
    ]

# YENİ OYUN MODU VERİTABANI: ŞAİR TAHMİN (KİM BU ŞAİR?)
@st.cache_data
def get_sair_tanimi_db():
    return [
        {"cevap": "Fuzuli", "ipucu": "16. yüzyıl Divan şairidir. Aşk ve ızdırap şairi olarak bilinir. 'Su Kasidesi' ve 'Leyla ile Mecnun' mesnevisi en ünlü eserleridir. Şikayetname adlı eseriyle ünlüdür."},
        {"cevap": "Baki", "ipucu": "16. yüzyıl Divan şairidir. 'Sultanü'ş Şuara' (Şairler Sultanı) olarak bilinir. Kanuni Mersiyesi ile tanınır. Din dışı konuları, zevk ve eğlenceyi işlemiştir."},
        {"cevap": "Nedim", "ipucu": "Lale Devri'nin en önemli şairidir. Şarkı nazım şeklinin en önemli temsilcisidir. İstanbul'u, eğlenceyi ve sadabadı anlatır. Mahallileşme akımının öncüsüdür."},
        {"cevap": "Nefi", "ipucu": "17. yüzyıl Hiciv (yergi) ustasıdır. 'Siham-ı Kaza' (Kaza Okları) adlı eseriyle bilinir. Övgüde de yergide de sınır tanımaz."},
        {"cevap": "Nabi", "ipucu": "Hikemi (öğretici) tarzın kurucusudur. 'Hayriye' adlı eseriyle oğluna öğütler verir. Düşünceye dayalı şiirler yazar."},
        {"cevap": "Şeyh Galip", "ipucu": "Divan edebiyatının son büyük şairidir. Sebk-i Hindi akımının temsilcisidir. 'Hüsn ü Aşk' adlı alegorik mesnevisiyle tanınır."},
        {"cevap": "Namık Kemal", "ipucu": "Vatan şairi olarak bilinir. Tanzimat 1. dönem sanatçısıdır. 'İntibah' (ilk edebi roman) ve 'Cezmi' (ilk tarihi roman) eserlerinin yazarıdır."},
        {"cevap": "Recaizade Mahmut Ekrem", "ipucu": "Tanzimat 2. dönem sanatçısıdır. 'Üstad' olarak anılır. 'Araba Sevdası' (ilk realist roman) eserinin yazarıdır. 'Sanat sanat içindir' anlayışını savunur."},
        {"cevap": "Abdülhak Hamit Tarhan", "ipucu": "Tanzimat 2. dönem şairidir. 'Şair-i Azam' olarak bilinir. 'Makber' şiiriyle eşinin ölümü üzerine duyduğu acıyı anlatır. Tezatlar şairidir."},
        {"cevap": "Tevfik Fikret", "ipucu": "Servet-i Fünun şiirinin en önemli temsilcisidir. 'Sis', 'Ferda', 'Balıkçılar' önemli şiirleridir. Hece ölçüsüyle sadece çocuklar için 'Şermin'i yazmıştır."},
        {"cevap": "Halit Ziya Uşaklıgil", "ipucu": "Türk romanının babası sayılır. Servet-i Fünun döneminin en büyük nesir ustasıdır. 'Mai ve Siyah', 'Aşk-ı Memnu' gibi başyapıtları vardır."},
        {"cevap": "Mehmet Akif Ersoy", "ipucu": "İstiklal Marşı şairimizdir. Milli Edebiyat dönemi bağımsız sanatçısıdır. 'Safahat' adlı eserinde şiirlerini toplamıştır. Realist bir şairdir."},
        {"cevap": "Yahya Kemal Beyatlı", "ipucu": "Milli Edebiyat dönemi bağımsızlarındandır. İstanbul şairi olarak bilinir. Aruz ölçüsünü Türkçeye başarıyla uygulamıştır. 'Kendi Gök Kubbemiz' önemli eseridir."},
        {"cevap": "Ahmet Haşim", "ipucu": "Fecr-i Ati topluluğunun en önemli temsilcisidir. Sembolizm ve Empresyonizm akımlarından etkilenmiştir. 'Piyale' ve 'Göl Saatleri' önemli eserleridir."},
        {"cevap": "Yakup Kadri Karaosmanoğlu", "ipucu": "Cumhuriyet dönemi yazarıdır. 'Yaban', 'Kiralık Konak', 'Sodom ve Gomore' gibi romanlarıyla Türk toplumunun geçirdiği değişimleri anlatır."},
        {"cevap": "Halide Edip Adıvar", "ipucu": "Milli Mücadele'nin kadın kahramanıdır. 'Ateşten Gömlek', 'Vurun Kahpeye', 'Sinekli Bakkal' gibi romanlarıyla tanınır."},
        {"cevap": "Reşat Nuri Güntekin", "ipucu": "Anadolu'yu romanlarında en iyi işleyen yazarlardan biridir. 'Çalıkuşu', 'Yaprak Dökümü', 'Yeşil Gece' gibi eserleriyle tanınır."},
        {"cevap": "Orhan Veli Kanık", "ipucu": "Garip akımının kurucusudur. Şiirde kafiye, redif ve ölçüye karşı çıkmıştır. Sıradan insanı anlatır. 'İstanbul'u Dinliyorum' şiiri meşhurdur."},
        {"cevap": "Cemal Süreya", "ipucu": "İkinci Yeni şiirinin en önemli isimlerindendir. 'Üvercinka', 'Sevda Sözleri' gibi eserleri vardır. İroni ve zeka dolu şiirler yazar."},
        {"cevap": "Attila İlhan", "ipucu": "Mavi Hareketi'nin öncüsüdür. 'Ben Sana Mecburum', 'Sisler Bulvarı' gibi şiirleriyle tanınır. Hem şair hem romancıdır."},
        {"cevap": "Necip Fazıl Kısakürek", "ipucu": "Mistisizm ve metafizik konuları işler. 'Kaldırımlar' şairi olarak bilinir. 'Çile' adlı şiir kitabı ve 'Bir Adam Yaratmak' tiyatrosu önemlidir."},
        {"cevap": "Nazım Hikmet", "ipucu": "Serbest nazım ve toplumcu gerçekçi şiirin öncüsüdür. 'Memleketimden İnsan Manzaraları', 'Kuvayi Milliye Destanı' önemli eserleridir."},
        {"cevap": "Ahmet Hamdi Tanpınar", "ipucu": "Zaman, rüya ve bilinçaltı kavramlarını işler. 'Huzur', 'Saatleri Ayarlama Enstitüsü' romanları ve 'Beş Şehir' denemesi başyapıtlarıdır."},
        {"cevap": "Oğuz Atay", "ipucu": "Postmodern Türk romanının öncüsüdür. 'Tutunamayanlar' romanıyla aydın bunalımını ve ironiyi işlemiştir."},
        {"cevap": "Yaşar Kemal", "ipucu": "Çukurova'yı ve efsaneleri anlatır. 'İnce Memed' serisiyle dünya çapında tanınır. Destansı bir anlatımı vardır."},
        {"cevap": "Orhan Pamuk", "ipucu": "Nobel Edebiyat Ödülü alan ilk Türk yazardır. 'Kara Kitap', 'Benim Adım Kırmızı', 'Masumiyet Müzesi' önemli eserleridir."},
        {"cevap": "Sait Faik Abasıyanık", "ipucu": "Durum (Çehov) hikayesinin Türk edebiyatındaki en önemli temsilcisidir. İstanbul'u, adaları ve balıkçıları anlatır. 'Semaver', 'Alemdağ'da Var Bir Yılan' eserleridir."},
        {"cevap": "Sabahattin Ali", "ipucu": "Toplumcu gerçekçi yazarımızdır. 'Kürk Mantolu Madonna', 'Kuyucaklı Yusuf', 'İçimizdeki Şeytan' romanlarıyla tanınır."},
        {"cevap": "Cahit Sıtkı Tarancı", "ipucu": "'Otuz Beş Yaş' şairi olarak bilinir. Ölüm korkusu ve yaşama sevinci şiirlerinin ana temasıdır."},
        {"cevap": "Arif Nihat Asya", "ipucu": "Bayrak şairi olarak bilinir. Milli ve manevi duyguları işleyen şiirler yazmıştır. Rubai türünde de eserleri vardır."}
    ]

@st.cache_data
def get_kavramlar_db():
    return [
        {"kavram": "Tezil", "aciklama": "Ciddi bir şiire (genellikle bir nazireye) alaycı ve mizahi bir dille yazılan karşılık şiiri."},
        {"kavram": "Nazire", "aciklama": "Bir şairin şiirine başka bir şair tarafından aynı ölçü, kafiye ve redifle yazılan benzer şiir."},
        {"kavram": "Tegazzül", "aciklama": "Kasidenin içinde, aynı ölçü ve kafiyede araya sıkıştırılan gazel bölümü."},
        {"kavram": "Fahriye", "aciklama": "Şairin kendi şairliğini, yeteneğini ve sanatını övdüğü bölüm."},
        {"kavram": "Surname", "aciklama": "Şehzadelerin sünnet düğünlerini veya hanım sultanların evlilik törenlerini, şenlikleri anlatan eserler."},
        {"kavram": "Kaside", "aciklama": "Genellikle din ve devlet büyüklerini övmek amacıyla yazılan, belli kuralları olan uzun şiir (33-99 beyit)."},
        {"kavram": "Gazel", "aciklama": "Aşk, şarap, güzellik gibi lirik konuları işleyen, 5-15 beyitlik en yaygın nazım şekli."},
        {"kavram": "Tahmis", "aciklama": "Bir gazelin her beytinin üzerine üçer dize eklenerek beşli hale getirilmesi."},
        {"kavram": "Muhammes", "aciklama": "Beşer dizelik bentlerden oluşan nazım şekli."},
        {"kavram": "Taşdir", "aciklama": "Bir gazelin beyitleri arasına üçer dize eklenerek beşlenmesi."},
        {"kavram": "Kamer (Mah)", "aciklama": "Ay. (Sevgilinin yüzünün parlaklığı ve yuvarlaklığı için kullanılır)."},
        {"kavram": "Bade (Mey)", "aciklama": "Şarap. (Tasavvufta ilahi aşkı veya marifeti temsil eder)."},
        {"kavram": "Selvi (Serv-i hıraman)", "aciklama": "Sevgilinin uzun, düzgün ve salınan boyu."},
        {"kavram": "Saki", "aciklama": "İçki sunan güzel. (Tasavvufta mürşit, yol gösterici)."},
        {"kavram": "Meyhane", "aciklama": "İçki içilen yer. (Tasavvufta tekke, dergah veya aşığın kalbi)."},
        {"kavram": "Rind", "aciklama": "Dünya malına değer vermeyen, şekilcilikten uzak, gönül adamı."},
        {"kavram": "Zahid (Sofu)", "aciklama": "Dinin sadece dış görünüşüne önem veren, kaba, anlayışsız ve aşktan anlamayan kişi."},
        {"kavram": "Rakip (Ağyar)", "aciklama": "Sevgiliye ulaşmaya çalışan diğer kişiler, engelleyenler, düşmanlar."},
        {"kavram": "Hamse", "aciklama": "Bir şairin yazdığı beş mesnevinin oluşturduğu külliyat."},
        {"kavram": "Tevhid", "aciklama": "Allah’ın varlığını ve birliğini anlatan şiirler."},
        {"kavram": "Münacaat", "aciklama": "Allah’a yalvarış, yakarış ve dua konulu şiirler."},
        {"kavram": "Naat", "aciklama": "Hz. Muhammed’i övmek için yazılan şiirler."},
        {"kavram": "Hicviye", "aciklama": "Bir kişiyi, kurumu veya toplumu eleştirmek, yermek için yazılan şiirler."},
        {"kavram": "Mersiye", "aciklama": "Ölen bir kişinin ardından duyulan üzüntüyü anlatan şiirler."},
        {"kavram": "Mesnevi", "aciklama": "Her beyti kendi içinde kafiyeli (aa, bb, cc...), hikaye anlatmaya yarayan uzun nazım şekli."},
        {"kavram": "Rubai", "aciklama": "Tek dörtlükten oluşan, aaba kafiye düzenindeki felsefi şiir."},
        {"kavram": "Tuyuğ", "aciklama": "Türklerin bulduğu, maniye benzeyen tek dörtlükten oluşan nazım şekli."},
        {"kavram": "Murabba", "aciklama": "Dörder dizelik bentlerden oluşan nazım şekli."},
        {"kavram": "Şarkı", "aciklama": "Bestelenmek amacıyla yazılan, nakaratları olan, Murabba’nın bir türü."},
        {"kavram": "Terkib-i Bent", "aciklama": "Bentlerle kurulan, her bendin sonunda kafiyesi değişen 'vasıta beyti' bulunan uzun şiir."},
        {"kavram": "Terci-i Bent", "aciklama": "Vasıta beytinin her bendin sonunda aynen tekrar edildiği, genellikle felsefi ve dini konuları işleyen şiir."},
        {"kavram": "Müstezat", "aciklama": "Gazelin her dizesine 'ziyade' denilen kısa bir dize eklenerek oluşturulan şiir."},
        {"kavram": "Kıta", "aciklama": "Genellikle iki beyitten oluşan, matla beyti olmayan nazım parçası."},
        {"kavram": "Lügaz", "aciklama": "Manzum bilmece. (Genellikle nesneler sorulur)."},
        {"kavram": "Muamma", "aciklama": "Cevabı genelde bir insan ismi veya Allah’ın ismi olan zor manzum bilmece."},
        {"kavram": "Şehrengiz", "aciklama": "Bir şehrin güzelliklerini ve o şehrin güzellerini anlatan eser."},
        {"kavram": "Sakiname", "aciklama": "İçkiyi, içki meclislerini ve adabını anlatan eser."},
        {"kavram": "Gazavatname", "aciklama": "Din uğruna yapılan savaşları ve kahramanlıkları anlatan eser."},
        {"kavram": "Siyer", "aciklama": "Hz. Muhammed’in hayatını anlatan eser."},
        {"kavram": "Hilye", "aciklama": "Hz. Muhammed’in veya dört halifenin fiziksel ve ruhsal özelliklerini anlatan eser."},
        {"kavram": "Pendname", "aciklama": "Öğüt veren, ahlaki didaktik eserler."},
        {"kavram": "Kıyafetname", "aciklama": "İnsanların dış görünüşlerinden karakter tahlili yapan eserler."},
        {"kavram": "Siyasetname", "aciklama": "Devlet yönetimi hakkında bilgi veren eserler."},
        {"kavram": "Bahariye", "aciklama": "Kasidelerin nesib bölümünde bahar mevsiminin tasvir edildiği kısım."},
        {"kavram": "Şitaiye", "aciklama": "Kış mevsiminin tasvir edildiği şiirler."},
        {"kavram": "Iydiye (Bayramiye)", "aciklama": "Bayram günlerini anlatan veya bayramda sunulan şiirler."},
        {"kavram": "Rahşiye", "aciklama": "Atları övmek ve tasvir etmek için yazılan şiirler."},
        {"kavram": "Matla", "aciklama": "Gazel veya kasidenin ilk beyti (aa)."},
        {"kavram": "Makta", "aciklama": "Gazel veya kasidenin son beyti (Şairin mahlası bulunur)."},
        {"kavram": "Beytü'l-Gazel", "aciklama": "Gazelin en güzel beyti."},
        {"kavram": "Taç Beyit", "aciklama": "Kasidede şairin mahlasının geçtiği beyit."},
        {"kavram": "Şah Beyit", "aciklama": "Şiirin en güzel, en dokunaklı beyti."},
        {"kavram": "Yek-ahenk", "aciklama": "Baştan sona aynı konuyu işleyen gazel."},
        {"kavram": "Yek-avaz", "aciklama": "Her beyti aynı söyleyiş güzelliğinde olan gazel."},
        {"kavram": "Musammat Gazel", "aciklama": "Dize ortasında iç kafiyesi olan, bölündüğünde dörtlük olabilen gazel."},
        {"kavram": "Nesib (Teşbib)", "aciklama": "Kasidenin girişindeki tasvir bölümü."},
        {"kavram": "Girizgah", "aciklama": "Kasidede tasvir bölümünden övgü bölümüne geçişi sağlayan beyit."},
        {"kavram": "Methiye", "aciklama": "Kasidenin asıl bölümü, sunulan kişinin övüldüğü kısım."},
        {"kavram": "Dua", "aciklama": "Kasidenin sonunda övülen kişi için iyi dileklerde bulunulan bölüm."},
        {"kavram": "Mahlas", "aciklama": "Şairin şiirlerinde kullandığı takma ad."},
        {"kavram": "Cönk", "aciklama": "Halk şiirlerinin toplandığı sığır dili şeklindeki defter."},
        {"kavram": "Mısra-ı Berceste", "aciklama": "Bir şiirin dillerde dolaşan, atasözü gibi olmuş en meşhur dizesi."},
        {"kavram": "Sebk-i Hindi", "aciklama": "Hint üslubu. Anlam derinliği, kapalı anlatım ve hayal zenginliği olan akım."},
        {"kavram": "Türki-i Basit", "aciklama": "Basit Türkçe akımı. Yabancı kelimelerden arınmış, sade Türkçe ile şiir yazma anlayışı."},
        {"kavram": "Encümen-i Şuara", "aciklama": "Tanzimat öncesi toplanan şairler topluluğu."},
        {"kavram": "Gonca", "aciklama": "Sevgilinin açılmamış, küçük ağzı."},
        {"kavram": "Lal", "aciklama": "Yakut taşı. (Sevgilinin kırmızı dudağı)."},
        {"kavram": "İnci (Dürr/Gevher)", "aciklama": "Sevgilinin dişleri veya şairin sözleri."},
        {"kavram": "Nergis", "aciklama": "Sevgilinin baygın, süzgün veya sarhoş bakan gözü."},
        {"kavram": "Badem (Çeşm-i Badem)", "aciklama": "Sevgilinin göz şekli."},
        {"kavram": "Keman (Yay)", "aciklama": "Sevgilinin kavisli kaşları."},
        {"kavram": "Tir (Ok/Har)", "aciklama": "Sevgilinin kirpikleri (Aşığın kalbine saplanır)."},
        {"kavram": "Gamze", "aciklama": "Sevgilinin yan bakışı, süzgün bakışı (Yaralayıcıdır)."},
        {"kavram": "Yılan (Mar)", "aciklama": "Sevgilinin saçı (Kıvrımlı, uzun ve siyah olması)."},
        {"kavram": "Akrep (Kajdum)", "aciklama": "Sevgilinin saçının ucu veya zülfü."},
        {"kavram": "Zincir", "aciklama": "Sevgilinin saçı (Aşık delidir ve bu zincire bağlanır)."},
        {"kavram": "Hat (Sebze)", "aciklama": "Genç sevgilinin yüzündeki ayva tüyleri."},
        {"kavram": "Ben (Hâl / Felfel)", "aciklama": "Sevgilinin yüzündeki siyah nokta (Genelde tuzağa konan yeme benzetilir)."},
        {"kavram": "Misk / Amber", "aciklama": "Güzel koku. (Sevgilinin saçının veya meclisin kokusu)."},
        {"kavram": "Gül", "aciklama": "Sevgili (Güzelliği, kırmızılığı ve nazlı oluşuyla)."},
        {"kavram": "Bülbül", "aciklama": "Aşık (Güle olan aşkı ve feryat edişiyle)."},
        {"kavram": "Pervane (Kelebek)", "aciklama": "Aşık (Mumun ışığına dönüp sonunda kendini yakmasıyla)."},
        {"kavram": "Şem (Mum)", "aciklama": "Sevgili (Parlaklığı, etrafını aydınlatması ama kendine yaklaşanı yakmasıyla)."},
        {"kavram": "Hüma", "aciklama": "Başına konduğu kişiye iktidar ve mutluluk getiren efsanevi kuş."},
        {"kavram": "Anka (Simurg)", "aciklama": "Kaf Dağı'nda yaşayan, küllerinden doğan efsanevi kuş."},
        {"kavram": "Hüdhüd", "aciklama": "Haberci kuş (Süleyman Peygamber ve Belkıs kıssasında geçer)."},
        {"kavram": "Saba", "aciklama": "Sevgilinin kokusunu aşığa getiren hafif sabah rüzgarı."},
        {"kavram": "Mihr (Afitab / Şems)", "aciklama": "Güneş (Sevgilinin yüzü veya sultan)."},
        {"kavram": "Çark (Felek)", "aciklama": "Gökyüzü, kader (Aşığa hep zulmeder, talihi ters döndürür)."},
        {"kavram": "Kan (Hun)", "aciklama": "Aşığın gözyaşı veya şarap."},
        {"kavram": "Eşk (Sirişk)", "aciklama": "Gözyaşı."},
        {"kavram": "Ah", "aciklama": "Aşığın iç çekişi (Göklere yükselen duman veya ateş)."},
        {"kavram": "Yakup", "aciklama": "Hüzün sembolü (Yusuf'a hasretinden kör olan baba)."},
        {"kavram": "Yusuf", "aciklama": "Güzellik sembolü."},
        {"kavram": "Züleyha", "aciklama": "Aşık kadın sembolü."},
        {"kavram": "Mecnun", "aciklama": "Aşkı uğruna aklını yitirmiş aşık."},
        {"kavram": "Leyla", "aciklama": "Uğruna çöllere düşülen sevgili (Gece, karanlık saçlı)."},
        {"kavram": "Ferhat", "aciklama": "Aşkı için dağları delen aşık."},
        {"kavram": "Hüsrev", "aciklama": "Kudretli hükümdar (Ferhat'ın rakibi)."},
        {"kavram": "Teşbih", "aciklama": "Benzetme sanatı."},
        {"kavram": "İstiare (Eğretileme)", "aciklama": "Bir sözü benzetme amacıyla başka bir söz yerine kullanma."},
        {"kavram": "Mecaz-ı Mürsel", "aciklama": "Benzetme amacı gütmeden bir sözü başka söz yerine kullanma."},
        {"kavram": "Teşhis", "aciklama": "Kişileştirme (İnsan dışı varlıklara insan özelliği verme)."},
        {"kavram": "İntak", "aciklama": "Konuşturma (İnsan dışı varlıkları konuşturma)."},
        {"kavram": "Tenasüp", "aciklama": "Anlamca birbiriyle ilgili kelimeleri bir arada kullanma sanatı."},
        {"kavram": "Telmih", "aciklama": "Herkesçe bilinen bir olaya, kişiye veya kıssaya gönderme yapma."},
        {"kavram": "Hüsn-i Talil", "aciklama": "Güzel nedene bağlama (Gerçek nedenin dışında hayali ve güzel bir neden uydurma)."},
        {"kavram": "Tecahül-i Arif", "aciklama": "Bilip de bilmemezlikten gelme sanatı."},
        {"kavram": "Kinaye", "aciklama": "Bir sözü hem gerçek hem mecaz anlama gelecek şekilde kullanma."},
        {"kavram": "Tevriye", "aciklama": "İki anlamı olan bir sözcüğün yakın anlamını söyleyip uzak anlamını kastetme."},
        {"kavram": "Tariz", "aciklama": "İğneleme, sitem (Söylenilenin tam tersini kastetme)."},
        {"kavram": "Mübalağa", "aciklama": "Abartma sanatı."},
        {"kavram": "Tezat", "aciklama": "Zıt anlamlı kelimeleri veya kavramları bir arada kullanma."},
        {"kavram": "Cinas", "aciklama": "Yazılışları aynı, anlamları farklı kelimeleri bir arada kullanma."},
        {"kavram": "Aliterasyon", "aciklama": "Ünsüz harf tekrarıyla ahenk sağlama."},
        {"kavram": "Asonans", "aciklama": "Ünlü harf tekrarıyla ahenk sağlama."},
        {"kavram": "Seci", "aciklama": "Düz yazıda (nesirde) yapılan kafiye."},
        {"kavram": "İrsal-i Mesel", "aciklama": "Şiirde atasözü veya vecize kullanma."},
        {"kavram": "Leff ü Neşr", "aciklama": "İlk dizede söylenenlerle ilgili kelimeleri ikinci dizede sıralama."},
        {"kavram": "Nida", "aciklama": "Seslenme sanatı (Ey, Hey!)."},
        {"kavram": "İstifham", "aciklama": "Soru sorma sanatı (Cevap beklemeden)."},
        {"kavram": "Aruz", "aciklama": "Hecelerin uzunluk ve kısalığına dayanan nazım ölçüsü."},
        {"kavram": "Vezin", "aciklama": "Ölçü."},
        {"kavram": "Kafiye (Uyak)", "aciklama": "Dize sonlarındaki ses benzerliği."},
        {"kavram": "Redif", "aciklama": "Kafiyeden sonra gelen, aynı görev ve anlamdaki ek veya kelime tekrarı."},
        {"kavram": "Zihaf", "aciklama": "Aruzda uzun heceyi kısa okuma kusuru."},
        {"kavram": "İmale", "aciklama": "Aruzda kısa heceyi uzun okuma (kusur sayılır ama bazen gereklidir)."},
        {"kavram": "Vasl (Ulama)", "aciklama": "Ünsüzle biten kelimeyi ünlüyle başlayan kelimeye bağlama."},
        {"kavram": "Med", "aciklama": "Bir buçuk ses değeri (Uzun heceyi daha da uzatma)."},
        {"kavram": "Takti", "aciklama": "Aruz veznini bulmak için şiiri duraklarına göre ayırma."},
        {"kavram": "Menkıbe", "aciklama": "Din büyüklerinin kerametlerini anlatan hikaye."},
        {"kavram": "Velayetname", "aciklama": "Velilerin hayatını anlatan eser."},
        {"kavram": "Fütüvvetname", "aciklama": "Ahilik teşkilatının kurallarını anlatan eser."},
        {"kavram": "Habname", "aciklama": "Rüya şeklinde anlatılan olaylar veya eleştiriler."},
        {"kavram": "Serazad", "aciklama": "Serbest, özgür (Kayıtsız sevgili veya nazım şekli)."},
        {"kavram": "Müfred (Fert)", "aciklama": "Tek beyitten oluşan, bağımsız şiir."},
        {"kavram": "Azade", "aciklama": "Tek mısralık bağımsız şiir."},
        {"kavram": "Lugaz", "aciklama": "Özellikleri anlatılarak sorulan şey (Bilmece)."},
        {"kavram": "Tardiye", "aciklama": "Muhammesin özel bir kalıbıyla yazılan şekli."},
        {"kavram": "Müseddes", "aciklama": "Altılı bentlerden oluşan nazım şekli."},
        {"kavram": "Müsebba", "aciklama": "Yedili bentlerden oluşan nazım şekli."},
        {"kavram": "Müsemmen", "aciklama": "Sekizli bentlerden oluşan nazım şekli."},
        {"kavram": "Muaşşer", "aciklama": "Onlu bentlerden oluşan nazım şekli."},
        {"kavram": "Mevlid", "aciklama": "Hz. Muhammed’in doğumunu anlatan eser."},
        {"kavram": "Miraciye", "aciklama": "Hz. Muhammed’in miraca yükselişini anlatan eser."},
        {"kavram": "Hicretname", "aciklama": "Hicreti anlatan eser."},
        {"kavram": "Kırk Hadis", "aciklama": "Kırk hadisin tercüme ve şerh edildiği manzum eserler."},
        {"kavram": "Vücudname", "aciklama": "İnsanın yaratılış evrelerini anlatan tasavvufi eser."}
    ]

# --- YENİ SORU ÜRETME ---
def yeni_soru_uret():
    kategori = st.session_state.kategori
    st.session_state.sanat_aciklama = ""
    st.session_state.sema_hoca_kizdi = False
    st.session_state.cevap_verildi = False
    st.session_state.soru_bitti = False
    
    if kategori == "SANATLAR":
        db = get_sanatlar_db()
        soru_data = random.choice(db)
        dogru_cevap = soru_data["sanat"]
        tum_sanatlar = list(set([x["sanat"] for x in db]))
        if dogru_cevap in tum_sanatlar: tum_sanatlar.remove(dogru_cevap)
        yanlis_siklar = random.sample(tum_sanatlar, min(3, len(tum_sanatlar)))
        siklar = yanlis_siklar + [dogru_cevap]
        random.shuffle(siklar)
        return {"tur": "EDEBİ SANAT", "eser": soru_data["beyit"], "dogru_cevap": dogru_cevap, "siklar": siklar, "aciklama": soru_data["aciklama"], "yazar": soru_data.get("yazar")}
    
    elif kategori == "ROMAN_OZET":
        db = get_ozet_db()
        soru_data = random.choice(db)
        dogru_cevap = soru_data["yazar"]
        tum_yazarlar = list(set([x["yazar"] for x in db]))
        if dogru_cevap in tum_yazarlar: tum_yazarlar.remove(dogru_cevap)
        yanlis_siklar = random.sample(tum_yazarlar, min(3, len(tum_yazarlar)))
        siklar = yanlis_siklar + [dogru_cevap]
        random.shuffle(siklar)
        return {"tur": "ROMAN ÖZETİ", "eser": soru_data["ozet"], "dogru_cevap": dogru_cevap, "siklar": siklar, "eser_adi": soru_data["roman"]}
    
    elif kategori == "KAVRAMLAR":
        db = get_kavramlar_db()
        soru_data = random.choice(db)
        dogru_cevap = soru_data["kavram"]
        tum_kavramlar = list(set([x["kavram"] for x in db]))
        if dogru_cevap in tum_kavramlar: tum_kavramlar.remove(dogru_cevap)
        yanlis_siklar = random.sample(tum_kavramlar, min(3, len(tum_kavramlar)))
        siklar = yanlis_siklar + [dogru_cevap]
        random.shuffle(siklar)
        return {"tur": "DİVAN KAVRAMI", "eser": soru_data["aciklama"], "dogru_cevap": dogru_cevap, "siklar": siklar}
        
    elif kategori == "SAIR_TAHMIN": # YENİ MOD
        db = get_sair_tanimi_db()
        soru_data = random.choice(db)
        dogru_cevap = soru_data["cevap"]
        # Yanlış şıkları aynı veritabanından seç
        tum_sairler = list(set([x["cevap"] for x in db]))
        if dogru_cevap in tum_sairler: tum_sairler.remove(dogru_cevap)
        yanlis_siklar = random.sample(tum_sairler, min(3, len(tum_sairler)))
        siklar = yanlis_siklar + [dogru_cevap]
        random.shuffle(siklar)
        return {"tur": "ŞAİR TAHMİN", "eser": soru_data["ipucu"], "dogru_cevap": dogru_cevap, "siklar": siklar}
    
    else:
        db = get_game_db(kategori)
        yazarlar = list(db.keys())
        if not yazarlar: return None 
        secilen_yazar = random.choice(yazarlar)
        turlar = list(db[secilen_yazar].keys())
        secilen_tur = random.choice(turlar)
        eserler = db[secilen_yazar][secilen_tur]
        secilen_eser = random.choice(eserler)
        yanlis_yazarlar = random.sample([y for y in yazarlar if y != secilen_yazar], min(3, len(yazarlar)-1))
        siklar = yanlis_yazarlar + [secilen_yazar]
        random.shuffle(siklar)
        return {"eser": secilen_eser, "tur": secilen_tur, "dogru_cevap": secilen_yazar, "siklar": siklar}

# --- HEADER (BAŞLIK & LOGO & DUYURU) ---
if st.session_state.page == "MENU":
    st.markdown('<div class="creator-name">👑 ALPEREN SÜNGÜ 👑</div>', unsafe_allow_html=True)
    st.write("") 

    col_logo, col_title = st.columns([1, 4]) 
    with col_logo:
        if os.path.exists("background.jpg"):
            with open("background.jpg", "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
            st.markdown(f'<img src="data:image/jpg;base64,{img_data}" width="100%" style="border-radius:15px; border:3px solid #3e7a39;">', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:60px; text-align:center;">📚</div>', unsafe_allow_html=True)
            
    with col_title:
        st.markdown(f"""
        <div style="
            background-color: {card_bg_color}; 
            padding: 20px; 
            border-radius: 15px; 
            border: 3px solid #3e7a39; 
            color: {text_color_cream}; 
            font-weight: 900; 
            font-size: 32px; 
            text-align: center;
            box-shadow: 0 5px 10px rgba(0,0,0,0.3);
            margin-top: 10px;
        ">
            EDEBİYAT LİGİ
        </div>
        """, unsafe_allow_html=True)
    
    # --- YÖNETİCİYE HIZLI MESAJ ---
    with st.expander("📨 Yöneticiye Hızlı Mesaj (Tıkla)", expanded=False):
        with st.form("hizli_mesaj_formu"):
            hizli_mesaj = st.text_input("Mesajınız:", placeholder="Hocam bir sorun var...", label_visibility="collapsed")
            col_h1, col_h2 = st.columns([4, 1])
            with col_h2:
                gonder_btn_hizli = st.form_submit_button("Gönder")
            if gonder_btn_hizli and hizli_mesaj:
                gonderen = st.session_state.kullanici_adi if st.session_state.kullanici_adi else "Misafir"
                mesaj_gonder(gonderen, hizli_mesaj)
                st.success("Mesajınız iletildi! 🚀")

    # --- KOMPAKT DUYURU ALANI ---
    img_tag = ""
    if os.path.exists("odul.jpg"):
        with open("odul.jpg", "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        img_tag = f'<img src="data:image/jpg;base64,{img_b64}" style="height: 120px; border-radius: 10px; border: 2px solid #ffeb3b;">'
    elif os.path.exists("odul.png"):
        with open("odul.png", "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        img_tag = f'<img src="data:image/png;base64,{img_b64}" style="height: 120px; border-radius: 10px; border: 2px solid #ffeb3b;">'
    else:
        img_tag = '<div style="font-size: 40px;">🎁</div>'

    st.markdown(f"""
    <div class='duyuru-wrapper'>
        <div style="flex: 1; color: #fffbe6; font-weight: bold; font-size: 16px; text-align: left;">
            🏆 Haftanın Birincisine <br> 
            <span style="color: #ffeb3b; font-size: 18px;">Limit AYT Edebiyat Cep Kitabı</span> Hediye! 
        </div>
        <div>{img_tag}</div>
    </div>""", unsafe_allow_html=True)
    
    # --- MINI LİDERLİK TABLOSU (TOP 5) ---
    st.markdown("<div style='text-align:center; font-weight:bold; color:#ffeb3b; margin-bottom:5px;'>🏆 Liderlik Tablosu (Top 5) 🏆</div>", unsafe_allow_html=True)
    
    skorlar = skorlari_yukle()
    sirali_skorlar = sorted(skorlar.items(), key=lambda x: x[1]['puan'], reverse=True)[:5] 
    
    if not sirali_skorlar: st.info("Henüz kimse oynamadı. İlk sen ol! 🚀")
    else:
        lider_html = "<div class='mini-leaderboard'>"
        for i, (isim, veri) in enumerate(sirali_skorlar):
            puan = veri['puan']
            aktif_mi = (time.time() - veri['zaman']) < 300 
            durum_ikonu = "🟢" if aktif_mi else ""
            madalya = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            lider_html += f"<div class='leader-item'>{madalya} {isim} {durum_ikonu}<br><span style='color:#ffeb3b;'>{puan} XP</span></div>"
        lider_html += "</div>"
        st.markdown(lider_html, unsafe_allow_html=True)

    # --- ANA EKRAN İSİM GİRME ---
    if not st.session_state.kullanici_adi:
        st.markdown("""<div style="background-color: #1b5e20; padding: 15px; border-radius: 15px; border: 2px solid #ffeb3b; text-align: center; margin-bottom: 20px;"><div style="color: #fffbe6; font-weight: bold; margin-bottom: 10px;">👇 Oyuna Başlamak İçin Adını Yaz 👇</div></div>""", unsafe_allow_html=True)
        st.text_input("Adın Nedir?", label_visibility="collapsed", placeholder="Adınızı buraya yazın...", key="main_isim_input")

    # --- RASTGELE KAVRAM BUTONU ---
    if st.button("🎲 BANA RASTGELE BİR BİLGİ VER!", use_container_width=True):
        kavram_db = get_kavramlar_db()
        st.session_state.rastgele_bilgi = random.choice(kavram_db)
    
    if st.session_state.rastgele_bilgi:
        bilgi = st.session_state.rastgele_bilgi
        st.markdown(f"""<div class="random-info-box"><h3 style="color:#ffeb3b; margin:0;">✨ {bilgi['kavram']} ✨</h3><p style="font-size:18px; margin-top:10px;">{bilgi['aciklama']}</p></div>""", unsafe_allow_html=True)
        if st.button("Kapat"):
            st.session_state.rastgele_bilgi = None
            st.rerun()

    st.markdown("---")
    
    # 3x2 Grid
    c_upper = st.columns(3)
    c_lower = st.columns(3)
    c_bottom = st.columns(3)
    
    # OYUN BAŞLATMA VE İSİM KONTROLÜ
    def start_game(kategori_adi):
        if "main_isim_input" in st.session_state and st.session_state.main_isim_input:
             st.session_state.kullanici_adi = st.session_state.main_isim_input
        if not st.session_state.kullanici_adi: st.session_state.kullanici_adi = "Misafir"
        
        # URL PARAMETRESİNİ GÜNCELLE (BENİ HATIRLA)
        if st.session_state.kullanici_adi != "Misafir":
            st.query_params["oyuncu"] = st.session_state.kullanici_adi
            
        skorlar = skorlari_yukle()
        if st.session_state.kullanici_adi in skorlar: st.session_state.xp = skorlar[st.session_state.kullanici_adi]['puan']
        else: st.session_state.xp = 0
        st.session_state.kategori = kategori_adi
        st.session_state.page = "GAME"
        st.session_state.soru_sayisi = 0
        st.session_state.soru_bitti = False
        st.session_state.mevcut_soru = yeni_soru_uret()
        st.rerun()

    # ÜST SIRA
    with c_upper[0]:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">🇹🇷</div><div class="menu-title">CUMH.</div></div>', unsafe_allow_html=True)
        if st.button("BAŞLA 🇹🇷", key="start_cumh"): start_game("CUMHURİYET")
    with c_upper[1]:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">🎩</div><div class="menu-title">TANZ.</div></div>', unsafe_allow_html=True)
        if st.button("BAŞLA 🎩", key="start_tanz"): start_game("TANZİMAT")
    with c_upper[2]:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">📜</div><div class="menu-title">DİVAN</div></div>', unsafe_allow_html=True)
        if st.button("BAŞLA 📜", key="start_divan"): start_game("DİVAN")
    
    # ALT SIRA
    with c_lower[0]:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">💎</div><div class="menu-title">SERVET</div></div>', unsafe_allow_html=True)
        if st.button("BAŞLA 💎", key="start_servet"): start_game("SERVET-İ FÜNUN")
    with c_lower[1]:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">📖</div><div class="menu-title">ROMAN</div></div>', unsafe_allow_html=True)
        if st.button("BAŞLA 📖", key="start_roman"): start_game("ROMAN_OZET")
    with c_lower[2]:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">🎨</div><div class="menu-title">SANAT</div></div>', unsafe_allow_html=True)
        if st.button("BAŞLA 🎨", key="start_sanat"): start_game("SANATLAR")
        
    # EN ALT SIRA (KAVRAM & HARİTA & YENİ ŞAİR MODU)
    with c_bottom[0]:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">🧠</div><div class="menu-title">KAVRAM</div></div>', unsafe_allow_html=True)
        if st.button("YARIŞ 🧠", key="start_kavram"): start_game("KAVRAMLAR")
    with c_bottom[1]:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">🗺️</div><div class="menu-title">SÖZLÜK</div></div>', unsafe_allow_html=True)
        if st.button("İNCELE 🗺️", key="goto_map"):
            st.session_state.page = "KAVRAM_HARITASI"
            st.rerun()
    # YENİ MOD BUTONU
    with c_bottom[2]:
        st.markdown('<div class="menu-card" style="border-color:#29b6f6;"><div style="font-size:30px;">🕵️‍♂️</div><div class="menu-title" style="color:#29b6f6;">ŞAİR KİM?</div></div>', unsafe_allow_html=True)
        if st.button("TAHMİN ET 🕵️‍♂️", key="start_sair_tahmin"):
            start_game("SAIR_TAHMIN")

    st.markdown("---")
    st.markdown(f"""<div class="menu-card" style="background-color:{card_bg_color}; border-color:#ffeb3b;"><div style="font-size:40px;">🎅🏻 🌨️ 🎄</div><div class="menu-title" style="color:#ffeb3b;">KIŞ OKUMA KÖŞESİ</div><div style="font-size:12px; color:{text_color_cream};">Ansiklopedi & Bilgi</div></div>""", unsafe_allow_html=True)
    if st.button("OKUMA KÖŞESİNE GİR ☕", key="start_study", use_container_width=True):
        st.session_state.page = "STUDY"
        st.rerun()

# --- STUDY SAYFASI ---
elif st.session_state.page == "STUDY":
    st.markdown('<div class="creator-name">👑 ALPEREN SÜNGÜ 👑</div>', unsafe_allow_html=True)
    st.markdown(f"<h1 style='color:#ffeb3b; font-weight:900; text-align:center; background-color:{card_bg_color}; padding:10px; border-radius:15px;'>🎅🏻 OKUMA KÖŞESİ 🎄</h1>", unsafe_allow_html=True)
    
    if st.button("⬅️ ANA MENÜYE DÖN", key="back_to_menu_study"):
        st.session_state.page = "MENU"
        st.rerun()
    db_study = get_reading_db()
    yazar_listesi = sorted(list(db_study.keys()))
    
    cols = st.columns(3)
    for i, yazar in enumerate(yazar_listesi):
        with cols[i % 3]:
            if st.button(f"👤 {yazar}", key=f"author_{i}", use_container_width=True):
                st.session_state.calisma_yazar = yazar
    
    if st.session_state.calisma_yazar:
        yazar = st.session_state.calisma_yazar
        bilgi = db_study[yazar]
        st.markdown("---")
        st.markdown(f"<div class='bio-box'><b>✍️ {yazar}</b><br>{bilgi['bio']}</div>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:{text_color_cream}'>📚 Eserleri ve Önemli Notlar</h4>", unsafe_allow_html=True)
        for eser, ozet in bilgi['eserler'].items():
            with st.expander(f"📖 {eser}"):
                st.markdown(f"<div class='eser-icerik-kutusu'>{ozet}</div>", unsafe_allow_html=True)
        if st.button("LİSTEYİ KAPAT / TEMİZLE", key="clear_study"):
            st.session_state.calisma_yazar = None
            st.rerun()

# --- KAVRAM HARİTASI SAYFASI ---
elif st.session_state.page == "KAVRAM_HARITASI":
    st.markdown('<div class="creator-name">👑 ALPEREN SÜNGÜ 👑</div>', unsafe_allow_html=True)
    st.markdown(f"<h1 style='color:#ffeb3b; font-weight:900; text-align:center; background-color:{card_bg_color}; padding:10px; border-radius:15px;'>🗺️ KAVRAM SÖZLÜĞÜ</h1>", unsafe_allow_html=True)
    
    if st.button("⬅️ ANA MENÜYE DÖN", key="back_to_menu_map"):
        st.session_state.page = "MENU"
        st.rerun()
    
    arama = st.text_input("Kavram Ara:", placeholder="Örn: Gazel, Teşbih...")
    kavramlar = get_kavramlar_db()
    kavramlar = sorted(kavramlar, key=lambda x: x['kavram'])
    
    found = False
    for k in kavramlar:
        if arama.lower() in k['kavram'].lower() or arama.lower() in k['aciklama'].lower():
            found = True
            with st.expander(f"📌 {k['kavram']}"):
                st.markdown(f"<div class='kavram-box'>{k['aciklama']}</div>", unsafe_allow_html=True)
    if not found and arama: st.warning("Aradığınız kavram bulunamadı.")


# --- GAME SAYFASI ---
elif st.session_state.page == "GAME":
    st.markdown('<div class="creator-name">👑 ALPEREN SÜNGÜ 👑</div>', unsafe_allow_html=True)
    
    # SENKRONİZASYON
    kayitli_skorlar = skorlari_yukle()
    if st.session_state.kullanici_adi in kayitli_skorlar:
         st.session_state.xp = kayitli_skorlar[st.session_state.kullanici_adi]["puan"]

    soru = st.session_state.mevcut_soru
    
    if st.session_state.sema_hoca_kizdi:
        st.markdown('<div class="sema-hoca-fixed-wrapper">', unsafe_allow_html=True)
        st.markdown("""<div class="sema-hoca-alert-box-body"><div style="font-size: 60px;">😡</div><div style="font-weight:900; font-size: 30px;">SEMA HOCAN<br>ÇOK KIZDI!</div><div style="font-size:20px; color:#ffeaa7; margin-top:10px;">Nasıl Bilemezsin?!</div>""", unsafe_allow_html=True)
        if st.button("Özür Dilerim 😔", key="btn_sorry"):
            skoru_guncelle_ve_kaydet(st.session_state.kullanici_adi, 0)
            if st.session_state.kategori == "SANATLAR":
                st.session_state.sema_hoca_kizdi = False
                st.rerun()
            else:
                st.session_state.soru_sayisi += 1
                st.session_state.soru_bitti = False
                st.session_state.cevap_verildi = False
                st.session_state.sema_hoca_kizdi = False
                st.session_state.mevcut_soru = yeni_soru_uret()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True) 
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    if soru is None:
        st.error("Veritabanı hatası. Lütfen menüye dön.")
        if st.button("Menü", key="error_menu_btn"):
            st.session_state.page = "MENU"
            st.rerun()
        st.stop()

    level = (st.session_state.soru_sayisi // 5) + 1
    st.markdown(f"<div class='mobile-score'><span style='color:{text_color_cream};'>⭐ Lv {level}</span><span style='color:#aed581;'>💎 {st.session_state.xp} XP</span></div>", unsafe_allow_html=True)
    st.progress((st.session_state.soru_sayisi % 5) * 20)
    
    # SORU BAŞLIĞI VE İÇERİK AYARLARI
    if st.session_state.kategori == "SANATLAR":
        title_text = "BU HANGİ EDEBİ SANAT?"
        content_text = f'"{soru["eser"]}"'
        sub_text = "Dizelerdeki sanatı bul!"
        konu_basligi = soru['dogru_cevap']
    elif st.session_state.kategori == "ROMAN_OZET":
        title_text = "BU ROMANIN YAZARI KİM?"
        content_text = soru["eser"]
        sub_text = "Özeti dikkatli oku!"
        konu_basligi = soru['dogru_cevap']
    elif st.session_state.kategori == "KAVRAMLAR":
        title_text = "BU KAVRAM NEDİR?"
        content_text = soru["eser"]
        sub_text = "Tanımı verilen terimi bul!"
        konu_basligi = soru['dogru_cevap']
    elif st.session_state.kategori == "SAIR_TAHMIN": # YENİ
        title_text = "KİM BU ŞAİR?"
        content_text = soru["eser"]
        sub_text = "Özellikleri verilen şairi bul!"
        konu_basligi = soru['dogru_cevap']
    else:
        title_text = f"TÜR: {soru['tur']}"
        content_text = f"✨ {soru['eser']} ✨"
        sub_text = "Kime aittir?"
        konu_basligi = soru['dogru_cevap']
        
    st.markdown(f"""<div class="question-card"><div style="color:{text_color_cream}; font-weight:bold; font-size:16px;">{title_text}</div><div style="font-size:22px; font-weight:900; color:#ffeb3b; margin: 15px 0; padding:10px; background:#3e7a39; border-radius:10px;">{content_text}</div><div style="font-size:18px; font-weight:bold; color:{text_color_cream};">{sub_text}</div></div>""", unsafe_allow_html=True)

    if st.session_state.kategori == "SANATLAR" and soru.get("yazar"):
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="
                background-color: #2e5a27;
                color: #fffbe6;
                padding: 8px 15px;
                border-radius: 10px;
                font-weight: 900;
                font-size: 18px;
                text-align: center;
                margin-top: 10px;
                margin-bottom: 10px;
                border: 2px solid #ffeb3b;
                box-shadow: 0 4px 8px rgba(0,0,0,0.5);
                display: inline-block;
            ">
                ✍️ Şair: {soru['yazar']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        cevap = st.radio("Seçim:", soru['siklar'], label_visibility="collapsed", disabled=st.session_state.soru_bitti)
    with col2:
        st.write("") 
        st.write("")
        if not st.session_state.soru_bitti:
            if st.button("YANITLA 🚀", key="btn_answer", type="primary", use_container_width=True):
                st.session_state.cevap_verildi = True
                
                # --- YANIT KONTROLÜ VE LOGLAMA ---
                is_correct = (cevap == soru['dogru_cevap'])
                
                # Detaylı Rapor Kaydı
                rapor_kaydet(
                    st.session_state.kullanici_adi, 
                    content_text, 
                    cevap, 
                    is_correct, 
                    soru['dogru_cevap'],
                    st.session_state.kategori,
                    konu_basligi
                )

                if is_correct:
                    # Puan kazanma (Söz sanatları dahil her yerde)
                    yeni_puan = skoru_guncelle_ve_kaydet(st.session_state.kullanici_adi, 100)
                    st.session_state.xp = yeni_puan
                    st.markdown(get_audio_html("dogru"), unsafe_allow_html=True)
                    st.success("MÜKEMMEL! +100 XP 🎯")
                    st.balloons()
                    
                    if st.session_state.kategori == "ROMAN_OZET" and "eser_adi" in soru: st.info(f"✅ Romanın Adı: **{soru['eser_adi']}**")
                    
                    if st.session_state.kategori == "SANATLAR":
                        if "aciklama" in soru: st.markdown(f"""<div class="sanat-aciklama"><b>💡 HOCA NOTU:</b><br>{soru['aciklama']}</div>""", unsafe_allow_html=True)
                        st.session_state.soru_bitti = True
                        st.rerun()
                    elif st.session_state.kategori == "SAIR_TAHMIN": # Şair Tahmin'de direkt geçebilir
                        time.sleep(1.5)
                        st.session_state.soru_sayisi += 1
                        st.session_state.soru_bitti = False
                        st.session_state.cevap_verildi = False
                        st.session_state.mevcut_soru = yeni_soru_uret()
                        st.rerun()
                    else:
                        time.sleep(1.5)
                        st.session_state.soru_sayisi += 1
                        st.session_state.soru_bitti = False
                        st.session_state.cevap_verildi = False
                        st.session_state.mevcut_soru = yeni_soru_uret()
                        st.rerun()
                else: 
                    st.markdown(get_audio_html("yanlis"), unsafe_allow_html=True)
                    st.session_state.sema_hoca_kizdi = True
                    st.error(f"YANLIŞ! Doğru: {soru['dogru_cevap']}")
                    yeni_puan = skoru_guncelle_ve_kaydet(st.session_state.kullanici_adi, -20)
                    st.session_state.xp = yeni_puan
                    st.rerun()
        
        elif st.session_state.soru_bitti and not st.session_state.sema_hoca_kizdi:
            if "aciklama" in soru: st.markdown(f"""<div class="sanat-aciklama"><b>💡 HOCA NOTU:</b><br>{soru['aciklama']}</div>""", unsafe_allow_html=True)
            if st.button("GEÇ ➡️", key="btn_next", type="primary", use_container_width=True):
                st.session_state.soru_sayisi += 1
                st.session_state.soru_bitti = False
                st.session_state.cevap_verildi = False
                st.session_state.mevcut_soru = yeni_soru_uret()
                st.rerun()