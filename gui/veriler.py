"""Arayüzde kullanılan sabit bilgiler: e-okuyucular, hedef formatlar, desteklenen dosyalar."""

from pathlib import Path


# E-okuyucu ekran çözünürlükleri (genişlik, yükseklik) — kapak bu boyuta getirilir
E_OKUYUCULAR = {
    "Kobo Clara": (1072, 1448),
    "Kobo Libra": (1264, 1680),
    "Kindle Paperwhite": (1236, 1648),
    "Kindle": (1072, 1448),
    "PocketBook": (1264, 1680),
}
TOPLU_HEDEFLER = ["EPUB", "PDF", "MOBI", "AZW3", "DOCX"]

# Her kaynak türü için satırdaki "neye çevrilsin" seçenekleri
HEDEFLER = {
    "PDF": ["→ EPUB", "→ MOBI", "→ AZW3", "→ DOCX"],
    "EPUB": ["EPUB kalsın, kapağı düzelt", "EPUB kalsın, sadece kapak", "→ PDF", "→ MOBI", "→ AZW3"],
    "MOBI": ["→ EPUB", "→ AZW3", "→ PDF"],
    "AZW3": ["→ EPUB", "→ MOBI", "→ PDF"],
    "DOCX": ["→ PDF", "→ EPUB"],
}

# EPUB eklenince kapak durumuna göre önceden seçilen hedef
KAPAGA_GORE_HEDEF = {
    "var": "EPUB kalsın, kapağı düzelt",
    "yok": "EPUB kalsın, sadece kapak",
}

# EPUB'u EPUB olarak bırakıp yalnızca kapağını işleyen hedefler
KAPAK_HEDEFLERI = set(KAPAGA_GORE_HEDEF.values())


def hedef_uzantisi(hedef):
    """'→ PDF' → '.pdf'; başka biçimdeki hedefler için None."""
    return "." + hedef[2:].strip().lower() if hedef.startswith("→ ") else None

# EPUB satırının altındaki bağlantı (tıklayınca kapak penceresi açılır)
KAPAGA_GORE_BAGLANTI = {
    "var": "Kapağa bak",
    "yok": "+ Kapak ekle",
}

# Listeye eklenebilen dosya uzantıları
DESTEKLENEN_UZANTILAR = {"." + tur.lower() for tur in HEDEFLER}
DOSYA_SUZGECI = "Kitaplar ve belgeler (" + " ".join(f"*{u}" for u in sorted(DESTEKLENEN_UZANTILAR)) + ")"


def desteklenen_dosyalar(yollar):
    """Yollardan yalnızca var olan ve desteklenen uzantıdaki dosyaları döndürür."""
    return [y for y in yollar if Path(y).is_file() and Path(y).suffix.lower() in DESTEKLENEN_UZANTILAR]
