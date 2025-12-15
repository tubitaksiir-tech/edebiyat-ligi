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

# --- RENK PALETİ ---
sidebar_color = "#1b3a1a"
card_bg_color = "#2e5a27"
text_color_cream = "#ffffff" # Bembeyaz yazı (Okunabilirlik için)
red_warning_color = "#c62828"

# --- SES ÇALMA FONKSİYONU ---
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
            "Ömer Seyfettin": {"Hikaye": ["Kaşağı", "Ant", "Falaka", "Pembe İncili Kaftan", "Bomba", "Yüksek Ökçeler", "Gizli Mabed", "Başını Vermeyen Şehit", "Perili Köşk", "Bahar ve Kelebekler", "Harem", "Yalnız Efe"], "Roman": ["Efruz Bey"]},
            "Ziya Gökalp": {"Şiir": ["Kızıl Elma", "Altın Işık", "Yeni Hayat"], "Fikir": ["Türkçülüğün Esasları", "Türkleşmek İslamlaşmak Muasırlaşmak", "Türk Medeniyeti Tarihi"]},
            "Yakup Kadri Karaosmanoğlu": {"Roman": ["Yaban", "Kiralık Konak", "Sodom ve Gomore", "Nur Baba", "Ankara", "Panorama", "Bir Sürgün", "Hep O Şarkı", "Hüküm Gecesi"], "Anı": ["Zoraki Diplomat", "Anamın Kitabı", "Gençlik ve Edebiyat Hatıraları", "Politikada 45 Yıl", "Vatan Yolunda"]},
            "Halide Edip Adıvar": {"Roman": ["Sinekli Bakkal", "Ateşten Gömlek", "Vurun Kahpeye", "Handan", "Tatarcık", "Yolpalas Cinayeti", "Kalp Ağrısı", "Zeyno'nun Oğlu", "Yeni Turan", "Sonsuz Panayır", "Döner Ayna"], "Anı": ["Mor Salkımlı Ev", "Türk'ün Ateşle İmtihanı"]},
            "Reşat Nuri Güntekin": {"Roman": ["Çalıkuşu", "Yaprak Dökümü", "Yeşil Gece", "Acımak", "Miskinler Tekkesi", "Dudaktan Kalbe", "Akşam Güneşi", "Kavak Yelleri", "Damga", "Bir Kadın Düşmanı", "Değirmen", "Gizli El", "Eski Hastalık"]},
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
    else: # DİVAN
        return {
            "Fuzuli": {"Mesnevi": ["Leyla ile Mecnun", "Bengü Bade", "Sohbetü'l Esmar"], "Nesir": ["Şikayetname", "Hadikatü's Süeda", "Rind ü Zahid"]},
            "Baki": {"Şiir": ["Kanuni Mersiyesi", "Baki Divanı"], "Nesir": ["Fezail-i Mekke"]},
            "Nefi": {"Hiciv": ["Siham-ı Kaza"], "Mesnevi": ["Tuhfetü’l-Uşşak"]},
            "Nabi": {"Mesnevi": ["Hayriye", "Hayrabad", "Surname"], "Gezi": ["Tuhfetü'l Haremeyn"]},
            "Şeyh Galip": {"Mesnevi": ["Hüsnü Aşk"]},
            "Şeyhi": {"Fabl": ["Harname"], "Mesnevi": ["Hüsrev ü Şirin"]},
            "Katip Çelebi": {"Bibliyografya": ["Keşfü'z Zunun"], "Coğrafya": ["Cihannüma"], "Tarih": ["Fezleke"]},
            "Evliya Çelebi": {"Gezi": ["Seyahatname"]},
            "Ali Şir Nevai": {"Sözlük": ["Muhakemetü'l Lügateyn"], "Tezkire": ["Mecalisü'n Nefais"], "Mesnevi": ["Lisanü't Tayr"]},
            "Sinan Paşa": {"Süslü Nesir": ["Tazarruname", "Maarifname"]},
            "Mercimek Ahmet": {"Sade Nesir": ["Kabusname"]},
            "Süleyman Çelebi": {"Mesnevi": ["Vesiletü'n Necat (Mevlid)"]},
            "Ahmedi": {"Mesnevi": ["İskendername", "Cemşid ü Hurşid"]},
            "Babürşah": {"Anı": ["Babürname"]},
            "Seydi Ali Reis": {"Gezi": ["Mir'atü'l Memalik"]},
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
            "Pir Sultan Abdal": {"Şiir": ["Nefesler"]},
            "Eşrefoğlu Rumi": {"Tasavvuf": ["Müzekkin Nüfus"]},
            "Taşlıcalı Yahya": {"Mesnevi": ["Şah ü Geda", "Yusuf ü Züleyha"]},
            "Zati": {"Mesnevi": ["Şem ü Pervane"]}
        }

@st.cache_data
def get_ozet_db():
    return [
        {"yazar": "Namık Kemal", "roman": "İntibah", "ozet": "Ali Bey, mirasyedi bir gençtir. Mahpeyker adlı hafif meşrep bir kadına aşık olur. Dilaşub adlı cariye ile Mahpeyker arasında kalır. Türk edebiyatının ilk edebi romanıdır."},
        {"yazar": "Namık Kemal", "roman": "Cezmi", "ozet": "Türk edebiyatının ilk tarihi romanıdır. II. Selim döneminde İran'la yapılan savaşları ve Cezmi'nin kahramanlıklarını anlatır."},
        {"yazar": "Recaizade Mahmut Ekrem", "roman": "Araba Sevdası", "ozet": "Bihruz Bey, alafrangalık özentisi, mirasyedi bir gençtir. Periveş adlı kadını soylu sanır. Yanlış batılılaşma mizahi dille anlatılır."},
        {"yazar": "Samipaşazade Sezai", "roman": "Sergüzeşt", "ozet": "Kafkasya'dan kaçırılıp İstanbul'a getirilen esir kız Dilber'in acıklı hikayesi. Dilber, Celal Bey'e aşık olur ama Nil Nehri'ne atlayarak intihar eder."},
        {"yazar": "Halit Ziya Uşaklıgil", "roman": "Mai ve Siyah", "ozet": "Ahmet Cemil'in şair olma hayalleri (Mai) ile hayatın acı gerçekleri (Siyah) arasındaki çatışma anlatılır. Batılı anlamda ilk teknik romandır."},
        {"yazar": "Halit Ziya Uşaklıgil", "roman": "Aşk-ı Memnu", "ozet": "Bihter, Adnan Bey ile evlenir ancak Behlül ile yasak aşk yaşar. Firdevs Hanım, Nihal ve Beşir diğer karakterlerdir."},
        {"yazar": "Mehmet Rauf", "roman": "Eylül", "ozet": "Suat, Süreyya ve Necip arasındaki yasak aşkı anlatan, olaydan çok psikolojik tahlillere dayanan ilk psikolojik romandır."},
        {"yazar": "Hüseyin Rahmi Gürpınar", "roman": "Şıpsevdi", "ozet": "Meftun Bey, alafranga züppe bir tiptir. Zengin Kasım Efendi'nin kızı Edibe ile parası için evlenmek ister. Gulyabani ve Mürebbiye ile benzer temadadır."},
        {"yazar": "Yakup Kadri Karaosmanoğlu", "roman": "Yaban", "ozet": "Ahmet Celal, bir Anadolu köyüne yerleşir. Köylü onu düşman ve 'Yaban' olarak görür. Aydın-Halk çatışması işlenir."},
        {"yazar": "Yakup Kadri Karaosmanoğlu", "roman": "Kiralık Konak", "ozet": "Naim Efendi (Gelenek), Servet Bey (Yozlaşma) ve Seniha (Köklerinden kopuş) üzerinden üç nesil arasındaki çatışmayı anlatır."},
        {"yazar": "Yakup Kadri Karaosmanoğlu", "roman": "Sodom ve Gomore", "ozet": "Mütareke dönemi İstanbul'unda işgalcilerle işbirliği yapan yozlaşmış çevreleri anlatır. Leyla ve Necdet baş karakterlerdir."},
        {"yazar": "Reşat Nuri Güntekin", "roman": "Çalıkuşu", "ozet": "Feride, Kamran'a küsüp Anadolu'da öğretmenlik yapar. İdealist öğretmen tipinin en güzel örneğidir."},
        {"yazar": "Reşat Nuri Güntekin", "roman": "Yeşil Gece", "ozet": "Öğretmen Şahin Efendi'nin softalarla ve yobazlıkla mücadelesini anlatan tezli bir romandır."},
        {"yazar": "Reşat Nuri Güntekin", "roman": "Yaprak Dökümü", "ozet": "Ali Rıza Bey ve ailesinin yanlış batılılaşma ve ahlaki çöküş nedeniyle dağılmasını anlatır."},
        {"yazar": "Halide Edip Adıvar", "roman": "Sinekli Bakkal", "ozet": "Rabia ve Peregrini aşkı üzerinden II. Abdülhamit dönemi İstanbul'unu ve Doğu-Batı sentezini anlatır."},
        {"yazar": "Halide Edip Adıvar", "roman": "Vurun Kahpeye", "ozet": "Aliye Öğretmen'in Anadolu'da yobaz Hacı Fettah ve işbirlikçiler tarafından linç edilmesini anlatan Kurtuluş Savaşı romanıdır."},
        {"yazar": "Peyami Safa", "roman": "Dokuzuncu Hariciye Koğuşu", "ozet": "Hasta bir çocuğun bacağındaki kemik veremi ve Nüzhet'e olan aşkı. Psikolojik tahliller yoğundur."},
        {"yazar": "Peyami Safa", "roman": "Fatih-Harbiye", "ozet": "Neriman'ın Fatih (Doğu) ile Harbiye (Batı) arasında kalışını, Şinasi ve Macit üzerinden anlatır."},
        {"yazar": "Ahmet Hamdi Tanpınar", "roman": "Saatleri Ayarlama Enstitüsü", "ozet": "Hayri İrdal ve Halit Ayarcı üzerinden Türk toplumunun modernleşme ironisi anlatılır."},
        {"yazar": "Ahmet Hamdi Tanpınar", "roman": "Huzur", "ozet": "Mümtaz ve Nuran aşkı, İstanbul sevgisi ve II. Dünya Savaşı huzursuzluğu işlenir."},
        {"yazar": "Oğuz Atay", "roman": "Tutunamayanlar", "ozet": "Turgut Özben, intihar eden arkadaşı Selim Işık'ın izini sürer. Küçük burjuva aydınının dramını anlatan postmodern bir eserdir."},
        {"yazar": "Orhan Pamuk", "roman": "Kara Kitap", "ozet": "Galip, kayıp karısı Rüya'yı ve Celal'i İstanbul sokaklarında arar. Şeyh Galip'in Hüsn ü Aşk'ına göndermeler vardır."},
        {"yazar": "Yaşar Kemal", "roman": "İnce Memed", "ozet": "Abdi Ağa'nın zulmüne başkaldıran Memed'in dağa çıkıp eşkıya olmasını ve köylü haklarını savunmasını anlatır."},
        {"yazar": "Sabahattin Ali", "roman": "Kürk Mantolu Madonna", "ozet": "Raif Efendi'nin Almanya'da Maria Puder ile yaşadığı hüzünlü aşk ve sonrasında içine kapanışı anlatılır."},
        {"yazar": "Sabahattin Ali", "roman": "Kuyucaklı Yusuf", "ozet": "Yusuf'un ailesinin öldürülmesi, Kaymakam tarafından evlat edinilmesi ve Muazzez'e olan aşkı anlatılır."},
        {"yazar": "Yusuf Atılgan", "roman": "Anayurt Oteli", "ozet": "Otel katibi Zebercet'in yalnızlığı ve psikolojik çöküşü. Gecikmeli Ankara treniyle gelen kadını bekler."},
        {"yazar": "Adalet Ağaoğlu", "roman": "Ölmeye Yatmak", "ozet": "Aysel'in bir otel odasında intiharı düşünürken geçmişiyle hesaplaşması."},
        {"yazar": "Ferit Edgü", "roman": "Hakkari'de Bir Mevsim", "ozet": "Bir öğretmenin Hakkari'nin Pirkanis köyündeki yalnızlığı ve köylülerle iletişimi (O adlı roman)."},
        {"yazar": "Kemal Tahir", "roman": "Devlet Ana", "ozet": "Osmanlı'nın kuruluşunu, Ertuğrul Gazi ve Osman Bey üzerinden anlatan tarihi romandır."},
        {"yazar": "Kemal Tahir", "roman": "Yorgun Savaşçı", "ozet": "Milli Mücadele dönemini Cehennem Yüzbaşı Cemil üzerinden anlatan tarihi roman."},
        {"yazar": "Tarık Buğra", "roman": "Küçük Ağa", "ozet": "İstanbullu Hoca'nın Kuvayi Milliye karşıtlığından, Akşehir'de bilinçlenerek Milli Mücadele destekçisine dönüşmesi."},
        {"yazar": "Orhan Kemal", "roman": "Bereketli Topraklar Üzerinde", "ozet": "Çukurova'ya çalışmaya giden üç arkadaşın (İflahsızın Yusuf, Köse Hasan, Pehlivan Ali) dramı."},
        {"yazar": "Nabizade Nazım", "roman": "Zehra", "ozet": "İlk psikolojik roman denemesidir. Kıskançlık teması işlenir. Zehra'nın Suphi'ye olan hastalıklı kıskançlığı anlatılır."},
        {"yazar": "Nabizade Nazım", "roman": "Karabibik", "ozet": "İlk köy romanıdır. Antalya'nın Kaş ilçesinde geçer. Karabibik'in tarlasını sürmek için öküz alma çabası anlatılır."}
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
                "Huzur": "Mümtaz ve Nuran aşkı üzerinden Doğu-Batı çatışması. AYT favorisidir.",
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
        "Peyami Safa": {"bio": "Psikolojik romanın güçlü kalemi. Doğu-Batı çatışması.", "eserler": {"Fatih-Harbiye": "Kültür çatışması.", "Dokuzuncu Hariciye Koğuşu": "Psikolojik roman."}},
        "Tarık Buğra": {"bio": "Tarihi ve psikolojik derinlikli romanlar.", "eserler": {"Küçük Ağa": "Kuvayi Milliye bilinci."}},
        "Halide Edip Adıvar": {"bio": "Milli Mücadele'nin kadın kahramanı.", "eserler": {"Sinekli Bakkal": "Töre romanı.", "Ateşten Gömlek": "Kurtuluş Savaşı."}},
        "Reşat Nuri Güntekin": {"bio": "Anadolu romancısı. Realizm.", "eserler": {"Çalıkuşu": "İdealist öğretmen.", "Yaprak Dökümü": "Sosyal değişim."}},
        "Mehmet Rauf": {"bio": "Servet-i Fünun yazarı. Psikolojik roman.", "eserler": {"Eylül": "İlk psikolojik roman."}},
        "Yakup Kadri Karaosmanoğlu": {"bio": "Nehir romanlarıyla toplum tarihini yazar.", "eserler": {"Yaban": "Aydın-Köylü çatışması.", "Kiralık Konak": "Kuşak çatışması."}},
        "Sait Faik Abasıyanık": {"bio": "Durum hikayecisi. İstanbul aşığı.", "eserler": {"Semaver": "Sıradan insanlar.", "Alemdağ'da Var Bir Yılan": "Sürrealizm."}},
        "Oğuz Atay": {"bio": "Postmodernizmin öncüsü.", "eserler": {"Tutunamayanlar": "Aydın bunalımı."}},
        "Namık Kemal": {"bio": "Vatan şairi. Tanzimat 1. Dönem.", "eserler": {"İntibah": "İlk edebi roman.", "Vatan Yahut Silistre": "İlk tiyatro."}}
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

# --- CSS TASARIMI (KESİN RESİM LİNKİ - YEŞİL KİTAPLAR) ---
bg_image_url = "https://e0.pxfuel.com/wallpapers/985/844/desktop-wallpaper-booknerd-book-and-background-literature.jpg"

st.markdown(f"""
    <style>
    /* ARKA PLAN AYARLARI */
    .stApp {{
        background-image: url("{bg_image_url}");
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
        border-right: 4px solid #3e7a39;
    }}
    [data-testid="stSidebar"] * {{
        color: #ffffff !important;
    }}
    
    /* GENEL KUTU TASARIMI (KOYU YEŞİL ZEMİN, BEYAZ YAZI) */
    
    /* Soru Kartı */
    .question-card {{
        background-color: {card_bg_color} !important;
        padding: 25px;
        border-radius: 20px;
        border: 4px solid #3e7a39;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        text-align: center;
        margin-bottom: 25px;
    }}
    .question-card div, .question-card span, .question-card p {{
        color: {text_color_cream} !important;
    }}
    
    /* Şık Kutuları (Radio) */
    .stRadio {{
        background-color: {card_bg_color} !important;
        padding: 20px;
        border-radius: 20px;
        border: 3px solid #3e7a39;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }}
    .stRadio label p {{
        color: {text_color_cream} !important;
        font-size: 18px !important;
        font-weight: 700 !important;
    }}
    
    /* Menü Kartları */
    .menu-card {{ 
        background-color: {card_bg_color}; 
        padding: 20px; 
        border-radius: 20px; 
        text-align: center; 
        border: 4px solid #3e7a39; 
        cursor: pointer; 
        margin-bottom: 15px; 
        box-shadow: 0 6px 0px #1b3a1a; 
    }}
    .menu-title {{ 
        font-size: 18px; 
        font-weight: 900; 
        color: {text_color_cream}; 
        text-transform: uppercase; 
    }}
    
    /* BUTONLAR */
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
    .sema-hoca-wrapper {{
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: rgba(0,0,0,0.5); /* Hafif karartma */
        z-index: 99998;
        display: flex; justify-content: center; align-items: center;
    }}
    
    .sema-hoca-box {{
        background-color: {red_warning_color};
        padding: 40px;
        border-radius: 20px;
        border: 8px solid white;
        text-align: center;
        box-shadow: 0 0 100px rgba(0,0,0,0.9);
        animation: shake 0.5s;
        z-index: 99999;
    }}
    
    @keyframes shake {{ 0% {{ transform: rotate(0deg); }} 25% {{ transform: rotate(5deg); }} 50% {{ transform: rotate(0eg); }} 75% {{ transform: rotate(-5deg); }} 100% {{ transform: rotate(0deg); }} }}

    /* Özür Dilerim Butonu */
    .ozur-btn-container button {{
        background-color: white !important;
        color: {red_warning_color} !important;
        border: 3px solid {red_warning_color} !important;
        margin-top: 20px;
        font-weight: bold;
    }}

    /* Okuma Köşesi Kartları */
    .bio-box {{ background-color: {card_bg_color}; color: {text_color_cream} !important; padding: 20px; border-radius: 15px; border-left: 8px solid #ffeb3b; margin-bottom: 20px; font-size: 16px; }}
    .bio-box b, .bio-box div, .bio-box span {{ color: {text_color_cream} !important; }}
    
    /* İsim Tabelası */
    .creator-name {{ background-color: {card_bg_color}; color: #ffeb3b !important; text-align: center; padding: 10px; font-weight: 900; font-size: 20px; border-radius: 15px; margin-bottom: 20px; border: 3px solid #3e7a39; box-shadow: 0 8px 0px rgba(0,0,0,0.4); text-transform: uppercase; }}
    
    /* Mobil Skor */
    .mobile-score {{ background-color: {card_bg_color}; padding: 10px; border-radius: 15px; border: 3px solid #3e7a39; text-align: center; margin-bottom: 15px; display: flex; justify-content: space-around; font-weight: bold; font-size: 18px; color: {text_color_cream} !important; }}
    .mobile-score span {{ color: {text_color_cream} !important; }}
    
    .sanat-aciklama {{ background-color: {card_bg_color}; color: {text_color_cream} !important; border-left: 6px solid #ffeb3b; padding: 20px; margin-top: 20px; font-size: 18px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    .sanat-aciklama div, .sanat-aciklama b {{ color: {text_color_cream} !important; }}
    
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
            st.markdown(f'<img src="data:image/jpg;base64,{img_data}" width="120" style="border-radius:10px; border:2px solid #3e7a39;">', unsafe_allow_html=True)
        else:
            st.info("Logo")
            
    with col_title:
        st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
        # BAŞLIK DA ARTIK KOYU ZEMİN ÜSTÜNDE KREM YAZI
        st.markdown(f'<h1 style="background-color:{card_bg_color}; padding:10px; border-radius:15px; border:3px solid #3e7a39; color:{text_color_cream} !important; font-weight:900; text-align:center;">EDEBİYAT<br>LİGİ</h1>', unsafe_allow_html=True)
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
    st.markdown(f"""<div class="menu-card" style="background-color:{card_bg_color}; border-color:#ffeb3b;"><div style="font-size:40px;">🎅🏻 🌨️ 🎄</div><div class="menu-title" style="color:#ffeb3b;">KIŞ OKUMA KÖŞESİ</div><div style="font-size:12px; color:{text_color_cream};">Ansiklopedi & Bilgi</div></div>""", unsafe_allow_html=True)
    if st.button("OKUMA KÖŞESİNE GİR ☕", use_container_width=True):
        st.session_state.page = "STUDY"
        st.rerun()

# --- STUDY SAYFASI ---
elif st.session_state.page == "STUDY":
    st.markdown(f"<h1 style='color:#ffeb3b; font-weight:900; text-align:center; background-color:{card_bg_color}; padding:10px; border-radius:15px;'>🎅🏻 OKUMA KÖŞESİ 🎄</h1>", unsafe_allow_html=True)
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
        st.markdown(f"<h4 style='color:{text_color_cream}'>📚 Eserleri ve Önemli Notlar</h4>", unsafe_allow_html=True)
        for eser, ozet in bilgi['eserler'].items():
            with st.expander(f"📖 {eser}"):
                st.markdown(f"<span style='color:{text_color_cream};'>{ozet}</span>", unsafe_allow_html=True)
        if st.button("LİSTEYİ KAPAT / TEMİZLE"):
            st.session_state.calisma_yazar = None
            st.rerun()

# --- GAME SAYFASI ---
elif st.session_state.page == "GAME":
    soru = st.session_state.mevcut_soru
    level = (st.session_state.soru_sayisi // 5) + 1
    
    # SEMA HOCA UYARISI
    if st.session_state.sema_hoca_kizdi:
        # Arka planı hafif karartmak için wrapper
        st.markdown('<div class="sema-hoca-wrapper">', unsafe_allow_html=True)
        
        # Kutu içeriği
        st.markdown("""
            <div class="sema-hoca-box">
                <div style="font-size: 60px;">😡</div>
                <div style="font-weight:900; font-size: 30px; color: white;">SEMA HOCAN<br>ÇOK KIZDI!</div>
                <div style="font-size:20px; color:#ffeaa7; margin-top:10px;">Nasıl Bilemezsin?!</div>
                <div class="ozur-btn-container">
        """, unsafe_allow_html=True)
        
        # Butonu Streamlit oluşturur, biz CSS ile kutu içine taşırız
        if st.button("Özür Dilerim 😔"):
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
        
        st.markdown('</div></div></div>', unsafe_allow_html=True) # Divleri kapat
    
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

    st.markdown(f"<div class='mobile-score'><span style='color:{text_color_cream};'>⭐ Lv {level}</span><span style='color:#aed581;'>💎 {st.session_state.xp} XP</span></div>", unsafe_allow_html=True)
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
        
    st.markdown(f"""<div class="question-card"><div style="color:{text_color_cream}; font-weight:bold; font-size:16px;">{title_text}</div><div style="font-size:22px; font-weight:900; color:#ffeb3b; margin: 15px 0; padding:10px; background:#3e7a39; border-radius:10px;">{content_text}</div><div style="font-size:18px; font-weight:bold; color:{text_color_cream};">{sub_text}</div></div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        cevap = st.radio("Seçim:", soru['siklar'], label_visibility="collapsed", disabled=st.session_state.soru_bitti)
    with col2:
        st.write("") 
        st.write("")
        
        if not st.session_state.soru_bitti:
            if st.button("YANITLA 🚀", type="primary", use_container_width=True):
                st.session_state.cevap_verildi = True
                
                if cevap == soru['dogru_cevap']:
                    st.session_state.xp += 100
                    st.markdown(get_audio_html("dogru"), unsafe_allow_html=True)
                    st.success("MÜKEMMEL! +100 XP 🎯")
                    st.balloons()
                    
                    if st.session_state.kategori == "ROMAN_OZET" and "eser_adi" in soru:
                        st.info(f"✅ Romanın Adı: **{soru['eser_adi']}**")

                    if st.session_state.kategori == "SANATLAR":
                        if "aciklama" in soru:
                            st.markdown(f"""<div class="sanat-aciklama"><b>💡 HOCA NOTU:</b><br>{soru['aciklama']}</div>""", unsafe_allow_html=True)
                        st.session_state.soru_bitti = True
                        st.rerun()
                    
                    else:
                        time.sleep(2.0)
                        st.session_state.soru_sayisi += 1
                        st.session_state.soru_bitti = False
                        st.session_state.cevap_verildi = False
                        st.session_state.mevcut_soru = yeni_soru_uret()
                        st.rerun()

                else: # YANLIŞ CEVAP
                    st.markdown(get_audio_html("yanlis"), unsafe_allow_html=True)
                    st.session_state.sema_hoca_kizdi = True
                    
                    msg = f"YANLIŞ! Doğru Cevap: {soru['dogru_cevap']} 💔"
                    if st.session_state.kategori == "ROMAN_OZET" and "eser_adi" in soru:
                        msg += f" (Eser: {soru['eser_adi']})"
                    
                    st.error(msg)
                    st.session_state.xp = max(0, st.session_state.xp - 20)
                    
                    if st.session_state.kategori == "SANATLAR":
                        st.session_state.soru_bitti = True
                    
                    st.rerun()
        
        elif st.session_state.soru_bitti and not st.session_state.sema_hoca_kizdi:
            if "aciklama" in soru:
                st.markdown(f"""<div class="sanat-aciklama"><b>💡 HOCA NOTU:</b><br>{soru['aciklama']}</div>""", unsafe_allow_html=True)
                
            if st.button("SIRADAKİ SORUYA GEÇ ➡️", type="primary", use_container_width=True, key="next_btn"):
                st.session_state.soru_sayisi += 1
                st.session_state.soru_bitti = False
                st.session_state.cevap_verildi = False
                st.session_state.mevcut_soru = yeni_soru_uret()
                st.rerun()