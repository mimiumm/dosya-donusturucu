"""Lavanta teması: renkler, yazı tipleri ve uygulamanın stil metni (QSS)."""


# --- Renkler (Lavanta teması) ---
ARKA_PLAN = "#FAF3F9"
KART = "#FFFFFF"
KENAR = "#EEDBEA"
ANA_DUGME = "#E6B8E0"
IKINCIL_DUGME = "#F3E2F0"
YAZI = "#4A2D45"
SOLUK_YAZI = "#7D6478"
BAGLANTI = "#8E4A85"
YESIL_ZEMIN = "#E6F4EA"
YESIL_YAZI = "#2E5E3A"
TURUNCU_ZEMIN = "#FDF1E4"
TURUNCU_YAZI = "#7A3E10"
ILERLEME = "#CF8FC6"
KAPAK_MOR = "#8E6AA8"
KESIK_CIZGI = "#E3AED8"
GIRIS_ZEMIN = "#FFFAFE"
UST_YUKSEKLIK = 236  # bırakma alanı ve Ayarlar kartının yüksekliği


YAZI_TIPLERI = ["Nunito", "Quicksand", "Noto Sans", "Cantarell", "sans-serif"]

STIL = f"""
QWidget#kok {{
    background: {ARKA_PLAN};
}}
QWidget {{
    color: {YAZI};
    font-size: 14px;
}}
QLabel#baslik {{
    font-size: 26px;
    font-weight: 800;
}}
QLabel#altBaslik {{
    color: {SOLUK_YAZI};
    font-size: 14px;
}}
QPushButton#ayDugmesi {{
    background: {KART};
    border: 1px solid {KENAR};
    border-radius: 23px;
}}
QPushButton#ayDugmesi:hover {{
    background: {IKINCIL_DUGME};
}}

/* Kartlar */
QFrame#kart {{
    background: {KART};
    border: 1px solid {KENAR};
    border-radius: 22px;
}}
QLabel#kartBasligi {{
    font-size: 17px;
    font-weight: 800;
}}
QLabel#etiket {{
    color: {SOLUK_YAZI};
}}
QLabel#birakBasligi {{
    font-size: 17px;
    font-weight: 700;
}}

/* Düğmeler: tur = ana | ikincil | cerceve */
QPushButton[tur] {{
    border-radius: 21px;
    padding: 0 22px;
    min-height: 42px;
    font-weight: 700;
    color: {YAZI};
}}
QPushButton[tur="ana"] {{
    background: {ANA_DUGME};
    border: none;
}}
QPushButton[tur="ana"]:hover {{
    background: #DDA6D5;
}}
QPushButton[tur="ikincil"] {{
    background: {IKINCIL_DUGME};
    border: none;
}}
QPushButton[tur="ikincil"]:hover {{
    background: #ECD2E8;
}}
QPushButton[tur="cerceve"] {{
    background: {KART};
    border: 1px solid {KENAR};
}}
QPushButton[tur="cerceve"]:hover {{
    background: {ARKA_PLAN};
}}

/* Giriş kutuları */
QLineEdit, QComboBox {{
    background: {GIRIS_ZEMIN};
    border: 1px solid {KENAR};
    border-radius: 12px;
    padding: 8px 12px;
    min-height: 22px;
}}
QLineEdit:focus, QComboBox:focus {{
    border-color: {ANA_DUGME};
}}
QComboBox::drop-down {{
    border: none;
    width: 28px;
}}
QComboBox QAbstractItemView {{
    background: {KART};
    border: 1px solid {KENAR};
    selection-background-color: {IKINCIL_DUGME};
    selection-color: {YAZI};
    outline: none;
}}
QCheckBox {{
    spacing: 8px;
}}

/* Sıradaki dosyalar */
QLabel#sayac {{
    background: {IKINCIL_DUGME};
    border-radius: 10px;
    padding: 2px 9px;
    font-size: 13px;
    font-weight: 700;
}}
QComboBox#hapSecim {{
    background: {IKINCIL_DUGME};
    border: none;
    border-radius: 19px;
    padding: 8px 36px 8px 14px;
    font-size: 15px;
}}
QComboBox#hedefSecim {{
    background: {KART};
    border-radius: 19px;
    padding: 7px 30px 7px 14px;
}}
QScrollArea, QWidget#liste {{
    background: transparent;
    border: none;
}}
QLabel#rozet {{
    background: {IKINCIL_DUGME};
    border-radius: 12px;
    font-size: 11px;
    font-weight: 800;
}}
QLabel#dosyaAdi {{
    font-size: 16px;
    font-weight: 600;
}}
QPushButton#baglanti {{
    background: transparent;
    border: none;
    color: {BAGLANTI};
    padding: 0;
    text-align: left;
    font-size: 13px;
    text-decoration: underline;
}}
QPushButton#baglanti:hover {{
    color: {YAZI};
}}
QLabel#yesilEtiket, QLabel#turuncuEtiket, QLabel#griEtiket {{
    border-radius: 10px;
    padding: 3px 9px;
    font-size: 12px;
    font-weight: 700;
}}
QLabel#yesilEtiket {{
    background: {YESIL_ZEMIN};
    color: {YESIL_YAZI};
}}
QLabel#turuncuEtiket {{
    background: {TURUNCU_ZEMIN};
    color: {TURUNCU_YAZI};
}}
QLabel#griEtiket {{
    background: #F1ECF0;
    color: {SOLUK_YAZI};
    padding: 6px 13px;
    font-size: 13px;
    font-weight: 600;
}}
QProgressBar {{
    background: {IKINCIL_DUGME};
    border: none;
    border-radius: 5px;
    max-height: 10px;
    min-height: 10px;
}}
QProgressBar::chunk {{
    background: {ILERLEME};
    border-radius: 5px;
}}
QLabel#bosYazi {{
    color: {SOLUK_YAZI};
    font-size: 15px;
}}
/* Kapak penceresi */
QDialog#kapakPenceresi {{
    background: {KART};
}}
QLabel#pencereBasligi {{
    font-size: 20px;
    font-weight: 800;
}}
QFrame#seritTuruncu {{
    background: {TURUNCU_ZEMIN};
    border-radius: 16px;
}}
QFrame#seritYesil {{
    background: {YESIL_ZEMIN};
    border-radius: 16px;
}}
QFrame#seritTuruncu QLabel {{
    color: {TURUNCU_YAZI};
    font-size: 15px;
    font-weight: 700;
}}
QFrame#seritYesil QLabel {{
    color: {YESIL_YAZI};
    font-size: 15px;
    font-weight: 700;
}}
QLabel#alanBasligi {{
    font-weight: 700;
}}
QLabel#kucukNot {{
    color: {SOLUK_YAZI};
    font-size: 12px;
}}
QLabel#gorselUyari {{
    color: {TURUNCU_YAZI};
    font-size: 12px;
    font-weight: 700;
}}
QLabel#gorselBirak {{
    color: {SOLUK_YAZI};
    font-weight: 700;
}}
QFrame#segment {{
    background: {IKINCIL_DUGME};
    border-radius: 22px;
}}
QPushButton#segmentDugme {{
    background: transparent;
    border: none;
    border-radius: 18px;
    padding: 0 16px;
    min-height: 36px;
    font-weight: 700;
    color: {SOLUK_YAZI};
}}
QPushButton#segmentDugme:checked {{
    background: {ANA_DUGME};
    color: {YAZI};
}}
QLabel#yuzde {{
    color: {SOLUK_YAZI};
    font-weight: 600;
}}
QPushButton#sil {{
    background: transparent;
    border: none;
    border-radius: 14px;
    color: {SOLUK_YAZI};
    font-size: 17px;
}}
QPushButton#sil:hover {{
    background: {IKINCIL_DUGME};
    color: {YAZI};
}}
"""
