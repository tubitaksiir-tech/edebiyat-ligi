import streamlit as st
import random
import time
import os
import urllib.parse

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Edebiyat Ligi",
    page_icon="📚",
    layout="centered"
)

# GOOGLE FORM LİNKİ
GOOGLE_FORM_LINKI = "https://docs.google.com/forms/d/e/1FAIpQLSd6x_NxAj58m8-5HAKpm6R6pmTvJ64zD-TETIPxF-wul5Muwg/viewform?usp=header"

# --- SES ÇALMA FONKSİYONU ---
def ses_cal(durum):
    """
    Duruma göre (dogru/yanlis) ses çalar.
    HTML audio etiketi kullanır, bu sayede ekstra kütüphane gerekmez.
    """
    if durum == "dogru":
        # Başarı Sesi (Magic Chime)
        ses_url = "https://www.soundjay.com/misc/sounds/magic-chime-01.mp3"
    else:
        # Hata Sesi (Fail Buzzer)
        ses_url = "https://www.soundjay.com/misc/sounds/fail-buzzer-01.mp3"
        
    # Sesi görünmez bir oynatıcıda otomatik çal
    st.markdown(f"""
        <audio autoplay style="display:none;">
            <source src="{ses_url}" type="audio/mp3">
        </audio>
    """, unsafe_allow_html=True)

# ======================================================
# 1. GENİŞLETİLMİŞ OYUN VERİTABANI
# ======================================================
@st.cache_data
def get_game_db(kategori):
    if kategori == "CUMHURİYET":
        return {
            "Ömer Seyfettin": {"Hikaye": ["Kaşağı", "Ant", "Falaka", "Pembe İncili Kaftan", "Bomba", "Yüksek Ökçeler", "Gizli Mabed", "Başını Vermeyen Şehit"], "Roman": ["Efruz Bey"]},
            "Ziya Gökalp": {"Şiir": ["Kızıl Elma", "Altın Işık", "Yeni Hayat"], "Fikir": ["Türkçülüğün Esasları", "Türkleşmek İslamlaşmak Muasırlaşmak"]},
            "Yakup Kadri Karaosmanoğlu": {"Roman": ["Yaban", "Kiralık Konak", "Sodom ve Gomore", "Nur Baba", "Ankara", "Panorama", "Bir Sürgün", "Hep O Şarkı"], "Anı": ["Zoraki Diplomat", "Anamın Kitabı"]},
            "Halide Edip Adıvar": {"Roman": ["Sinekli Bakkal", "Ateşten Gömlek", "Vurun Kahpeye", "Handan", "Tatarcık", "Yolpalas Cinayeti"], "Anı": ["Mor Salkımlı Ev"]},
            "Reşat Nuri Güntekin": {"Roman": ["Çalıkuşu", "Yaprak Dökümü", "Yeşil Gece", "Acımak", "Miskinler Tekkesi", "Dudaktan Kalbe", "Akşam Güneşi"]},
            "Peyami Safa": {"Roman": ["Dokuzuncu Hariciye Koğuşu", "Fatih-Harbiye", "Yalnızız", "Matmazel Noraliya'nın Koltuğu", "Bir Tereddüdün Romanı"]},
            "Tarık Buğra": {"Roman": ["Küçük Ağa", "Osmancık", "İbişin Rüyası", "Firavun İmanı", "Yağmur Beklerken"]},
            "Sait Faik Abasıyanık": {"Hikaye": ["Semaver", "Sarnıç", "Lüzumsuz Adam", "Son Kuşlar", "Alemdağ'da Var Bir Yılan", "Şahmerdan"]},
            "Sabahattin Ali": {"Roman": ["Kürk Mantolu Madonna", "Kuyucaklı Yusuf", "İçimizdeki Şeytan"], "Hikaye": ["Değirmen", "Kağnı", "Ses"]},
            "Ahmet Hamdi Tanpınar": {"Roman": ["Huzur", "Saatleri Ayarlama Enstitüsü", "Sahnenin Dışındakiler", "Mahur Beste"], "Deneme": ["Beş Şehir"]},
            "Necip Fazıl Kısakürek": {"Şiir": ["Çile", "Kaldırımlar", "Örümcek Ağı", "Ben ve Ötesi"], "Tiyatro": ["Bir Adam Yaratmak", "Reis Bey", "Tohum"]},
            "Nazım Hikmet": {"Şiir": ["Memleketimden İnsan Manzaraları", "Kuvayi Milliye Destanı", "Simavne Kadısı Oğlu Bedreddin", "835 Satır"]},
            "Yaşar Kemal": {"Roman": ["İnce Memed", "Yer Demir Gök Bakır", "Ağrı Dağı Efsanesi", "Yılanı Öldürseler", "Orta Direk", "Teneke"]},
            "Orhan Pamuk": {"Roman": ["Kara Kitap", "Benim Adım Kırmızı", "Masumiyet Müzesi", "Cevdet Bey ve Oğulları", "Sessiz Ev", "Kar"]},
            "Oğuz Atay": {"Roman": ["Tutunamayanlar", "Tehlikeli Oyunlar", "Bir Bilim Adamının Romanı"], "Hikaye": ["Korkuyu Beklerken"]},
            "Attila İlhan": {"Şiir": ["Ben Sana Mecburum", "Sisler Bulvarı", "Duvar", "Yağmur Kaçağı"], "Roman": ["Kurtlar Sofrası", "Sokaktaki Adam"]},
            "Cemal Süreya": {"Şiir": ["Üvercinka", "Sevda Sözleri", "Göçebe", "Beni Öp Sonra Doğur Beni"]},
            "Adalet Ağaoğlu": {"Roman": ["Ölmeye Yatmak", "Bir Düğün Gecesi", "Fikrimin İnce Gülü", "Yüksek Gerilim"]},
            "Orhan Kemal": {"Roman": ["Bereketli Topraklar Üzerinde", "Murtaza", "Eskici ve Oğulları", "Hanımın Çiftliği", "Cemile", "Baba Evi"]},
            "Kemal Tahir": {"Roman": ["Devlet Ana", "Yorgun Savaşçı", "Esir Şehrin İnsanları", "Rahmet Yolları Kesti", "Köyün Kamburu"]},
            "Refik Halit Karay": {"Hikaye": ["Memleket Hikayeleri", "Gurbet Hikayeleri"], "Roman": ["Sürgün", "Bugünün Saraylısı", "Yezidin Kızı", "Nilgün"]},
            "Mehmet Akif Ersoy": {"Şiir": ["Safahat"]},
            "Yahya Kemal Beyatlı": {"Şiir": ["Kendi Gök Kubbemiz", "Eski Şiirin Rüzgarıyla"], "Nesir": ["Aziz İstanbul", "Eğil Dağlar"]},
            "Faruk Nafiz Çamlıbel": {"Şiir": ["Han Duvarları", "Çoban Çeşmesi", "Dinle Neyden"], "Tiyatro": ["Akın", "Canavar"]},
            "Memduh Şevket Esendal": {"Roman": ["Ayaşlı ve Kiracıları", "Vassaf Bey"], "Hikaye": ["Otlakçı", "Mendil Altında"]},
            "Orhan Veli Kanık": {"Şiir": ["Garip", "Vazgeçemediğim", "Destan Gibi", "Yenisi"]},
            "Cahit Sıtkı Tarancı": {"Şiir": ["Otuz Beş Yaş", "Düşten Güzel", "Ömrümde Sükut"]},
            "Ahmet Muhip Dıranas": {"Şiir": ["Fahriye Abla", "Serenad", "Olvido", "Kar"], "Tiyatro": ["Gölgeler"]},
            "Ziya Osman Saba": {"Şiir": ["Sebil ve Güvercinler", "Geçen Zaman", "Nefes Almak"], "Hikaye": ["Mesut İnsanlar Fotoğrafhanesi"]},
            "Arif Damar": {"Şiir": ["Günden Güne", "İstanbul Bulutu", "Kedi Aklı"]},
            "Ferit Edgü": {"Roman": ["Hakkari'de Bir Mevsim (O)", "Kimse"], "Hikaye": ["Bir Gemide", "Çığlık"]},
            "Enis Behiç Koryürek": {"Şiir": ["Miras", "Güneşin Ölümü"], "Destan": ["Gemiciler"]},
            "Yusuf Ziya Ortaç": {"Şiir": ["Akından Akına"], "Mizah": ["Çimdik"]},
            "Orhan Seyfi Orhon": {"Şiir": ["Fırtına ve Kar", "Peri Kızı ile Çoban Hikayesi"]},
            "Halit Fahri Ozansoy": {"Şiir": ["Aruza Veda"], "Tiyatro": ["Baykuş"]},
            "Behçet Necatigil": {"Şiir": ["Kapalı Çarşı", "Evler", "Çevre", "Divançe"]},
            "Hilmi Yavuz": {"Şiir": ["Bakış Kuşu", "Bedreddin Üzerine Şiirler", "Doğu Şiirleri"]},
            "Cahit Külebi": {"Şiir": ["Adamın Biri", "Rüzgar", "Atatürk Kurtuluş Savaşı'nda", "Yeşeren Otlar"]},
            "Fazıl Hüsnü Dağlarca": {"Şiir": ["Havaya Çizilen Dünya", "Çocuk ve Allah", "Üç Şehitler Destanı"]},
            "Bedri Rahmi Eyüboğlu": {"Şiir": ["Yaradana Mektuplar", "Karadut", "Dol Karabakır Dol"]},
            "Salah Birsel": {"Deneme": ["Kahveler Kitabı", "Ah Beyoğlu Vah Beyoğlu"], "Şiir": ["Dünya İşleri"]},
            "Oktay Rifat": {"Şiir": ["Perçemli Sokak", "Karga ile Tilki", "Aşık Merdiveni"]},
            "Melih Cevdet Anday": {"Şiir": ["Rahatı Kaçan Ağaç", "Kolları Bağlı Odysseus", "Telgrafhane"]},
            "Yusuf Atılgan": {"Roman": ["Aylak Adam", "Anayurt Oteli"]},
            "Haldun Taner": {"Tiyatro": ["Keşanlı Ali Destanı", "Gözlerimi Kaparım Vazifemi Yaparım"], "Hikaye": ["Şişhaneye Yağmur Yağıyordu", "On İkiye Bir Var"]},
            "Sezai Karakoç": {"Şiir": ["Monna Rosa", "Körfez", "Hızırla Kırk Saat", "Şahdamar"]},
            "Turgut Uyar": {"Şiir": ["Göğe Bakma Durağı", "Dünyanın En Güzel Arabistanı", "Tütünler Islak"]},
            "Edip Cansever": {"Şiir": ["Yerçekimli Karanfil", "Masa Da Masaymış", "İkindi Üstü"]},
            "Ece Ayhan": {"Şiir": ["Bakışsız Bir Kedi Kara", "Yort Savul", "Kinar Hanımın Denizleri"]},
            "Falih Rıfkı Atay": {"Anı": ["Çankaya", "Zeytindağı"], "Gezi": ["Deniz Aşırı", "Taymis Kıyıları"]},
            "Nurullah Ataç": {"Deneme": ["Günlerin Getirdiği", "Karalama Defteri", "Sözden Söze"]},
            "Ahmet Kutsi Tecer": {"Şiir": ["Orada Bir Köy Var Uzakta"], "Tiyatro": ["Koçyiğit Köroğlu", "Köşebaşı"]},
            "Fakir Baykurt": {"Roman": ["Yılanların Öcü", "Kaplumbağalar", "Tırpan"]},
            "Latife Tekin": {"Roman": ["Sevgili Arsız Ölüm", "Berci Kristin Çöp Masalları"]}
        }
    else: # DİVAN
        return {
            "Fuzuli": {"Mesnevi": ["Leyla ile Mecnun", "Bengü Bade"], "Nesir": ["Şikayetname", "Hadikatü's Süeda"]},
            "Baki": {"Şiir": ["Kanuni Mersiyesi"], "Nesir": ["Fezail-i Mekke"]},
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
            "Kaygusuz Abdal": {"Nesir": ["Budalaname", "Muglataname"]},
            "Aşık Paşa": {"Mesnevi": ["Garibname"]},
            "Hoca Dehhani": {"Destan": ["Selçuklu Şehnamesi"]},
            "Kadı Burhaneddin": {"Şiir": ["Tuyuğlar"]},
            "Nedim": {"Şiir": ["Şarkı Formu"]},
            "Nergisi": {"Nesir": ["Nergisi Hamsesi"]}
        }

# ======================================================
# 2. ROMAN ÖZETLERİ VERİTABANI
# ======================================================
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

# ======================================================
# 3. EDEBİ SANATLAR VERİTABANI
# ======================================================
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

# ======================================================
# 4. OKUMA KÖŞESİ VERİTABANI
# ======================================================
@st.cache_data
def get_reading_db():
    return {
        "Ferit Edgü": {"bio": "Küçürek öykünün ustasıdır. Hakkari'de öğretmenlik yaparken yaşadıklarını eserlerine yansıtmıştır.", "eserler": {"Hakkari'de Bir Mevsim": "Yabancılaşma ve yalnızlık.", "Çığlık": "Kısa ve çarpıcı öyküler."}},
        "Ziya Osman Saba": {"bio": "Yedi Meşaleciler'in şiire en sadık ismidir. Ev, aile, küçük mutluluklar şairidir.", "eserler": {"Sebil ve Güvercinler": "Huzur ve ahiret özlemi.", "Mesut İnsanlar Fotoğrafhanesi": "İstanbul hikayeleri."}},
        "Arif Damar": {"bio": "Toplumcu gerçekçi şairdir. 'Günden Güne' ile tanınır.", "eserler": {"Günden Güne": "Toplumsal umut şiirleri."}},
        "Enis Behiç Koryürek": {"bio": "Beş Hececilerdendir. Deniz ve korsan şiirleriyle tanınır.", "eserler": {"Gemiciler": "Türk denizciliğini anlatan şiir."}},
        "Ahmet Muhip Dıranas": {"bio": "Saf şiir anlayışını benimsemiştir. Sembolizmden etkilenmiştir.", "eserler": {"Fahriye Abla": "Efsaneleşmiş lirik şiir.", "Olvido": "Unutuş temalı şiir."}},
        "Cahit Sıtkı Tarancı": {"bio": "Ölüm, yaşama sevinci ve yalnızlık temalarını işler. 'Otuz Beş Yaş' şairidir.", "eserler": {"Otuz Beş Yaş": "Ölüm korkusu ve yaşlılık."}},
        "Orhan Veli Kanık": {"bio": "Garip akımının öncüsüdür. Şiirden ölçü, kafiye ve söz sanatlarını atmıştır.", "eserler": {"İstanbul'u Dinliyorum": "İstanbul sevgisi."}},
        "Behçet Necatigil": {"bio": "Evler Şairi olarak bilinir. Modern insanın yalnızlığını ve ev içi yaşamı anlatır.", "eserler": {"Kapalı Çarşı": "Şehir ve insan ilişkisi."}},
        "Fazıl Hüsnü Dağlarca": {"bio": "Türkçem benim ses bayrağım diyen, çok üretken bir şairdir. Destan şairidir.", "eserler": {"Üç Şehitler Destanı": "Kurtuluş Savaşı."}},
        "Peyami Safa": {"bio": "Psikolojik romanın ve Doğu-Batı çatışmasının en güçlü kalemidir.", "eserler": {"Fatih-Harbiye": "Kültür çatışması."}},
        "Tarık Buğra": {"bio": "Milli ve manevi değerleri, tarihi olayları psikolojik derinlikle işler.", "eserler": {"Küçük Ağa": "Kuvayi Milliye bilinci."}},
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

# --- CSS VE TASARIM ---
oyun_deseni = "https://www.transparenttextures.com/patterns/cubes.png"
okuma_deseni = "https://www.transparenttextures.com/patterns/candy-cane.png"

# SES ÇALMA FONKSİYONU
def ses_cal(durum):
    if durum == "dogru":
        ses_url = "https://www.soundjay.com/misc/sounds/magic-chime-01.mp3"
    else:
        ses_url = "https://www.soundjay.com/misc/sounds/fail-buzzer-01.mp3"
    st.markdown(f'<audio autoplay style="display:none;"><source src="{ses_url}" type="audio/mp3"></audio>', unsafe_allow_html=True)

# Arka Plan Ayarı
if st.session_state.page == "STUDY":
    bg_style = f"background-color: #ffcccc; background-image: url('{okuma_deseni}');"
    sidebar_color = "#c0392b"
else:
    bg_style = f"background: linear-gradient(135deg, #ff9ff3, #ff6b6b, #51cf66); background-image: linear-gradient(135deg, rgba(255,159,243,0.8), rgba(255,107,107,0.8), rgba(81,207,102,0.8)), url('{oyun_deseni}'); background-blend-mode: overlay; background-size: cover;"
    sidebar_color = "#2d3436"

st.markdown(f"""
    <style>
    .stApp {{ {bg_style} background-attachment: fixed; }}
    html, body, p, div, label, h1, h2, h3, h4, h5, h6, li, span {{ color: #000000 !important; font-family: 'Segoe UI', sans-serif; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_color} !important; border-right: 4px solid #fff; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    
    /* Sema Hoca Uyarı Kutusu */
    .sema-hoca {{ position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background-color: #d63031; color: white !important; padding: 40px; border-radius: 20px; border: 5px solid white; z-index: 9999; font-size: 30px; font-weight: 900; text-align: center; box-shadow: 0 0 50px rgba(0,0,0,0.5); animation: shake 0.5s; }}
    @keyframes shake {{ 0% {{ transform: translate(-50%, -50%) rotate(0deg); }} 25% {{ transform: translate(-50%, -50%) rotate(5deg); }} 50% {{ transform: translate(-50%, -50%) rotate(0eg); }} 75% {{ transform: translate(-50%, -50%) rotate(-5deg); }} 100% {{ transform: translate(-50%, -50%) rotate(0deg); }} }}

    .sanat-aciklama {{ background-color: #fff3cd; border-left: 6px solid #ffc107; padding: 15px; margin-top: 15px; font-size: 18px; border-radius: 10px; }}
    .menu-card {{ background-color: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 20px; text-align: center; border: 4px solid #2d3436; cursor: pointer; transition: all 0.2s; margin-bottom: 15px; box-shadow: 0 6px 0px #d63031; }}
    .menu-card:hover {{ transform: translateY(-5px); background-color: #ffffff; }}
    .menu-title {{ font-size: 18px; font-weight: 900; color: #d63031; text-transform: uppercase; }}
    .stButton button {{ background-color: #d63031 !important; color: white !important; border-radius: 15px !important; font-weight: 900 !important; border: 3px solid #000 !important; box-shadow: 0 5px 0 #000 !important; }}
    .stButton button:active {{ box-shadow: 0 0 0 #000 !important; transform: translateY(5px); }}
    .question-card {{ background-color: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 25px; border: 4px solid #2d3436; box-shadow: 0 8px 0px #2d3436; text-align: center; margin-bottom: 25px; }}
    .stRadio {{ background-color: rgba(255, 255, 255, 0.9) !important; padding: 15px; border-radius: 20px; border: 3px solid #2d3436; }}
    .creator-name {{ background-color: #2d3436; color: #00cec9 !important; text-align: center; padding: 10px; font-weight: 900; font-size: 20px; border-radius: 15px; letter-spacing: 2px; margin-bottom: 20px; border: 3px solid #fff; box-shadow: 0 8px 0px rgba(0,0,0,0.4); text-transform: uppercase; }}
    .study-title {{ color: #c0392b !important; font-size: 30px; font-weight: 900; text-align: center; text-shadow: 2px 2px 0px white; }}
    .bio-box {{ background-color: #ffeaa7; padding: 15px; border-radius: 10px; border-left: 5px solid #fdcb6e; margin-bottom: 20px; font-style: italic; }}
    .kaydet-btn {{ display: block; background-color: #00b894; color: white; padding: 12px; text-align: center; border-radius: 15px; text-decoration: none; font-weight: 900; font-size: 18px; border: 3px solid #006266; box-shadow: 0 4px 0 #006266; margin-top: 15px; }}
    .mobile-score {{ background-color: rgba(255,255,255,0.9); padding: 10px; border-radius: 15px; border: 3px solid #2d3436; text-align: center; margin-bottom: 15px; display: flex; justify-content: space-around; font-weight: bold; font-size: 18px; }}
    </style>
    """, unsafe_allow_html=True)

# --- SORU ÜRETME ---
def yeni_soru_uret():
    kategori = st.session_state.kategori
    st.session_state.sanat_aciklama = ""
    st.session_state.sema_hoca_kizdi = False
    
    if kategori == "SANATLAR":
        db = get_sanatlar_db()
        soru_data = random.choice(db)
        dogru_cevap = soru_data["sanat"]
        tum_sanatlar = list(set([x["sanat"] for x in db]))
        if dogru_cevap in tum_sanatlar: tum_sanatlar.remove(dogru_cevap)
        yanlis_siklar = random.sample(tum_sanatlar, 3)
        siklar = yanlis_siklar + [dogru_cevap]
        random.shuffle(siklar)
        st.session_state.cevap_verildi = False
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
        st.session_state.cevap_verildi = False
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
        st.session_state.cevap_verildi = False
        return {"eser": secilen_eser, "tur": secilen_tur, "dogru_cevap": secilen_yazar, "siklar": siklar}

# --- HEADER ---
st.markdown('<div class="creator-name">👑 ALPEREN SÜNGÜ 👑</div>', unsafe_allow_html=True)

# --- MENU SAYFASI ---
if st.session_state.page == "MENU":
    col_logo, col_title = st.columns([1, 2])
    with col_logo:
        resim_adi = "background.jpg"
        if os.path.exists(resim_adi): st.image(resim_adi, width=120)
        else: st.info("Logo")
    with col_title:
        st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
        st.markdown(f'<h1 style="background-color:rgba(255,255,255,0.8); padding:10px; border-radius:15px; border:3px solid #2d3436; color:#2d3436 !important; font-weight:900; text-align:center;">EDEBİYAT<br>LİGİ</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">🇹🇷</div><div class="menu-title">CUMH.</div></div>', unsafe_allow_html=True)
        if st.button("BAŞLA 🇹🇷"):
            st.session_state.kategori = "CUMHURİYET"
            st.session_state.page = "GAME"
            st.session_state.xp = 0
            st.session_state.soru_sayisi = 0
            st.session_state.mevcut_soru = yeni_soru_uret()
            st.rerun()
    with c2:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">📜</div><div class="menu-title">DİVAN</div></div>', unsafe_allow_html=True)
        if st.button("BAŞLA 📜"):
            st.session_state.kategori = "DİVAN"
            st.session_state.page = "GAME"
            st.session_state.xp = 0
            st.session_state.soru_sayisi = 0
            st.session_state.mevcut_soru = yeni_soru_uret()
            st.rerun()
    with c3:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">📖</div><div class="menu-title">ROMAN</div></div>', unsafe_allow_html=True)
        if st.button("BAŞLA 📖"):
            st.session_state.kategori = "ROMAN_OZET"
            st.session_state.page = "GAME"
            st.session_state.xp = 0
            st.session_state.soru_sayisi = 0
            st.session_state.mevcut_soru = yeni_soru_uret()
            st.rerun()
    with c4:
        st.markdown('<div class="menu-card"><div style="font-size:30px;">🎨</div><div class="menu-title">SANAT</div></div>', unsafe_allow_html=True)
        if st.button("BAŞLA 🎨"):
            st.session_state.kategori = "SANATLAR"
            st.session_state.page = "GAME"
            st.session_state.xp = 0
            st.session_state.soru_sayisi = 0
            st.session_state.mevcut_soru = yeni_soru_uret()
            st.rerun()

    st.markdown("---")
    st.markdown("""<div class="menu-card" style="background-color:#ffeaa7; border-color:#d35400;"><div style="font-size:40px;">🎅🏻 🌨️ 🎄</div><div class="menu-title" style="color:#d35400;">KIŞ OKUMA KÖŞESİ</div><div style="font-size:12px;">Ansiklopedi & Bilgi</div></div>""", unsafe_allow_html=True)
    if st.button("OKUMA KÖŞESİNE GİR ☕", use_container_width=True):
        st.session_state.page = "STUDY"
        st.rerun()

# --- STUDY SAYFASI ---
elif st.session_state.page == "STUDY":
    st.markdown("<h1 class='study-title'>🎅🏻 OKUMA KÖŞESİ 🎄</h1>", unsafe_allow_html=True)
    if st.button("⬅️ ANA MENÜYE DÖN"):
        st.session_state.page = "MENU"
        st.rerun()
    db_study = get_reading_db()
    yazar_listesi = sorted(list(db_study.keys()))
    secilen_yazar = st.selectbox("Bir Yazar Seçip Bilgilenelim:", ["Seçiniz..."] + yazar_listesi)
    if secilen_yazar != "Seçiniz...":
        bilgi = db_study[secilen_yazar]
        st.markdown(f"<div class='bio-box'><b>✍️ {secilen_yazar}</b><br>{bilgi['bio']}</div>", unsafe_allow_html=True)
        st.markdown("#### 📚 Eserleri")
        for eser, ozet in bilgi['eserler'].items():
            with st.expander(f"📖 {eser}"):
                st.write(ozet)

# --- GAME SAYFASI ---
elif st.session_state.page == "GAME":
    soru = st.session_state.mevcut_soru
    level = (st.session_state.soru_sayisi // 5) + 1
    
    if st.session_state.sema_hoca_kizdi:
        st.markdown("""<div class="sema-hoca">😡 SEMA HOCAN<br>ÇOK KIZDI!<br><span style="font-size:20px">Nasıl Bilemezsin?!</span></div>""", unsafe_allow_html=True)
    
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

    st.markdown(f"<div class='mobile-score'><span style='color:#d63031;'>⭐ Lv {level}</span><span style='color:#00cec9;'>💎 {st.session_state.xp} XP</span></div>", unsafe_allow_html=True)
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
        
    st.markdown(f"""<div class="question-card"><div style="color:#636e72; font-weight:bold; font-size:16px;">{title_text}</div><div style="font-size:22px; font-weight:900; color:#d63031; margin: 15px 0; padding:10px; background:#f1f2f6; border-radius:10px;">{content_text}</div><div style="font-size:18px; font-weight:bold;">{sub_text}</div></div>""", unsafe_allow_html=True)

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
                ses_cal("dogru")
                st.success("MÜKEMMEL! +100 XP 🎯")
                st.balloons()
            else:
                ses_cal("yanlis")
                st.session_state.sema_hoca_kizdi = True
                st.error(f"YANLIŞ! Doğru Cevap: {soru['dogru_cevap']} 💔")
                st.session_state.xp = max(0, st.session_state.xp - 20)
            
            if st.session_state.kategori == "SANATLAR" and "aciklama" in soru:
                st.markdown(f"""<div class="sanat-aciklama"><b>💡 HOCA NOTU:</b><br>{soru['aciklama']}</div>""", unsafe_allow_html=True)
            if st.session_state.kategori == "ROMAN_OZET" and "eser_adi" in soru:
                st.info(f"Romanın Adı: **{soru['eser_adi']}**")

            st.session_state.soru_sayisi += 1
            st.session_state.cevap_verildi = True
            time.sleep(3.5)
            st.session_state.mevcut_soru = yeni_soru_uret()
            st.rerun()