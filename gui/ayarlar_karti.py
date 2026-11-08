"""Sağ üstteki Ayarlar kartı: kayıt yeri, e-okuyucu, bitince klasörü aç."""

from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QCheckBox, QFileDialog, QFrame, QHBoxLayout, QLineEdit, QVBoxLayout

from .bilesenler import Secim, dugme, etiket
from .tema import UST_YUKSEKLIK
from .veriler import E_OKUYUCULAR


def varsayilan_kayit_klasoru():
    """Sistemin Belgeler klasörünün içinde 'Kitaplar' (henüz olmayabilir; Dönüştür'de oluşturulur)."""
    belgeler = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) or str(Path.home())
    return Path(belgeler) / "Kitaplar"


def kisa_yol(yol):
    """Ev klasörünü '~' ile gösterir: /home/ad/Belgeler/Kitaplar → ~/Belgeler/Kitaplar"""
    try:
        return "~/" + str(Path(yol).relative_to(Path.home()))
    except ValueError:
        return str(yol)


class AyarlarKarti(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("kart")
        self.setFixedWidth(300)
        self.setFixedHeight(UST_YUKSEKLIK)
        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(20, 20, 20, 20)
        duzen.setSpacing(8)

        duzen.addWidget(etiket("Ayarlar", "kartBasligi"))
        duzen.addSpacing(4)

        duzen.addWidget(etiket("Kayıt yeri"))
        yer = QHBoxLayout()
        yer.setSpacing(8)
        self.kayit_yeri = QLineEdit()
        self.kayit_yeri.setReadOnly(True)
        self.degistir = dugme("Değiştir")
        self.degistir.setStyleSheet("border-radius: 12px; padding: 0 12px; min-height: 40px;")
        self.degistir.clicked.connect(self.kayit_yeri_sec)
        yer.addWidget(self.kayit_yeri)
        yer.addWidget(self.degistir)
        duzen.addLayout(yer)
        duzen.addSpacing(4)
        self.kayit_klasoru_ayarla(varsayilan_kayit_klasoru())

        duzen.addWidget(etiket("E-okuyucum (kapak boyutu buna göre)"))
        self.e_okuyucu = Secim()
        self.e_okuyucu.addItems(E_OKUYUCULAR)
        duzen.addWidget(self.e_okuyucu)
        duzen.addSpacing(4)

        self.klasoru_ac = QCheckBox("Bitince klasörü aç")
        self.klasoru_ac.setChecked(True)
        duzen.addStretch()
        duzen.addWidget(self.klasoru_ac)

    def kayit_klasoru_ayarla(self, klasor):
        self.kayit_klasoru = Path(klasor)
        self.kayit_yeri.setText(kisa_yol(self.kayit_klasoru))
        self.kayit_yeri.setToolTip(str(self.kayit_klasoru))
        self.kayit_yeri.setCursorPosition(0)

    def kayit_yeri_sec(self):
        # Seçme penceresi, kayıt klasörünün var olan en yakın üst klasöründe açılır
        baslangic = self.kayit_klasoru
        while not baslangic.exists() and baslangic != baslangic.parent:
            baslangic = baslangic.parent
        klasor = QFileDialog.getExistingDirectory(self, "Kayıt yeri seç", str(baslangic))
        if klasor:
            self.kayit_klasoru_ayarla(klasor)
