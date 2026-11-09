import os
from pathlib import Path

from .documents import pdf_to_epub, epub_to_pdf
from .yollar import benzersiz_yol

# "uyari": kayıplı dönüşümlerde kullanıcıya gösterilecek açıklama
CONVERTERS = {
    (".pdf", ".epub"): {
        "fn": pdf_to_epub,
        "quality": "lossy",
        "uyari": "Yalnızca yazılar aktarılır; resimler, tablolar ve sayfa düzeni kaybolur. "
                 "Her PDF sayfası ayrı bölüm olur.",
    },
    (".epub", ".pdf"): {"fn": epub_to_pdf, "quality": "good", "uyari": ""},
}


class DonusturmeHatasi(Exception):
    """Dönüştürme yapılamadığında; mesajı kullanıcıya gösterilebilir."""


def donusturucu(kaynak_uzanti, hedef_uzanti):
    """Bu iki uzantı arasında dönüştürücü varsa bilgisini, yoksa None döndürür."""
    return CONVERTERS.get((kaynak_uzanti.lower(), hedef_uzanti.lower()))


def kayipli_mi(kaynak_uzanti, hedef_uzanti):
    girdi = donusturucu(kaynak_uzanti, hedef_uzanti)
    return bool(girdi) and girdi["quality"] == "lossy"


def dosyaya_donustur(kaynak, hedef_klasor, hedef_uzanti, ad=None):
    """Kaynağı hedef_klasor'e yeni dosya olarak dönüştürür; orijinale dokunmaz. Yazılan yolu döndürür.

    ad verilmezse kaynağın adı kullanılır. Ad doluysa 'ad (2).uzantı' kullanılır.
    Önce geçici adla yazılır, bitince asıl ada taşınır.
    Hata olursa DonusturmeHatasi verir ve yarım dosya bırakmaz.
    """
    kaynak = Path(kaynak).resolve()
    girdi = donusturucu(kaynak.suffix, hedef_uzanti)
    if girdi is None:
        raise DonusturmeHatasi(f"Desteklenmeyen dönüşüm: {kaynak.suffix} → {hedef_uzanti}")
    hedef_klasor = Path(hedef_klasor)
    try:
        hedef_klasor.mkdir(parents=True, exist_ok=True)
    except OSError as hata:
        raise DonusturmeHatasi(f"Kayıt klasörü oluşturulamadı: {hata}") from hata
    hedef = benzersiz_yol(hedef_klasor, (ad or kaynak.stem) + hedef_uzanti.lower())
    if hedef.resolve() == kaynak:  # olmaz ama orijinalin üzerine asla yazılmasın
        raise DonusturmeHatasi("Hedef dosya orijinalle aynı.")
    gecici = hedef.with_name(f".{hedef.stem}.yaziliyor{hedef.suffix}")  # uzantı sonda kalsın
    try:
        girdi["fn"](str(kaynak), str(gecici))
        os.replace(gecici, hedef)
    except Exception as hata:  # kütüphaneler farklı hata türleri veriyor
        gecici.unlink(missing_ok=True)
        raise DonusturmeHatasi(f"Dönüştürülemedi: {hata}") from hata
    return hedef


def convert(src, dst):
    """Komut satırı (main.py) için; arayüzle aynı güvenli yolu kullanır. Yazılan yolu döndürür.

    dst doluysa üzerine yazılmaz, 'ad (2).uzantı' kullanılır. Hata olursa DonusturmeHatasi verir.
    """
    src, dst = Path(src), Path(dst)
    if kayipli_mi(src.suffix, dst.suffix):
        print("Uyarı: bu dönüşüm kayıplıdır. " + donusturucu(src.suffix, dst.suffix)["uyari"])
    return dosyaya_donustur(src, dst.parent, dst.suffix, ad=dst.stem)
