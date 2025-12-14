import streamlit as st
import random
import time
import os
import base64

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Edebiyat Ligi",
    page_icon="📚",
    layout="centered"
)

# GOOGLE FORM LİNKİ
GOOGLE_FORM_LINKI = "https://docs.google.com/forms/d/e/1FAIpQLSd6x_NxAj58m8-5HAKpm6R6pmTvJ64zD-TETIPxF-wul5Muwg/viewform?usp=header"

# --- ARKA PLAN VE SES FONKSİYONLARI ---
def get_audio_html(sound_type):
    if sound_type == "dogru":
        audio_url = "https://cdn.pixabay.com/audio/2021/08/04/audio_bb630cc098.mp3"
    else:
        audio_url = "https://cdn.pixabay.com/audio/2021/08/04/audio_88447e769f.mp3"
    return f"""<audio autoplay="true" style="display:none;"><source src="{audio_url}" type="audio/mp3"></audio>"""

# ======================================================
# 1. VERİTABANLARI
# ======================================================
@st.cache_data
def get_game_db(kategori):
    if kategori == "CUMHURİYET":
        return {
            "Ömer Seyfettin": {"Hikaye": ["Kaşağı", "Ant", "Falaka", "Pembe İncili Kaftan", "Bomba", "Yüksek Ökçeler", "Gizli Mabed"], "Roman": ["Efruz Bey"]},
            "Ziya Gökalp": {"Şiir": ["Kızıl Elma", "Altın Işık", "Yeni Hayat"], "Fikir": ["Türkçülüğün Esasları"]},
            "Yakup Kadri Karaosmanoğlu": {"Roman": ["Yaban", "Kiralık Konak", "Sodom ve Gomore", "Nur Baba", "Ankara", "Panorama"], "Anı": ["Zoraki Diplomat"]},
            "Halide Edip Adıvar": {"Roman": ["Sinekli Bakkal", "Ateşten Gömlek", "Vurun Kahpeye", "Handan", "Tatarcık"], "Anı": ["Mor Salkımlı Ev"]},
            "Reşat Nuri Güntekin": {"Roman": ["Çalıkuşu", "Yaprak Dökümü", "Yeşil Gece", "Acımak", "Miskinler Tekkesi"]},
            "Peyami Safa": {"Roman": ["Dokuzuncu Hariciye Koğuşu", "Fatih-Harbiye", "Yalnızız", "Matmazel Noraliya'nın Koltuğu"]},
            "Tarık Buğra": {"Roman": ["Küçük Ağa", "Osmancık", "İbişin Rüyası", "Firavun İmanı"]},
            "Sait Faik Abasıyanık": {"Hikaye": ["Semaver", "Sarnıç", "Lüzumsuz Adam", "Son Kuşlar", "Alemdağ'da Var Bir Yılan"]},
            "Sabahattin Ali": {"Roman": ["Kürk Mantolu Madonna", "Kuyucaklı Yusuf", "İçimizdeki Şeytan"], "Hikaye": ["Değirmen", "Kağnı"]},
            "Ahmet Hamdi Tanpınar": {"Roman": ["Huzur", "Saatleri Ayarlama Enstitüsü", "Sahnenin Dışındakiler"], "Deneme": ["Beş Şehir"]},
            "Necip Fazıl Kısakürek": {"Şiir": ["Çile", "Kaldırımlar", "Örümcek Ağı"], "Tiyatro": ["Bir Adam Yaratmak", "Reis Bey"]},
            "Nazım Hikmet": {"Şiir": ["Memleketimden İnsan Manzaraları", "Kuvayi Milliye Destanı", "Simavne Kadısı Oğlu Bedreddin"]},
            "Yaşar Kemal": {"Roman": ["İnce Memed", "Yer Demir Gök Bakır", "Ağrı Dağı Efsanesi"]},
            "Orhan Pamuk": {"Roman": ["Kara Kitap", "Benim Adım Kırmızı", "Masumiyet Müzesi", "Cevdet Bey ve Oğulları"]},
            "Oğuz Atay": {"Roman": ["Tutunamayanlar", "Tehlikeli Oyunlar", "Bir Bilim Adamının Romanı"], "Hikaye": ["Korkuyu Beklerken"]},
            "Attila İlhan": {"Şiir": ["Ben Sana Mecburum", "Sisler Bulvarı", "Duvar"], "Roman": ["Kurtlar Sofrası"]},
            "Cemal Süreya": {"Şiir": ["Üvercinka", "Sevda Sözleri", "Göçebe"]},
            "Adalet Ağaoğlu": {"Roman": ["Ölmeye Yatmak", "Bir Düğün Gecesi", "Fikrimin İnce Gülü"]},
            "Orhan Kemal": {"Roman": ["Bereketli Topraklar Üzerinde", "Murtaza", "Eskici ve Oğulları", "Hanımın Çiftliği"]},
            "Kemal Tahir": {"Roman": ["Devlet Ana", "Yorgun Savaşçı", "Esir Şehrin İnsanları"]},
            "Refik Halit Karay": {"Hikaye": ["Memleket Hikayeleri", "Gurbet Hikayeleri"], "Roman": ["Sürgün", "Bugünün Saraylısı"]},
            "Mehmet Akif Ersoy": {"Şiir": ["Safahat"]},
            "Yahya Kemal Beyatlı": {"Şiir": ["Kendi Gök Kubbemiz", "Eski Şiirin Rüzgarıyla"], "Nesir": ["Aziz İstanbul"]},
            "Faruk Nafiz Çamlıbel": {"Şiir": ["Han Duvarları", "Çoban Çeşmesi"], "Tiyatro": ["Akın", "Canavar"]},
            "Memduh Şevket Esendal": {"Roman": ["Ayaşlı ve Kiracıları"], "Hikaye": ["Otlakçı", "Mendil Altında"]},
            "Orhan Veli Kanık": {"Şiir": ["Garip", "Vazgeçemediğim", "Destan Gibi"]},
            "Cahit Sıtkı Tarancı": {"Şiir": ["Otuz Beş Yaş", "Düşten Güzel"]},
            "Ahmet Muhip Dıranas": {"Şiir": ["Fahriye Abla", "Serenad", "Olvido"]},
            "Ziya Osman Saba": {"Şiir": ["Sebil ve Güvercinler", "Geçen Zaman"], "Hikaye": ["Mesut İnsanlar Fotoğrafhanesi"]},
            "Arif Damar": {"Şiir": ["Günden Güne", "İstanbul Bulutu"]},
            "Ferit Edgü": {"Roman": ["Hakkari'de Bir Mevsim (O)"], "Hikaye": ["Bir Gemide", "Çığlık"]},
            "Enis Behiç Koryürek": {"Şiir": ["Miras", "Güneşin Ölümü"], "Destan": ["Gemiciler"]},
            "Behçet Necatigil": {"Şiir": ["Kapalı Çarşı", "Evler"]},
            "Hilmi Yavuz": {"Şiir": ["Bakış Kuşu", "Doğu Şiirleri"]},
            "Cahit Külebi": {"Şiir": ["Adamın Biri", "Rüzgar", "Atatürk Kurtuluş Savaşı'nda"]},
            "Fazıl Hüsnü Dağlarca": {"Şiir": ["Havaya Çizilen Dünya", "Çocuk ve Allah", "Üç Şehitler Destanı"]},
            "Salah Birsel": {"Deneme": ["Kahveler Kitabı", "Ah Beyoğlu Vah Beyoğlu"], "Şiir": ["Dünya İşleri"]},
            "Oktay Rifat": {"Şiir": ["Perçemli Sokak", "Karga ile Tilki"]},
            "Melih Cevdet Anday": {"Şiir": ["Rahatı Kaçan Ağaç", "Kolları Bağlı Odysseus"]},
            "Yusuf Atılgan": {"Roman": ["Aylak Adam", "Anayurt Oteli"]},
            "Haldun Taner": {"Tiyatro": ["Keşanlı Ali Destanı"], "Hikaye": ["Şişhaneye Yağmur Yağıyordu"]},
            "Sezai Karakoç": {"Şiir": ["Monna Rosa", "Körfez", "Hızırla Kırk Saat"]},
            "Turgut Uyar": {"Şiir": ["Göğe Bakma Durağı", "Dünyanın En Güzel Arabistanı"]},
            "Edip Cansever": {"Şiir": ["Yerçekimli Karanfil", "Masa Da Masaymış"]},
            "Ece Ayhan": {"Şiir": ["Bakışsız Bir Kedi Kara", "Yort Savul"]},
            "Falih Rıfkı Atay": {"Anı": ["Çankaya", "Zeytindağı"]},
            "Nurullah Ataç": {"Deneme": ["Günlerin Getirdiği", "Karalama Defteri"]},
            "Ahmet Kutsi Tecer": {"Şiir": ["Orada Bir Köy Var Uzakta"], "Tiyatro": ["Koçyiğit Köroğlu"]},
            "Fakir Baykurt": {"Roman": ["Yılanların Öcü", "Kaplumbağalar"]},
            "Latife Tekin": {"Roman": ["Sevgili Arsız Ölüm"]}
        }
    else: # DİVAN
        return {
            "Fuzuli": {"Mesnevi": ["Leyla ile Mecnun", "Bengü Bade"], "Nesir": ["Şikayetname"]},
            "Baki": {"Şiir": ["Kanuni Mersiyesi", "Baki Divanı"], "Nesir": ["Fezail-i Mekke"]},
            "Nefi": {"Hiciv": ["Siham-ı Kaza"]},
            "Nabi": {"Mesnevi": ["Hayriye", "Hayrabad"], "Gezi": ["Tuhfetü'l Haremeyn"]},
            "Şeyh Galip": {"Mesnevi": ["Hüsnü Aşk"]},
            "Şeyhi": {"Fabl": ["Harname"], "Mesnevi": ["Hüsrev ü Şirin"]},
            "Katip Çelebi": {"Bibliyografya": ["Keşfü'z Zunun"], "Coğrafya": ["Cihannüma"]},
            "Evliya Çelebi": {"Gezi": ["Seyahatname"]},
            "Ali Şir Nevai": {"Sözlük": ["Muhakemetü'l Lügateyn"], "Tezkire": ["Mecalisü'n Nefais"]},
            "Sinan Paşa": {"Süslü Nesir": ["Tazarruname"]},
            "Mercimek Ahmet": {"Sade Nesir": ["Kabusname"]},
            "Süleyman Çelebi": {"Mesnevi": ["Vesiletü'n Necat (Mevlid)"]},
            "Ahmedi": {"Mesnevi": ["İskendername"]},
            "Babürşah": {"Anı": ["Babürname"]},
            "Seydi Ali Reis": {"Gezi": ["Mir'atü'l Memalik"]},
            "Yirmisekiz Çelebi Mehmet": {"Sefaretname": ["Paris Sefaretnamesi"]},
            "Gülşehri": {"Mesnevi": ["Mantıku't Tayr"]},
            "Kaygusuz Abdal": {"Nesir": ["Budalaname"]},
            "Aşık Paşa": {"Mesnevi": ["Garibname"]},
            "Hoca Dehhani": {"Destan": ["Selçuklu Şehnamesi"]},
            "Kadı Burhaneddin": {"Şiir": ["Tuyuğlar"]},
            "Nedim": {"Şiir": ["Şarkı Formu"]},
            "Nergisi": {"Nesir": ["Nergisi Hamsesi"]}
        }

@st.cache_data
def get_ozet_db():
    return [
        {"yazar": "Namık Kemal", "roman": "İntibah", "ozet": "Ali Bey, mirasyedi bir gençtir. Mahpeyker adlı hafif meşrep bir kadına aşık olur. Dilaşub adlı cariye ile Mahpeyker arasında kalır."},
        {"yazar": "Recaizade Mahmut Ekrem", "roman": "Araba Sevdası", "ozet": "Bihruz Bey, alafrangalık özentisi, mirasyedi bir gençtir. Periveş adlı kadını soylu sanır. Yanlış batılılaşma mizahi dille anlatılır."},
        {"yazar": "Halit Ziya Uşaklıgil", "roman": "Mai ve Siyah", "ozet": "Ahmet Cemil'in şair olma hayalleri (Mai) ile hayatın acı gerçekleri (Siyah) arasındaki çatışma anlatılır."},
        {"yazar": "Halit Ziya Uşaklıgil", "roman": "Aşk-ı Memnu", "ozet": "Bihter, Adnan Bey ile evlenir ancak Behlül ile yasak aşk yaşar. Firdevs Hanım ve Nihal diğer karakterlerdir."},
        {"yazar": "Mehmet Rauf", "roman": "Eylül", "ozet": "Suat, Süreyya ve Necip arasındaki yasak aşkı anlatan ilk psikolojik romandır."},
        {"yazar": "Yakup Kadri Karaosmanoğlu", "roman": "Yaban", "ozet": "Ahmet Celal, bir Anadolu köyüne yerleşir. Köylü-aydın çatışması işlenir."},
        {"yazar": "Reşat Nuri Güntekin", "roman": "Çalıkuşu", "ozet": "Feride, Kamran'a küsüp Anadolu'da öğretmenlik yapar."},
        {"yazar": "Peyami Safa", "roman": "Dokuzuncu Hariciye Koğuşu", "ozet": "Hasta bir çocuğun bacağındaki kemik veremi ve Nüzhet'e olan aşkı."},
        {"yazar": "Ahmet Hamdi Tanpınar", "roman": "Saatleri Ayarlama Enstitüsü", "ozet": "Hayri İrdal ve Halit Ayarcı üzerinden Türk toplumunun modernleşme ironisi anlatılır."},
        {"yazar": "Oğuz Atay", "roman": "Tutunamayanlar", "ozet": "Turgut Özben, intihar eden arkadaşı Selim Işık'ın izini sürer. Küçük burjuva aydınının dramı."},
        {"yazar": "Orhan Pamuk", "roman": "Kara Kitap", "ozet": "Galip, kayıp karısı Rüya'yı ve Celal'i İstanbul sokaklarında arar."},
        {"yazar": "Yaşar Kemal", "roman": "İnce Memed", "ozet": "Abdi Ağa'nın zulmüne başkaldıran Memed'in eşkıya oluşu."},
        {"yazar": "Sabahattin Ali", "roman": "Kürk Mantolu Madonna", "ozet": "Raif Efendi'nin Almanya'da Maria Puder ile yaşadığı hüzünlü aşk."},
        {"yazar": "Yusuf Atılgan", "roman": "Anayurt Oteli", "ozet": "Otel katibi Zebercet'in yalnızlığı ve psikolojik çöküşü."},
        {"yazar": "Adalet Ağaoğlu", "roman": "Ölmeye Yatmak", "ozet": "Aysel'in bir otel odasında intiharı düşünürken geçmişiyle hesaplaşması."},
        {"yazar": "Ferit Edgü", "roman": "Hakkari'de Bir Mevsim", "ozet": "Bir öğretmenin Hakkari'nin Pirkanis köyündeki yalnızlığı ve köylülerle iletişimi (O adlı roman)."}
    ]

@st.cache_data
def get_sanatlar_db():
    return [
        {"sanat": "Teşbih (Benzetme)", "beyit": "Cennet gibi güzel vatanım...", "aciklama": "Burada vatan (benzeyen), cennete (benzetilen) benzetilmiştir. 'Gibi' edatı kullanılmıştır."},
        {"sanat": "İstiare (Eğretileme)", "beyit": "Şakaklarıma kar mı yağdı ne var?", "aciklama": "Burada beyaz saç (benzeyen) söylenmemiş, sadece 'kar' (benzetilen) söylenerek İstiare yapılmıştır."},
        {"sanat": "Tezat (Zıtlık)", "beyit": "Ağlarım hatıra geldikçe gülüştüklerimiz.", "aciklama": "'Ağlamak' ve 'Gülüşmek' zıt anlamlı kelimeler bir arada kullanılmıştır."},
        {"sanat": "Hüsnü Talil (Güzel Neden)", "beyit": "Güzel şeyler düşünelim diye / Yemyeşil oluvermiş ağaçlar", "aciklama": "Ağaçların yeşermesi doğal bir olaydır ama şair bunu 'biz güzel düşünelim diye' diyerek güzel bir nedene bağlamıştır."},
        {"sanat": "Telmih (Hatırlatma)", "beyit": "Gökyüzünde İsa ile, Tur dağında Musa ile...", "aciklama": "Hz. İsa ve Hz. Musa peygamberlere ait olaylar hatırlatılmıştır."},
        {"sanat": "Tecahülü Arif (Bilmezlik)", "beyit": "Göz gördü gönül sevdi seni ey yüzü mahım / Kurbanın olam var mı benim bunda günahım?", "aciklama": "Şair aşık olduğunu bildiği halde, 'günahım var mı' diye sorarak bilmezlikten geliyor."},
        {"sanat": "Mübalağa (Abartma)", "beyit": "Bir ah çeksem dağı taşı eritir / Gözüm yaşı değirmeni yürütür", "aciklama": "Gözyaşıyla değirmen yürütmek imkansız bir abartıdır."},
        {"sanat": "İntak (Konuşturma)", "beyit": "Ben ki toz kanatlı bir kelebeğim / Minicik gövdeme yüklü Kafdağı", "aciklama": "Kelebek insan gibi konuşturulmuştur."},
        {"sanat": "Tevriye (İki Anlamlılık)", "beyit": "Bu kadar letafet çünkü sende var / Beyaz gerdanında bir de ben gerek", "aciklama": "'Ben' kelimesi hem vücuttaki siyah nokta hem de 1. tekil şahıs (kendisi) olarak iki anlama gelecek şekilde kullanılmıştır."},
        {"sanat": "İrsal-i Mesel", "beyit": "Balık baştan kokar bunu bilmemek / Seyrani gafilin ahmaklığıdır", "aciklama": "'Balık baştan kokar' atasözü şiirde kullanılmıştır."},
        {"sanat": "Teşhis (Kişileştirme)", "beyit": "Haliç'te bir vapuru vurdular dört kişi / Demirlemişti eli kolu bağlıydı ağlıyordu", "aciklama": "Vapura insani özellikler (eli kolu bağlı olmak, ağlamak) verilmiştir."}
    ]

@st.cache_data
def get_reading_db():
    return {
        "Orhan Veli Kanık": {
            "bio": "Garip akımının kurucusudur. 'Sokağı şiire taşıyan adam'dır.",
            "eserler": {
                "İstanbul'u Dinliyorum": "Şairin İstanbul'a olan aşkını sesler ve imgelerle anlattığı şiir.",
                "Kitabe-i Seng-i Mezar": "Sıradan bir insan olan Süleyman Efendi'yi anlatan şiir."
            }
        },
        "Ahmet Hamdi Tanpınar": {
            "bio": "Rüya, Zaman ve Bilinçaltı kavramlarını işler. Şiirde sembolisttir.",
            "eserler": {
                "Huzur": "Mümtaz ve Nuran aşkı üzerinden Doğu-Batı çatışması.",
                "Beş Şehir": "Ankara, Erzurum, Konya, Bursa ve İstanbul üzerine denemeler."
            }
        },
        "Ferit Edgü": {"bio": "Küçürek öykü ustası. Hakkari'de öğretmenlik yaparken yaşadıklarını yazar.", "eserler": {"Hakkari'de Bir Mevsim": "Yabancılaşma ve yalnızlık."}},
        "Ziya Osman Saba": {"bio": "Yedi Meşaleciler'in şairi. Ev ve küçük mutlulukları işler.", "eserler": {"Sebil ve Güvercinler": "Huzur ve ahiret özlemi."}},
        "Arif Damar": {"bio": "Toplumcu gerçekçi şair.", "eserler": {"Günden Güne": "Toplumsal umut."}},
        "Enis Behiç Koryürek": {"bio": "Beş Hececilerdendir. Deniz şiirleriyle tanınır.", "eserler": {"Gemiciler": "Türk denizciliği."}},
        "Ahmet Muhip Dıranas": {"bio": "Saf şiir ve sembolizm.", "eserler": {"Fahriye Abla": "Efsaneleşmiş lirik şiir."}},
        "Cahit Sıtkı Tarancı": {"bio": "Ölüm, yaşama sevinci ve yalnızlık. 'Otuz Beş Yaş' şairidir.", "eserler": {"Otuz Beş Yaş": "Ölüm korkusu."}},
        "Behçet Necatigil": {"bio": "Evler Şairi. Modern insanın yalnızlığı.", "eserler": {"Kapalı Çarşı": "Şehir ve insan."}},
        "Fazıl Hüsnü Dağlarca": {"bio": "'Türkçem benim ses bayrağım' der. Destan şairidir.", "eserler": {"Üç Şehitler Destanı": "Kurtuluş Savaşı."}},
        "Peyami Safa": {"bio": "Psikolojik romanın güçlü kalemi.", "eserler": {"Fatih-Harbiye": "Doğu-Batı çatışması."}},
        "Tarık Buğra": {"bio": "Tarihi ve psikolojik derinlikli romanlar.", "eserler": {"Küçük Ağa": "Kuvayi Milliye bilinci."}},
    }

# --- SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "MENU"
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
if 'sema_hoca_kizdi' not in st.session_state:
    st.session_state.sema_hoca_kizdi = False
if 'sanat_aciklama' not in st.session_state:
    st.session_state.sanat_aciklama = ""
if 'calisma_yazar' not in st.session_state:
    st.session_state.calisma_yazar = None
if 'soru_bitti' not in st.session_state:
    st.session_state.soru_bitti = False

# --- CSS TASARIMI (YEŞİL SARMAŞIKLI KİTAP GÖRSELİNE UYGUN) ---
# Resim URL'si (Senin beğendiğin tarzın çok benzeri, güvenilir bir kaynak)
# VEYA sen 'background.jpg' olarak kendi dosyanı yüklersen onu kullanır.
if os.path.exists("background.jpg"):
    with open("background.jpg", "rb") as f:
        img_data = base64.b64encode(f.read()).decode()
    bg_image_css = f"background-image: url('data:image/jpg;base64,{img_data}');"
else:
    # Eğer background.jpg yoksa, senin görseline çok benzeyen yüksek kaliteli bir online alternatif
    bg_image_css = "background-image: url('https://img.freepik.com/free-vector/hand-drawn-library-pattern_23-2149429596.jpg?w=2000');"

# YAN MENÜ RENGİ (Görseldeki yeşil tonlarına uygun koyu haki/zeytin yeşili)
sidebar_color = "#33691e" 

st.markdown(f"""
    <style>
    /* ARKA PLAN AYARLARI */
    .stApp {{
        {bg_image_css}
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    html, body, p, div, label, h1, h2, h3, h4, h5, h6, li, span, b, i {{
        font-family: 'Segoe UI', sans-serif;
    }}
    
    /* YAN MENÜ (İSTATİSTİKLER) */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_color} !important;
        border-right: 4px solid #aed581;
    }}
    /* Yan menüdeki TÜM yazılar BEYAZ olsun */
    [data-testid="stSidebar"] * {{
        color: #ffffff !important;
    }}
    
    /* SORU KARTI VE ŞIKLAR (OKUNABİLİRLİK İÇİN YARI SAYDAM ZEMİN) */
    
    /* Soru Kartı */
    .question-card {{
        background-color: rgba(255, 255, 255, 0.95) !important; /* %95 Beyaz */
        padding: 25px;
        border-radius: 20px;
        border: 4px solid #33691e; /* Koyu yeşil çerçeve */
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        text-align: center;
        margin-bottom: 25px;
    }}
    /* Soru kartı içindeki yazılar SİMSİYAH */
    .question-card div, .question-card span, .question-card p {{
        color: #000000 !important;
    }}
    
    /* Şık Kutuları (Radio) */
    .stRadio {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        padding: 20px;
        border-radius: 20px;
        border: 3px solid #33691e;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }}
    /* Şık yazıları SİMSİYAH */
    .stRadio label p {{
        color: #000000 !important;
        font-size: 18px !important;
        font-weight: 700 !important;
    }}
    
    /* Menü Kartları */
    .menu-card {{ 
        background-color: rgba(255, 255, 255, 0.95); 
        padding: 20px; 
        border-radius: 20px; 
        text-align: center; 
        border: 4px solid #33691e; 
        cursor: pointer; 
        margin-bottom: 15px; 
        box-shadow: 0 6px 0px #1b5e20; 
    }}
    .menu-title {{ 
        font-size: 18px; 
        font-weight: 900; 
        color: #33691e; 
        text-transform: uppercase; 
    }}
    
    /* BUTONLAR (Kiremit Rengi - Yeşil ile Kontrast) */
    .stButton button {{
        background-color: #d84315 !important;
        color: white !important;
        border-radius: 15px !important;
        font-weight: 900 !important;
        border: 2px solid #fff !important;
        box-shadow: 0 5px 0 #bf360c !important;
        font-size: 18px !important;
    }}
    .stButton button:active {{
        box-shadow: 0 0 0 #000 !important;
        transform: translateY(5px);
    }}
    
    /* YEŞİL GEÇ BUTONU */
    .next-btn button {{ background-color: #2e7d32 !important; box-shadow: 0 5px 0 #1b5e20 !important; }}
    
    /* Sema Hoca Uyarı Kutusu */
    .sema-hoca {{ 
        position: fixed; top: 40%; left: 50%; transform: translate(-50%, -50%); 
        background-color: #c62828; color: white !important; padding: 40px; 
        border-radius: 20px; border: 8px solid white; z-index: 99999; 
        font-size: 30px; font-weight: 900; text-align: center; 
        box-shadow: 0 0 100px rgba(0,0,0,0.9); animation: shake 0.5s;
    }}
    @keyframes shake {{ 0% {{ transform: translate(-50%, -50%) rotate(0deg); }} 25% {{ transform: translate(-50%, -50%) rotate(5deg); }} 50% {{ transform: translate(-50%, -50%) rotate(0eg); }} 75% {{ transform: translate(-50%, -50%) rotate(-5deg); }} 100% {{ transform: translate(-50%, -50%) rotate(0deg); }} }}

    /* Özür Dilerim Butonu */
    .ozur-container {{
        position: fixed; top: 60%; left: 50%; transform: translate(-50%, -50%);
        z-index: 100000;
    }}
    div[data-testid="stVerticalBlock"] > div > div[class*="ozur-container"] button {{
        background-color: white !important; color: #c62828 !important; border: 3px solid #c62828 !important;
    }}

    /* Okuma Köşesi Kartları */
    .bio-box {{ background-color: rgba(255, 255, 255, 0.95); color: black !important; padding: 20px; border-radius: 15px; border-left: 8px solid #ffb300; margin-bottom: 20px; font-size: 16px; }}
    .bio-box b, .bio-box div {{ color: black !important; }}
    
    /* İsim Tabelası */
    .creator-name {{ background-color: #33691e; color: #ffeb3b !important; text-align: center; padding: 10px; font-weight: 900; font-size: 20px; border-radius: 15px; margin-bottom: 20px; border: 3px solid #fff; box-shadow: 0 8px 0px rgba(0,0,0,0.4); text-transform: uppercase; }}
    
    /* Mobil Skor */
    .mobile-score {{ background-color: rgba(255, 255, 255, 0.95); padding: 10px; border-radius: 15px; border: 3px solid #33691e; text-align: center; margin-bottom: 15px; display: flex; justify-content: space-around; font-weight: bold; font-size: 18px; color: black !important; }}
    .mobile-score span {{ color: black !important; }}
    
    .sanat-aciklama {{ background-color: rgba(255, 253, 231, 0.95); color: black !important; border-left: 6px solid #fbc02d; padding: 20px; margin-top: 20px; font-size: 18px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    .sanat-aciklama div, .sanat-aciklama b {{ color: black !important; }}
    
    .kaydet-btn {{ display: block; background-color: #2e7d32; color: white !important; padding: 12px; text-align: center; border-radius: 15px; text-decoration: none; font-weight: 900; font-size: 18px; border: 3px solid #1b5e20; box-shadow: 0 4px 0 #1b5e20; margin-top: 15px; }}
    </style>
    """, unsafe_allow_html=True)

# --- SORU ÜRETME ---
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
        yanlis_siklar = random.sample(tum_sanatlar, 3)
        siklar = yanlis_siklar + [dogru_cevap]
        random.shuffle(siklar)
        return {"tur": "EDEBİ SANAT", "eser": soru_data["beyit"], "dogru_cevap": dogru_cevap, "siklar": siklar, "aciklama": soru_data["aciklama"]}
    
    elif kategori == "ROMAN_OZET":
        db = get_ozet_db()
        soru_data = random.choice(db)
        dogru_cevap = soru_data["yazar"]
        tum_yazarlar = list(set([x["yazar"] for x in db]))
        if dogru_cevap in tum_yazarlar: tum_yazarlar.remove(dogru_cevap)
        yanlis_siklar = random.sample(tum_yazarlar, 3)
        siklar = yanlis_siklar + [dogru_cevap]
        random.shuffle(siklar)
        return {"tur": "ROMAN ÖZETİ", "eser": soru_data["ozet"], "dogru_cevap": dogru_cevap, "siklar": siklar, "eser_adi": soru_data["roman"]}
    
    else:
        db = get_game_db(kategori)
        yazarlar = list(db.keys())
        secilen_yazar = random.choice(yazarlar)
        turlar = list(db[secilen_yazar].keys())
        secilen_tur = random.choice(turlar)
        eserler = db[secilen_yazar][secilen_tur]
        secilen_eser = random.choice(eserler)
        yanlis_yazarlar = random.sample([y for y in yazarlar if y != secilen_yazar], 3)
        siklar = yanlis_yazarlar + [secilen_yazar]
        random.shuffle(siklar)
        return {"eser": secilen_eser, "tur": secilen_tur, "dogru_cevap": secilen_yazar, "siklar": siklar}

# --- HEADER ---
st.markdown('<div class="creator-name">👑 ALPEREN SÜNGÜ 👑</div>', unsafe_allow_html=True)

# --- MENU SAYFASI ---
if st.session_state.page == "MENU":
    col_logo, col_title = st.columns([1, 2])
    with col_logo:
        # Logo gösterimi (Varsa resmi kullan, yoksa info)
        if os.path.exists("background.jpg"):
            with open("background.jpg", "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
            st.markdown(f'<img src="data:image/jpg;base64,{img_data}" width="120" style="border-radius:10px; border:2px solid #33691e;">', unsafe_allow_html=True)
        else:
            st.info("Logo")
            
    with col_title:
        st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
        st.markdown(f'<h1 style="background-color:#fff8e1; padding:10px; border-radius:15px; border:3px solid #33691e; color:#33691e !important; font-weight:900; text-align:center;">EDEBİYAT<br>LİGİ</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">🇹🇷</div><div class="menu-title">CUMH.</div></div>', unsafe_allow_html=True)
        if st.button("BAŞLA 🇹🇷"):
            st.session_state.kategori = "CUMHURİYET"
            st.session_state.page = "GAME"
            st.session_state.xp = 0
            st.session_state.soru_sayisi = 0
            st.session_state.soru_bitti = False
            st.session_state.mevcut_soru = yeni_soru_uret()
            st.rerun()
    with c2:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">📜</div><div class="menu-title">DİVAN</div></div>', unsafe_allow_html=True)
        if st.button("BAŞLA 📜"):
            st.session_state.kategori = "DİVAN"
            st.session_state.page = "GAME"
            st.session_state.xp = 0
            st.session_state.soru_sayisi = 0
            st.session_state.soru_bitti = False
            st.session_state.mevcut_soru = yeni_soru_uret()
            st.rerun()
    with c3:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">📖</div><div class="menu-title">ROMAN</div></div>', unsafe_allow_html=True)
        if st.button("BAŞLA 📖"):
            st.session_state.kategori = "ROMAN_OZET"
            st.session_state.page = "GAME"
            st.session_state.xp = 0
            st.session_state.soru_sayisi = 0
            st.session_state.soru_bitti = False
            st.session_state.mevcut_soru = yeni_soru_uret()
            st.rerun()
    with c4:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">🎨</div><div class="menu-title">EDEBİ SANATLAR</div></div>', unsafe_allow_html=True)
        if st.button("BAŞLA 🎨"):
            st.session_state.kategori = "SANATLAR"
            st.session_state.page = "GAME"
            st.session_state.xp = 0
            st.session_state.soru_sayisi = 0
            st.session_state.soru_bitti = False
            st.session_state.mevcut_soru = yeni_soru_uret()
            st.rerun()

    st.markdown("---")
    st.markdown("""<div class="menu-card" style="background-color:#ffeaa7; border-color:#ffb300;"><div style="font-size:40px;">🎅🏻 🌨️ 🎄</div><div class="menu-title" style="color:#e65100;">KIŞ OKUMA KÖŞESİ</div><div style="font-size:12px; color:black;">Ansiklopedi & Bilgi</div></div>""", unsafe_allow_html=True)
    if st.button("OKUMA KÖŞESİNE GİR ☕", use_container_width=True):
        st.session_state.page = "STUDY"
        st.rerun()

# --- STUDY SAYFASI ---
elif st.session_state.page == "STUDY":
    st.markdown("<h1 style='color:#c0392b; font-weight:900; text-align:center;'>🎅🏻 OKUMA KÖŞESİ 🎄</h1>", unsafe_allow_html=True)
    if st.button("⬅️ ANA MENÜYE DÖN"):
        st.session_state.page = "MENU"
        st.rerun()
    db_study = get_reading_db()
    yazar_listesi = sorted(list(db_study.keys()))
    
    # IZGARA SİSTEMİ (KARTLAR)
    cols = st.columns(3)
    for i, yazar in enumerate(yazar_listesi):
        with cols[i % 3]:
            # Beyaz kart görünümlü butonlar
            if st.button(f"👤 {yazar}", use_container_width=True):
                st.session_state.calisma_yazar = yazar
    
    # DETAY EKRANI
    if st.session_state.calisma_yazar:
        yazar = st.session_state.calisma_yazar
        bilgi = db_study[yazar]
        st.markdown("---")
        st.markdown(f"<div class='bio-box'><b>✍️ {yazar}</b><br>{bilgi['bio']}</div>", unsafe_allow_html=True)
        st.markdown("#### 📚 Eserleri ve Önemli Notlar")
        for eser, ozet in bilgi['eserler'].items():
            with st.expander(f"📖 {eser}"):
                st.markdown(f"<span style='color:black;'>{ozet}</span>", unsafe_allow_html=True)
        if st.button("LİSTEYİ KAPAT / TEMİZLE"):
            st.session_state.calisma_yazar = None
            st.rerun()

# --- GAME SAYFASI ---
elif st.session_state.page == "GAME":
    soru = st.session_state.mevcut_soru
    level = (st.session_state.soru_sayisi // 5) + 1
    
    # 1. SEMA HOCA UYARISI (En Üst Katman)
    if st.session_state.sema_hoca_kizdi:
        st.markdown("""
        <div class="sema-hoca">
            😡 SEMA HOCAN<br>ÇOK KIZDI!<br>
            <span style="font-size:20px; color:#ffeaa7;">Nasıl Bilemezsin?!</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Özür Dilerim Butonu
        st.markdown('<div class="ozur-container">', unsafe_allow_html=True)
        if st.button("Özür Dilerim 😔"):
            # A) EDEBİ SANATLAR İSE: Sadece uyarıyı kapat (Notu okumak için)
            if st.session_state.kategori == "SANATLAR":
                st.session_state.sema_hoca_kizdi = False
                st.rerun()
            
            # B) DİĞER MODLAR İSE: Direkt diğer soruya geç
            else:
                st.session_state.soru_sayisi += 1
                st.session_state.soru_bitti = False
                st.session_state.cevap_verildi = False
                st.session_state.sema_hoca_kizdi = False
                st.session_state.mevcut_soru = yeni_soru_uret()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("🏆 DURUM")
        st.metric("⭐ Level", f"{level}")
        st.metric("💎 Puan", f"{st.session_state.xp}")
        st.markdown("---")
        st.markdown(f"<div style='text-align:center;color:white;'>SKORU KAYDET:</div><a href='{GOOGLE_FORM_LINKI}' target='_blank' class='kaydet-btn'>📝 LİSTEYE EKLE</a>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("⬅️ ÇIKIŞ"):
            st.session_state.page = "MENU"
            st.session_state.xp = 0
            st.rerun()

    st.markdown(f"<div class='mobile-score'><span style='color:#33691e;'>⭐ Lv {level}</span><span style='color:#2e7d32;'>💎 {st.session_state.xp} XP</span></div>", unsafe_allow_html=True)
    st.progress((st.session_state.soru_sayisi % 5) * 20)
    
    if st.session_state.kategori == "SANATLAR":
        title_text = "BU HANGİ EDEBİ SANAT?"
        content_text = f'"{soru["eser"]}"'
        sub_text = "Dizelerdeki sanatı bul!"
    elif st.session_state.kategori == "ROMAN_OZET":
        title_text = "BU ROMANIN YAZARI KİM?"
        content_text = soru["eser"]
        sub_text = "Özeti dikkatli oku!"
    else:
        title_text = f"TÜR: {soru['tur']}"
        content_text = f"✨ {soru['eser']} ✨"
        sub_text = "Kime aittir?"
        
    st.markdown(f"""<div class="question-card"><div style="color:#33691e; font-weight:bold; font-size:16px;">{title_text}</div><div style="font-size:22px; font-weight:900; color:#d84315; margin: 15px 0; padding:10px; background:#fff3e0; border-radius:10px;">{content_text}</div><div style="font-size:18px; font-weight:bold; color:black;">{sub_text}</div></div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        # CEVAP VERİLDİYSE ŞIKLARI KİLİTLE
        cevap = st.radio("Seçim:", soru['siklar'], label_visibility="collapsed", disabled=st.session_state.soru_bitti)
    with col2:
        st.write("") 
        st.write("")
        
        # --- BUTON MANTIĞI ---
        if not st.session_state.soru_bitti:
            # Soru henüz cevaplanmadıysa YANITLA butonu
            if st.button("YANITLA 🚀", type="primary", use_container_width=True):
                st.session_state.cevap_verildi = True
                
                if cevap == soru['dogru_cevap']:
                    st.session_state.xp += 100
                    st.markdown(get_audio_html("dogru"), unsafe_allow_html=True)
                    st.success("MÜKEMMEL! +100 XP 🎯")
                    st.balloons()
                    
                    # SANATLAR ise açıklamayı gösterip bekle
                    if st.session_state.kategori == "SANATLAR":
                        if "aciklama" in soru:
                            st.markdown(f"""<div class="sanat-aciklama"><b>💡 HOCA NOTU:</b><br>{soru['aciklama']}</div>""", unsafe_allow_html=True)
                        st.session_state.soru_bitti = True # Butonu "Sıradaki" yap
                        st.rerun()
                    
                    # DİĞER MODLAR İSE -> DİREKT GEÇ
                    else:
                        time.sleep(1.2)
                        st.session_state.soru_sayisi += 1
                        st.session_state.soru_bitti = False
                        st.session_state.cevap_verildi = False
                        st.session_state.mevcut_soru = yeni_soru_uret()
                        st.rerun()

                else: # YANLIŞ CEVAP
                    st.markdown(get_audio_html("yanlis"), unsafe_allow_html=True)
                    st.session_state.sema_hoca_kizdi = True # Sema Hoca Kızdı!
                    st.error(f"YANLIŞ! Doğru Cevap: {soru['dogru_cevap']} 💔")
                    st.session_state.xp = max(0, st.session_state.xp - 20)
                    
                    # Sanatlarda yanlış yapılsa bile açıklama hazırlanır (Özür dileyince görünecek)
                    if st.session_state.kategori == "SANATLAR":
                        st.session_state.soru_bitti = True
                    
                    st.rerun()
        
        # Soru Bitti (Cevaplandı) -> Sadece SANATLAR modunda buraya düşer
        elif st.session_state.soru_bitti and not st.session_state.sema_hoca_kizdi:
            # Açıklamayı tekrar göster
            if "aciklama" in soru:
                st.markdown(f"""<div class="sanat-aciklama"><b>💡 HOCA NOTU:</b><br>{soru['aciklama']}</div>""", unsafe_allow_html=True)
                
            if st.button("SIRADAKİ SORUYA GEÇ ➡️", type="primary", use_container_width=True, key="next_btn"):
                st.session_state.soru_sayisi += 1
                st.session_state.soru_bitti = False
                st.session_state.cevap_verildi = False
                st.session_state.mevcut_soru = yeni_soru_uret()
                st.rerun()