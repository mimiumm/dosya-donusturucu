"""Dönüştürmeyi arka planda, satır satır yapar; arayüz donmaz."""

from PySide6.QtCore import QThread, Signal

from converter.kapak import KapakHatasi, epub_kapakli_yaz
from converter.registry import DonusturmeHatasi, dosyaya_donustur


class DonusturmeIsi(QThread):
    """isler: [(anahtar, iş bilgisi)] — iş bilgisi DosyaSatiri.donusturme_isi() sonucudur
    ("kapak": EPUB kapağı işlenir, "donustur": PDF ↔ EPUB).

    Sinyaller ana iş parçacığına (arayüze) güvenle ulaşır.
    """

    basladi = Signal(object)            # anahtar
    bitti = Signal(object, str)         # anahtar, yazılan dosyanın yolu
    hata_oldu = Signal(object, str)     # anahtar, kullanıcıya gösterilecek mesaj

    def __init__(self, isler, hedef_klasor, boyut, parent=None):
        super().__init__(parent)
        self.isler = isler
        self.hedef_klasor = hedef_klasor
        self.boyut = boyut
        self._dur = False

    def durdur(self):
        """Elindeki kitabı bitirir, sıradakilere başlamaz."""
        self._dur = True

    def run(self):
        for anahtar, is_ in self.isler:
            if self._dur:
                return
            self.basladi.emit(anahtar)
            try:
                if is_["tur"] == "donustur":  # başka biçime (PDF ↔ EPUB)
                    yol = dosyaya_donustur(is_["kaynak"], self.hedef_klasor, is_["hedef_uzanti"])
                else:  # EPUB kalır, kapak işlenir
                    yol = epub_kapakli_yaz(
                        is_["kaynak"],
                        self.hedef_klasor,
                        self.boyut,
                        gorsel_yolu=is_["gorsel_yolu"],
                        sigdir=is_["sigdir"],
                        kitap_adi=is_["kitap_adi"],
                        yazar=is_["yazar"],
                    )
            except (KapakHatasi, DonusturmeHatasi) as hata:
                self.hata_oldu.emit(anahtar, str(hata))
            except Exception as hata:  # beklenmeyen bir şey olsa da diğer kitaplar devam etsin
                self.hata_oldu.emit(anahtar, f"Beklenmeyen hata: {hata}")
            else:
                self.bitti.emit(anahtar, str(yol))
