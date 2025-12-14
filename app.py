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

# --- SES ÇALMA FONKSİYONU ---
def get_audio_html(sound_type):
    if sound_type == "dogru":
        audio_url = "https://cdn.pixabay.com/audio/2021/08/04/audio_bb630cc098.mp3"
    else:
        audio_url = "https://cdn.pixabay.com/audio/2021/08/04/audio_88447e769f.mp3"
    return f"""<audio autoplay="true" style="display:none;"><source src="{audio_url}" type="audio/mp3"></audio>"""

# ======================================================
# 1. DETAYLANDIRILMIŞ OKUMA KÖŞESİ VERİTABANI (YENİ!)
# ======================================================
@st.cache_data
def get_reading_db():
    return {
        "Orhan Veli Kanık": {
            "bio": "Garip (I. Yeni) akımının kurucusudur. Şiirden ölçüyü, kafiyeyi ve edebi sanatları atarak 'Sokağı şiire taşıyan adam' olmuştur. Sıradan insanı (Süleyman Efendi) konu edinir. İroni ve mizahı silah olarak kullanır.",
            "eserler": {
                "İstanbul'u Dinliyorum": """
                <b>📝 Analiz:</b> Şairin İstanbul'a olan tutkusunu, sesler ve imgeler üzerinden anlattığı serbest nazım şaheseridir. Garip akımının kurallarını biraz esnettiği, lirizmin baskın olduğu bir şiirdir.<br><br>
                <b>🎓 Sınav Notu:</b> ÖSYM bu şiiri sever! Genellikle 'İmgelerin gerçekçi kullanımı' veya 'İstanbul sevgisi' sorularında paragraf içinde verilir.<br><br>
                <b>❝ Alıntı: ❞</b><br><i>'İstanbul'u dinliyorum, gözlerim kapalı / Önce hafiften bir rüzgar esiyor...'</i>
                """,
                "Kitabe-i Seng-i Mezar": """
                <b>📝 Analiz:</b> Sıradan bir vatandaş olan 'Süleyman Efendi'nin nasırını şiire sokarak Divan edebiyatındaki 'Yüce Sevgili' anlayışını yerle bir etmiştir.<br><br>
                <b>🎓 Sınav Notu:</b> 2010 ve 2017 LYS'de Garip akımının özellikleri sorulurken bu şiir örnek gösterildi. 'Nasır' kelimesi anahtar kelimedir.
                """
            }
        },
        "Ahmet Hamdi Tanpınar": {
            "bio": "Şiirde sembolist, romanda realisttir. 'Rüya', 'Zaman' ve 'Bilinçaltı' kavramları onun kilit taşlarıdır. Bergson felsefesinden etkilenmiştir. 'Ne içindeyim zamanın, ne de büsbütün dışında' dizesi hayat felsefesidir.",
            "eserler": {
                "Huzur": """
                <b>📝 Analiz:</b> Mümtaz ve Nuran aşkı çerçevesinde Doğu-Batı çatışması, eski musiki ve İstanbul kültürü işlenir. II. Dünya Savaşı'nın yaklaşan ayak sesleri huzursuzluk yaratır.<br><br>
                <b>🎓 Sınav Notu:</b> AYT Edebiyat'ın vazgeçilmezidir! Karakterler (Mümtaz, Nuran, Suat) mutlaka bilinmeli. 'Bilinç akışı' tekniğinin uygulandığı ilk başarılı örneklerdendir.<br><br>
                <b>❝ Alıntı: ❞</b><br><i>'Fakat ne kadar inkar ederse etsin, Nuran'ı seviyordu.'</i>
                """,
                "Beş Şehir": """
                <b>📝 Analiz:</b> Ankara, Erzurum, Konya, Bursa ve İstanbul'u anlattığı deneme türünün zirvesidir. Şehirlerin ruhunu ve tarihini şiirsel bir dille anlatır.<br><br>
                <b>🎓 Sınav Notu:</b> Deneme türü sorulduğunda akla gelmesi gereken ilk eserdir.
                """
            }
        },
        "Cahit Sıtkı Tarancı": {
            "bio": "'Ölüm Şairi' olarak bilinir ama aslında yaşama sevincini kaybetmekten korktuğu için ölümü yazar. Sembolizm akımından etkilenmiştir. Biçim mükemmelliğine önem verir.",
            "eserler": {
                "Otuz Beş Yaş": """
                <b>📝 Analiz:</b> İnsanın ömrünün geçiciliğini ve ölüm korkusunu Dante'ye atıf yaparak (Yolun yarısı) anlatır.<br><br>
                <b>🎓 Sınav Notu:</b> Şiirde ahenk ve redif/kafiye sorularında teknik analiz için sıkça kullanılır. 'Dante gibi ortasındayız ömrün' dizesi çok meşhurdur.<br><br>
                <b>❝ Alıntı: ❞</b><br><i>'Yaş otuz beş! Yolun yarısı eder. / Dante gibi ortasındayız ömrün.'</i>
                """,
                "Desem Ki": """
                <b>📝 Analiz:</b> Romantik ve lirik bir aşk şiiridir. Renk imgeleriyle doludur.
                """
            }
        },
        "Yakup Kadri Karaosmanoğlu": {
            "bio": "Fecri Ati'den gelip Milli Edebiyat'ın en güçlü romancısı olmuştur. 'Nehir Roman' (birbirinin devamı olan romanlar) tekniğiyle Tanzimat'tan 1950'lere kadar Türk toplumunun değişimini anlatır.",
            "eserler": {
                "Yaban": """
                <b>📝 Analiz:</b> Kurtuluş Savaşı'nda bir Anadolu köyüne giden Ahmet Celal'in (aydın), köylülerle yaşadığı doku uyuşmazlığını anlatır. Köylü onu 'Yaban' olarak görür.<br><br>
                <b>🎓 Sınav Notu:</b> AYT'de en çok sorulan romanlardan biridir. Tezli Roman özelliği taşır. Aydın-Halk çatışması sorulursa cevap %90 Yaban'dır.
                """,
                "Kiralık Konak": """
                <b>📝 Analiz:</b> Naim Efendi (Gelenek), Servet Bey (Yozlaşmış Batılı), Seniha (Köklerinden kopuk gençlik) üzerinden kuşak çatışmasını anlatır.
                """
            }
        },
        "Oğuz Atay": {
            "bio": "Türk edebiyatında Postmodernizmin öncüsüdür. İroni, parodi, bilinç akışı gibi teknikleri ilk ve en iyi kullananlardandır. 'Tutunamayanlar' ile aydın bunalımını işlemiştir.",
            "eserler": {
                "Tutunamayanlar": """
                <b>📝 Analiz:</b> Turgut Özben'in, intihar eden arkadaşı Selim Işık'ın izini sürmesini anlatır. Klasik roman kurgusunu yıkan, ansiklopedik bilgiler ve oyunlarla dolu bir eserdir.<br><br>
                <b>🎓 Sınav Notu:</b> 'Bilinç akışı', 'İç monolog' veya 'Postmodernizm' sorulursa cevap budur. Olric karakteri (hayali arkadaş) sorularda ipucudur.<br><br>
                <b>❝ Alıntı: ❞</b><br><i>'Beni hemen anlamalısın, çünkü ben kitap değilim, çünkü ben öldükten sonra kimse beni okuyamaz.'</i>
                """
            }
        },
        "Namık Kemal": {
            "bio": "Vatan Şairidir. Sanat toplum içindir anlayışını benimser. Tiyatroyu 'faydalı bir eğlence' olarak görür. Romantizm akımından etkilenmiştir.",
            "eserler": {
                "İntibah": """
                <b>📝 Analiz:</b> İlk edebi romandır. Ali Bey'in Mahpeyker'e (kötü kadın) aşık olup Dilaşub'u (iyi cariye) harcamasını ve çöküşünü anlatır.<br><br>
                <b>🎓 Sınav Notu:</b> 'İlkler' sorusunda mutlaka çıkar. Mahpeyker ve Dilaşub karakterleri anahtar kelimedir.
                """,
                "Vatan Yahut Silistre": """
                <b>📝 Analiz:</b> Sahnelenen ilk tiyatrodur. Eser sahnelendikten sonra halk galeyana gelmiş, Namık Kemal sürgüne gönderilmiştir. İslam Bey ve Zekiye'nin vatan aşkı anlatılır.
                """
            }
        },
        "Fuzuli": {
            "bio": "16. yy. Divan şairi. Aşkı, ızdırabı ve tasavvufu işler. 'İlimsiz şiir, temelsiz duvar gibidir' der. Azeri Türkçesi kullanır.",
            "eserler": {
                "Leyla ile Mecnun": """
                <b>📝 Analiz:</b> Beşeri aşktan ilahi aşka geçişi anlatan, Türk edebiyatının en lirik mesnevisidir.<br><br>
                <b>🎓 Sınav Notu:</b> Mesnevi türünün zirvesidir. Alegorik (sembolik) anlatım vardır.
                """,
                "Şikayetname": """
                <b>📝 Analiz:</b> Kanuni'nin bağladığı maaşı alamayınca yazdığı, bürokrasiyi ve rüşveti eleştiren süslü nesir örneğidir.<br><br>
                <b>❝ Alıntı: ❞</b><br><i>'Selam verdim rüşvet değildir deyü almadılar.'</i>
                """
            }
        },
        "Sait Faik Abasıyanık": {
            "bio": "Çehov (Durum) hikayesinin edebiyatımızdaki en büyük ismidir. İstanbul, Burgazada, deniz, balıkçılar ve küçük insanlar ana temasıdır. 'Bir insanı sevmekle başlar her şey' sözüyle bilinir.",
            "eserler": {
                "Alemdağ'da Var Bir Yılan": """
                <b>📝 Analiz:</b> Yazarın son dönem eseridir. Gerçeküstücülüğe (Sürrealizm) kaydığı, yalnızlığı ve yabancılaşmayı anlattığı hikayelerdir.<br><br>
                <b>🎓 Sınav Notu:</b> Sait Faik'in çizgisini değiştirdiği eser olarak sorulur. 'Panco' karakteri önemlidir.
                """
            }
        }
    }

# ======================================================
# 2. OYUN VERİTABANLARI (Öncekiyle Aynı Kalıp Genişletildi)
# ======================================================
@st.cache_data
def get_game_db(kategori):
    if kategori == "CUMHURİYET":
        return {
            "Ömer Seyfettin": {"Hikaye": ["Kaşağı", "Ant", "Falaka", "Pembe İncili Kaftan", "Bomba", "Yüksek Ökçeler", "Gizli Mabed", "Başını Vermeyen Şehit", "Perili Köşk", "Bahar ve Kelebekler"], "Roman": ["Efruz Bey", "Yalnız Efe"]},
            "Ziya Gökalp": {"Şiir": ["Kızıl Elma", "Altın Işık", "Yeni Hayat"], "Fikir": ["Türkçülüğün Esasları", "Türkleşmek İslamlaşmak Muasırlaşmak"]},
            "Yakup Kadri Karaosmanoğlu": {"Roman": ["Yaban", "Kiralık Konak", "Sodom ve Gomore", "Nur Baba", "Ankara", "Panorama", "Bir Sürgün", "Hep O Şarkı"], "Anı": ["Zoraki Diplomat", "Anamın Kitabı", "Gençlik ve Edebiyat Hatıraları"]},
            "Halide Edip Adıvar": {"Roman": ["Sinekli Bakkal", "Ateşten Gömlek", "Vurun Kahpeye", "Handan", "Tatarcık", "Yolpalas Cinayeti", "Kalp Ağrısı", "Zeyno'nun Oğlu"], "Anı": ["Mor Salkımlı Ev", "Türk'ün Ateşle İmtihanı"]},
            "Reşat Nuri Güntekin": {"Roman": ["Çalıkuşu", "Yaprak Dökümü", "Yeşil Gece", "Acımak", "Miskinler Tekkesi", "Dudaktan Kalbe", "Akşam Güneşi", "Kavak Yelleri", "Damga"]},
            "Peyami Safa": {"Roman": ["Dokuzuncu Hariciye Koğuşu", "Fatih-Harbiye", "Yalnızız", "Matmazel Noraliya'nın Koltuğu", "Bir Tereddüdün Romanı", "Sözde Kızlar", "Mahşer"]},
            "Tarık Buğra": {"Roman": ["Küçük Ağa", "Osmancık", "İbişin Rüyası", "Firavun İmanı", "Yağmur Beklerken", "Dönemeçte", "Gençliğim Eyvah"]},
            "Sait Faik Abasıyanık": {"Hikaye": ["Semaver", "Sarnıç", "Lüzumsuz Adam", "Son Kuşlar", "Alemdağ'da Var Bir Yılan", "Şahmerdan", "Mahalle Kahvesi", "Havada Bulut"]},
            "Sabahattin Ali": {"Roman": ["Kürk Mantolu Madonna", "Kuyucaklı Yusuf", "İçimizdeki Şeytan"], "Hikaye": ["Değirmen", "Kağnı", "Ses", "Yeni Dünya", "Sırça Köşk"]},
            "Ahmet Hamdi Tanpınar": {"Roman": ["Huzur", "Saatleri Ayarlama Enstitüsü", "Sahnenin Dışındakiler", "Mahur Beste", "Aydaki Kadın"], "Deneme": ["Beş Şehir", "Yaşadığım Gibi"]},
            "Necip Fazıl Kısakürek": {"Şiir": ["Çile", "Kaldırımlar", "Örümcek Ağı", "Ben ve Ötesi"], "Tiyatro": ["Bir Adam Yaratmak", "Reis Bey", "Tohum", "Para", "Sabır Taşı"]},
            "Nazım Hikmet": {"Şiir": ["Memleketimden İnsan Manzaraları", "Kuvayi Milliye Destanı", "Simavne Kadısı Oğlu Bedreddin", "835 Satır", "Jokond ile Si-Ya-U"]},
            "Yaşar Kemal": {"Roman": ["İnce Memed", "Yer Demir Gök Bakır", "Ağrı Dağı Efsanesi", "Yılanı Öldürseler", "Orta Direk", "Teneke", "Demirciler Çarşısı Cinayeti", "Binboğalar Efsanesi"]},
            "Orhan Pamuk": {"Roman": ["Kara Kitap", "Benim Adım Kırmızı", "Masumiyet Müzesi", "Cevdet Bey ve Oğulları", "Sessiz Ev", "Kar", "Beyaz Kale", "Yeni Hayat"]},
            "Oğuz Atay": {"Roman": ["Tutunamayanlar", "Tehlikeli Oyunlar", "Bir Bilim Adamının Romanı"], "Hikaye": ["Korkuyu Beklerken"]},
            "Attila İlhan": {"Şiir": ["Ben Sana Mecburum", "Sisler Bulvarı", "Duvar", "Yağmur Kaçağı", "Elde Var Hüzün"], "Roman": ["Kurtlar Sofrası", "Sokaktaki Adam", "Bıçağın Ucu"]},
            "Cemal Süreya": {"Şiir": ["Üvercinka", "Sevda Sözleri", "Göçebe", "Beni Öp Sonra Doğur Beni", "Uçurumda Açan"]},
            "Adalet Ağaoğlu": {"Roman": ["Ölmeye Yatmak", "Bir Düğün Gecesi", "Fikrimin İnce Gülü", "Yüksek Gerilim", "Ruh Üşümesi"]},
            "Orhan Kemal": {"Roman": ["Bereketli Topraklar Üzerinde", "Murtaza", "Eskici ve Oğulları", "Hanımın Çiftliği", "Cemile", "Baba Evi", "Avare Yıllar", "Gurbet Kuşları"]},
            "Kemal Tahir": {"Roman": ["Devlet Ana", "Yorgun Savaşçı", "Esir Şehrin İnsanları", "Rahmet Yolları Kesti", "Köyün Kamburu", "Yol Ayrımı", "Kurt Kanunu"]},
            "Refik Halit Karay": {"Hikaye": ["Memleket Hikayeleri", "Gurbet Hikayeleri"], "Roman": ["Sürgün", "Bugünün Saraylısı", "Yezidin Kızı", "Nilgün", "Çete"]},
            "Mehmet Akif Ersoy": {"Şiir": ["Safahat (Külliyat)"]},
            "Yahya Kemal Beyatlı": {"Şiir": ["Kendi Gök Kubbemiz", "Eski Şiirin Rüzgarıyla"], "Nesir": ["Aziz İstanbul", "Eğil Dağlar"]},
            "Faruk Nafiz Çamlıbel": {"Şiir": ["Han Duvarları", "Çoban Çeşmesi", "Dinle Neyden", "Gönülden Gönüle"], "Tiyatro": ["Akın", "Canavar", "Yayla Kartalı"]},
            "Memduh Şevket Esendal": {"Roman": ["Ayaşlı ve Kiracıları", "Vassaf Bey"], "Hikaye": ["Otlakçı", "Mendil Altında", "Temiz Sevgiler"]},
            "Orhan Veli Kanık": {"Şiir": ["Garip", "Vazgeçemediğim", "Destan Gibi", "Yenisi", "Karşı"]},
            "Cahit Sıtkı Tarancı": {"Şiir": ["Otuz Beş Yaş", "Düşten Güzel", "Ömrümde Sükut"]},
            "Ahmet Muhip Dıranas": {"Şiir": ["Fahriye Abla", "Serenad", "Olvido", "Kar"], "Tiyatro": ["Gölgeler", "O Böyle İstemezdi"]},
            "Ziya Osman Saba": {"Şiir": ["Sebil ve Güvercinler", "Geçen Zaman", "Nefes Almak"], "Hikaye": ["Mesut İnsanlar Fotoğrafhanesi", "Değişen İstanbul"]},
            "Arif Damar": {"Şiir": ["Günden Güne", "İstanbul Bulutu", "Kedi Aklı", "Saat Sekizi Geç Vurdu"]},
            "Ferit Edgü": {"Roman": ["Hakkari'de Bir Mevsim (O)", "Kimse"], "Hikaye": ["Bir Gemide", "Çığlık", "Doğu Öyküleri"]},
            "Enis Behiç Koryürek": {"Şiir": ["Miras", "Güneşin Ölümü"], "Destan": ["Gemiciler"]},
            "Behçet Necatigil": {"Şiir": ["Kapalı Çarşı", "Evler", "Çevre", "Divançe", "Eski Toprak"]},
            "Hilmi Yavuz": {"Şiir": ["Bakış Kuşu", "Bedreddin Üzerine Şiirler", "Doğu Şiirleri", "Gizemli Şiirler"]},
            "Cahit Külebi": {"Şiir": ["Adamın Biri", "Rüzgar", "Atatürk Kurtuluş Savaşı'nda", "Yeşeren Otlar"]},
            "Fazıl Hüsnü Dağlarca": {"Şiir": ["Havaya Çizilen Dünya", "Çocuk ve Allah", "Üç Şehitler Destanı", "Çakırın Destanı"]},
            "Salah Birsel": {"Deneme": ["Kahveler Kitabı", "Ah Beyoğlu Vah Beyoğlu", "Boğaziçi Şıngır Mıngır"], "Şiir": ["Dünya İşleri"]},
            "Oktay Rifat": {"Şiir": ["Perçemli Sokak", "Karga ile Tilki", "Aşık Merdiveni", "Elleri Var Özgürlüğün"]},
            "Melih Cevdet Anday": {"Şiir": ["Rahatı Kaçan Ağaç", "Kolları Bağlı Odysseus", "Telgrafhane", "Teknenin Ölümü"]},
            "Yusuf Atılgan": {"Roman": ["Aylak Adam", "Anayurt Oteli", "Canistan"]},
            "Haldun Taner": {"Tiyatro": ["Keşanlı Ali Destanı", "Gözlerimi Kaparım Vazifemi Yaparım"], "Hikaye": ["Şişhaneye Yağmur Yağıyordu", "On İkiye Bir Var", "Yalıda Sabah"]},
            "Sezai Karakoç": {"Şiir": ["Monna Rosa", "Körfez", "Hızırla Kırk Saat", "Şahdamar", "Taha'nın Kitabı"]},
            "Turgut Uyar": {"Şiir": ["Göğe Bakma Durağı", "Dünyanın En Güzel Arabistanı", "Tütünler Islak", "Divan"]},
            "Edip Cansever": {"Şiir": ["Yerçekimli Karanfil", "Masa Da Masaymış", "İkindi Üstü", "Dirlik Düzenlik"]},
            "Ece Ayhan": {"Şiir": ["Bakışsız Bir Kedi Kara", "Yort Savul", "Kinar Hanımın Denizleri", "Devlet ve Tabiat"]},
            "Falih Rıfkı Atay": {"Anı": ["Çankaya", "Zeytindağı"], "Gezi": ["Deniz Aşırı", "Taymis Kıyıları", "Tuna Kıyıları"]},
            "Nurullah Ataç": {"Deneme": ["Günlerin Getirdiği", "Karalama Defteri", "Sözden Söze", "Okuruma Mektuplar"]},
            "Ahmet Kutsi Tecer": {"Şiir": ["Orada Bir Köy Var Uzakta"], "Tiyatro": ["Koçyiğit Köroğlu", "Köşebaşı", "Satılık Ev"]},
            "Fakir Baykurt": {"Roman": ["Yılanların Öcü", "Kaplumbağalar", "Tırpan", "Irazca'nın Dirliği"]},
            "Latife Tekin": {"Roman": ["Sevgili Arsız Ölüm", "Berci Kristin Çöp Masalları", "Gece Dersleri"]}
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
        {"yazar": "Namık Kemal", "roman": "İntibah", "ozet": "Ali Bey, mirasyedi bir gençtir. Mahpeyker adlı hafif meşrep bir kadına aşık olur. Annesi onu kurtarmak için Dilaşub'u alır. Mahpeyker intikam planları yapar."},
        {"yazar": "Recaizade Mahmut Ekrem", "roman": "Araba Sevdası", "ozet": "Bihruz Bey, alafrangalık özentisi, mirasyedi bir gençtir. Periveş adlı kadını soylu sanır. Araba tutkusu ve yanlış batılılaşma mizahi dille anlatılır."},
        {"yazar": "Halit Ziya Uşaklıgil", "roman": "Mai ve Siyah", "ozet": "Ahmet Cemil'in şair olma hayalleri (Mai) ile hayatın acı gerçekleri (Siyah) arasındaki çatışma. Servet-i Fünun neslinin karamsarlığını yansıtır."},
        {"yazar": "Halit Ziya Uşaklıgil", "roman": "Aşk-ı Memnu", "ozet": "Adnan Bey ile evlenen Bihter'in, Adnan Bey'in yeğeni Behlül ile yaşadığı yasak aşk. Firdevs Hanım, Nihal ve Beşir diğer önemli karakterlerdir."},
        {"yazar": "Mehmet Rauf", "roman": "Eylül", "ozet": "Suat, Süreyya ve Necip arasındaki yasak aşkı anlatan, olaydan çok psikolojik tahlillere dayanan ilk psikolojik romanımızdır."},
        {"yazar": "Yakup Kadri Karaosmanoğlu", "roman": "Yaban", "ozet": "Ahmet Celal, Kurtuluş Savaşı'nda kolunu kaybedip bir Anadolu köyüne yerleşir. Köylü onu düşman ve 'Yaban' olarak görür. Aydın-Halk çatışması işlenir."},
        {"yazar": "Reşat Nuri Güntekin", "roman": "Çalıkuşu", "ozet": "Feride, Kamran'a küsüp Anadolu'da öğretmenlik yapar. İdealist öğretmen tipinin en güzel örneğidir."},
        {"yazar": "Peyami Safa", "roman": "Dokuzuncu Hariciye Koğuşu", "ozet": "Hasta bir çocuğun bacağındaki kemik veremi yüzünden çektiği acılar ve Nüzhet'e duyduğu platonik aşk. Psikolojik tahliller yoğundur."},
        {"yazar": "Ahmet Hamdi Tanpınar", "roman": "Saatleri Ayarlama Enstitüsü", "ozet": "Hayri İrdal, Halit Ayarcı ve Muvakkit Nuri Efendi karakterleri üzerinden Türk toplumunun modernleşme süreci ve bürokrasi ironik bir dille eleştirilir."},
        {"yazar": "Oğuz Atay", "roman": "Tutunamayanlar", "ozet": "Turgut Özben, intihar eden arkadaşı Selim Işık'ın izini sürer. Küçük burjuva aydınının dramını, bilinç akışı ve ironiyle anlatan postmodern bir eserdir."},
        {"yazar": "Orhan Pamuk", "roman": "Kara Kitap", "ozet": "Avukat Galip, kayıp karısı Rüya'yı ve gazeteci Celal'i İstanbul sokaklarında arar. Şeyh Galip'in Hüsn ü Aşk'ına göndermeler vardır."},
        {"yazar": "Yaşar Kemal", "roman": "İnce Memed", "ozet": "Abdi Ağa'nın zulmüne başkaldıran Memed'in dağa çıkıp eşkıya olmasını ve köylü haklarını savunmasını anlatan destansı roman."},
        {"yazar": "Sabahattin Ali", "roman": "Kürk Mantolu Madonna", "ozet": "Raif Efendi'nin gençliğinde Almanya'da Maria Puder ile yaşadığı hüzünlü aşk ve sonrasında içine kapanışı anlatılır."},
        {"yazar": "Yusuf Atılgan", "roman": "Anayurt Oteli", "ozet": "Manisa'daki Anayurt Oteli'nin katibi Zebercet'in, otelde bir gece kalan gizemli kadını beklemesi ve giderek delirmesi anlatılır."},
        {"yazar": "Adalet Ağaoğlu", "roman": "Ölmeye Yatmak", "ozet": "Doçent Aysel'in bir otel odasında intiharı düşünürken, Cumhuriyet dönemi eğitimini ve geçmişini sorgulamasını anlatır."},
        {"yazar": "Ferit Edgü", "roman": "Hakkari'de Bir Mevsim", "ozet": "Sürgün bir öğretmenin (O), Hakkari'nin karlı dağlarındaki Pirkanis köyünde yaşadığı yalnızlığı, çaresizliği ve köylülerle iletişimini anlatır."},
        {"yazar": "Kemal Tahir", "roman": "Devlet Ana", "ozet": "Osmanlı'nın kuruluşunu, Ertuğrul Gazi, Osman Bey ve Şeyh Edebali üzerinden anlatan, Anadolu'nun Türkleşmesini işleyen tarihi roman."},
        {"yazar": "Tarık Buğra", "roman": "Küçük Ağa", "ozet": "İstanbullu Hoca'nın Kuvayi Milliye karşıtlığından, Akşehir'de bilinçlenerek Milli Mücadele'nin en büyük destekçisi 'Küçük Ağa'ya dönüşmesini anlatır."}
    ]

@st.cache_data
def get_sanatlar_db():
    return [
        {"sanat": "Teşbih (Benzetme)", "beyit": "Cennet gibi güzel vatanım...", "aciklama": "Vatan (Benzeyen), Cennet (Benzetilen), Gibi (Edat). Zayıf olan, güçlü olana benzetilmiş."},
        {"sanat": "İstiare (Eğretileme)", "beyit": "Şakaklarıma kar mı yağdı ne var?", "aciklama": "Beyaz saç (Benzeyen) söylenmemiş, sadece Kar (Benzetilen) söylenmiş. Bu bir 'Açık İstiare'dir."},
        {"sanat": "Tezat (Zıtlık)", "beyit": "Ağlarım hatıra geldikçe gülüştüklerimiz.", "aciklama": "'Ağlamak' ve 'Gülüşmek' zıt kavramlardır ve bir arada kullanılmıştır."},
        {"sanat": "Hüsnü Talil (Güzel Neden)", "beyit": "Güzel şeyler düşünelim diye / Yemyeşil oluvermiş ağaçlar", "aciklama": "Ağaçların yeşermesi doğal bir olaydır. Şair bunu 'biz güzel düşünelim diye' diyerek hayali ve güzel bir nedene bağlamış."},
        {"sanat": "Telmih (Hatırlatma)", "beyit": "Gökyüzünde İsa ile, Tur dağında Musa ile...", "aciklama": "Hz. İsa'nın göğe yükselmesi ve Hz. Musa'nın Tur dağındaki olayı hatırlatılmıştır."},
        {"sanat": "Tecahülü Arif (Bilmezlik)", "beyit": "Göz gördü gönül sevdi seni ey yüzü mahım / Kurbanın olam var mı benim bunda günahım?", "aciklama": "Şair aşık olduğunu bildiği halde, 'günahım var mı' diye sorarak bilmezlikten geliyor."},
        {"sanat": "Mübalağa (Abartma)", "beyit": "Bir ah çeksem dağı taşı eritir / Gözüm yaşı değirmeni yürütür", "aciklama": "Gözyaşıyla değirmen dönmesi imkansızdır, olay olduğundan çok abartılmıştır."},
        {"sanat": "İntak (Konuşturma)", "beyit": "Ben ki toz kanatlı bir kelebeğim / Minicik gövdeme yüklü Kafdağı", "aciklama": "Kelebek insan gibi konuşturulmuş (Ben... diyerek). İntak varsa orada mutlaka Teşhis de vardır."},
        {"sanat": "Tevriye (İki Anlamlılık)", "beyit": "Bu kadar letafet çünkü sende var / Beyaz gerdanında bir de ben gerek", "aciklama": "'Ben' kelimesi 1. Vücuttaki siyah nokta, 2. Şairin kendisi (Şahıs) anlamında kullanılmış. Yakın anlam söylenip uzak anlam kastedilmiş."},
        {"sanat": "İrsal-i Mesel", "beyit": "Balık baştan kokar bunu bilmemek / Seyrani gafilin ahmaklığıdır", "aciklama": "'Balık baştan kokar' atasözü şiirde kullanılarak düşünce kanıtlanmaya çalışılmış."},
        {"sanat": "Teşhis (Kişileştirme)", "beyit": "Haliç'te bir vapuru vurdular dört kişi / Demirlemişti eli kolu bağlıydı ağlıyordu", "aciklama": "Vapura 'ağlamak', 'eli kolu bağlı olmak' gibi insani özellikler verilmiş."}
    ]

# --- CSS VE TASARIM ---
oyun_deseni = "https://www.transparenttextures.com/patterns/cubes.png"
okuma_deseni = "https://www.transparenttextures.com/patterns/candy-cane.png"

# Hangi sayfadaysak ona göre arka plan belirle
if st.session_state.page == "STUDY":
    bg_style = f"background-color: #ffcccc; background-image: url('{okuma_deseni}');"
    sidebar_color = "#c0392b" # Kırmızı yan menü
else:
    bg_style = f"background: linear-gradient(135deg, #ff9ff3, #ff6b6b, #51cf66); background-image: linear-gradient(135deg, rgba(255,159,243,0.8), rgba(255,107,107,0.8), rgba(81,207,102,0.8)), url('{oyun_deseni}'); background-blend-mode: overlay; background-size: cover;"
    sidebar_color = "#2d3436"

st.markdown(f"""
    <style>
    .stApp {{
        {bg_style}
        background-attachment: fixed;
    }}
    
    html, body, p, div, label, h1, h2, h3, h4, h5, h6, li, span, b, i {{
        color: #000000 !important;
        font-family: 'Segoe UI', sans-serif;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {sidebar_color} !important;
        border-right: 4px solid #fff;
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    /* Sema Hoca Uyarı Kutusu (BÜYÜK VE KORKUTUCU) */
    .sema-hoca {{
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: #d63031;
        color: white !important;
        padding: 50px;
        border-radius: 20px;
        border: 10px solid white;
        z-index: 99999;
        font-size: 35px;
        font-weight: 900;
        text-align: center;
        box-shadow: 0 0 100px rgba(0,0,0,0.9);
        animation: shake 0.5s;
    }}
    
    @keyframes shake {{
      0% {{ transform: translate(-50%, -50%) rotate(0deg); }}
      25% {{ transform: translate(-50%, -50%) rotate(5deg); }}
      50% {{ transform: translate(-50%, -50%) rotate(0eg); }}
      75% {{ transform: translate(-50%, -50%) rotate(-5deg); }}
      100% {{ transform: translate(-50%, -50%) rotate(0deg); }}
    }}

    .sanat-aciklama {{
        background-color: #fff3cd;
        border-left: 6px solid #ffc107;
        padding: 20px;
        margin-top: 20px;
        font-size: 18px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    .menu-card {{
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        border: 4px solid #2d3436;
        cursor: pointer;
        transition: all 0.2s;
        margin-bottom: 15px;
        box-shadow: 0 6px 0px #d63031;
    }}
    .menu-card:hover {{
        transform: translateY(-5px);
        background-color: #ffffff;
    }}
    .menu-title {{
        font-size: 18px;
        font-weight: 900;
        color: #d63031;
        text-transform: uppercase;
    }}
    
    .stButton button {{
        background-color: #d63031 !important;
        color: white !important;
        border-radius: 15px !important;
        font-weight: 900 !important;
        border: 3px solid #000 !important;
        box-shadow: 0 5px 0 #000 !important;
    }}
    .stButton button:active {{
        box-shadow: 0 0 0 #000 !important;
        transform: translateY(5px);
    }}
    
    .question-card {{
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 25px;
        border: 4px solid #2d3436;
        box-shadow: 0 8px 0px #2d3436;
        text-align: center;
        margin-bottom: 25px;
    }}
    
    .stRadio {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 15px;
        border-radius: 20px;
        border: 3px solid #2d3436;
    }}
    
    .creator-name {{
        background-color: #2d3436;
        color: #00cec9 !important;
        text-align: center;
        padding: 10px;
        font-weight: 900;
        font-size: 20px;
        border-radius: 15px;
        letter-spacing: 2px;
        margin-bottom: 20px;
        border: 3px solid #fff;
        box-shadow: 0 8px 0px rgba(0,0,0,0.4);
        text-transform: uppercase;
    }}
    
    .study-title {{
        color: #c0392b !important;
        font-size: 30px;
        font-weight: 900;
        text-align: center;
        text-shadow: 2px 2px 0px white;
    }}
    
    .bio-box {{
        background-color: #ffeaa7;
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #fdcb6e;
        margin-bottom: 20px;
        font-size: 16px;
        line-height: 1.6;
    }}
    
    .kaydet-btn {{
        display: block;
        background-color: #00b894;
        color: white;
        padding: 12px;
        text-align: center;
        border-radius: 15px;
        text-decoration: none;
        font-weight: 900;
        font-size: 18px;
        border: 3px solid #006266;
        box-shadow: 0 4px 0 #006266;
        margin-top: 15px;
    }}
    
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
    </style>
    """, unsafe_allow_html=True)

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
        st.markdown("#### 📚 Eserleri ve Önemli Notlar")
        for eser, ozet in bilgi['eserler'].items():
            with st.expander(f"📖 {eser}"):
                st.markdown(ozet, unsafe_allow_html=True)

# --- GAME SAYFASI ---
elif st.session_state.page == "GAME":
    soru = st.session_state.mevcut_soru
    level = (st.session_state.soru_sayisi // 5) + 1
    
    # SEMA HOCA UYARISI
    if st.session_state.sema_hoca_kizdi:
        st.markdown("""
        <div class="sema-hoca">
            😡 SEMA HOCAN<br>ÇOK KIZDI!<br>
            <span style="font-size:20px; color:#ffeaa7;">Nasıl Bilemezsin?!</span>
        </div>
        """, unsafe_allow_html=True)
    
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
                st.markdown(get_audio_html("dogru"), unsafe_allow_html=True) # HIZLI SES
                st.success("MÜKEMMEL! +100 XP 🎯")
                st.balloons()
            else:
                st.markdown(get_audio_html("yanlis"), unsafe_allow_html=True) # HIZLI SES
                st.session_state.sema_hoca_kizdi = True
                st.error(f"YANLIŞ! Doğru Cevap: {soru['dogru_cevap']} 💔")
                st.session_state.xp = max(0, st.session_state.xp - 20)
            
            if st.session_state.kategori == "SANATLAR" and "aciklama" in soru:
                st.markdown(f"""<div class="sanat-aciklama"><b>💡 HOCA NOTU:</b><br>{soru['aciklama']}</div>""", unsafe_allow_html=True)
            if st.session_state.kategori == "ROMAN_OZET" and "eser_adi" in soru:
                st.info(f"Romanın Adı: **{soru['eser_adi']}**")

            st.session_state.soru_sayisi += 1
            st.session_state.cevap_verildi = True
            time.sleep(2)
            st.session_state.mevcut_soru = yeni_soru_uret()
            st.rerun()