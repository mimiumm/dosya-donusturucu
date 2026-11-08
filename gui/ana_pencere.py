"""Uygulamanın ana penceresi: bölümleri bir araya getirir ve düğmeleri bağlar."""

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QMainWindow, QVBoxLayout, QWidget

from .ayarlar_karti import AyarlarKarti
from .bilesenler import dugme
from .birakma_alani import BirakmaAlani
from .donusturme import DonusturmeIsi
from .dosya_listesi import DosyaListesiKarti
from .simgeler import AyDugmesi, Logo
from .veriler import DOSYA_SUZGECI, E_OKUYUCULAR, desteklenen_dosyalar


class AnaPencere(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dosya Dönüştürücü")
        self.resize(960, 860)

        kok = QWidget()
        kok.setObjectName("kok")
        self.setCentralWidget(kok)

        self.duzen = QVBoxLayout(kok)
        self.duzen.setContentsMargins(32, 28, 32, 28)
        self.duzen.setSpacing(20)
        self.duzen.addLayout(self._baslik_olustur())

        ust = QHBoxLayout()
        ust.setSpacing(20)
        self.birakma_alani = BirakmaAlani()
        self.ayarlar = AyarlarKarti()
        ust.addWidget(self.birakma_alani, 1)
        ust.addWidget(self.ayarlar)
        self.duzen.addLayout(ust)

        self.dosya_listesi = DosyaListesiKarti()
        self.duzen.addWidget(self.dosya_listesi, 1)

        alt = QHBoxLayout()
        alt.setSpacing(12)
        alt.addStretch()
        self.listeyi_temizle = dugme("Listeyi temizle", "cerceve")
        self.donustur = dugme("Dönüştür", "ana")
        for d in (self.listeyi_temizle, self.donustur):
            d.setMinimumWidth(140)
            d.setStyleSheet("font-size: 16px; min-height: 48px; border-radius: 24px; padding: 0 28px;")
            alt.addWidget(d)
        self.duzen.addLayout(alt)

        self._son_klasor = str(Path.home())
        self.birakma_alani.dosya_sec.clicked.connect(self.dosya_sec)
        self.birakma_alani.dosyalar_birakildi.connect(self.dosya_listesi.dosyalari_ekle)
        self.listeyi_temizle.clicked.connect(self.dosya_listesi.temizle)
        self.donustur.clicked.connect(self.donusturmeyi_baslat)
        self._is = None  # çalışan DonusturmeIsi

    # --- Dönüştür ---

    def donusturmeyi_baslat(self):
        """Sırada ya da hatalı satırları arka planda dönüştürür; orijinal dosyalara dokunulmaz."""
        if self._is is not None:
            return
        isler = []
        self._satirlar = {}  # anahtar → satır
        for satir in self.dosya_listesi.satirlar_listesi():
            if satir.durum not in ("sirada", "hata", "desteklenmiyor"):
                continue  # bitmiş satırlar yeniden yapılmaz
            is_ = satir.donusturme_isi()
            if is_ is None:
                satir.durum_ayarla("desteklenmiyor")
                continue
            anahtar = id(satir)
            self._satirlar[anahtar] = satir
            isler.append((anahtar, is_))
            satir.kuyruga_al()
        if not isler:
            return

        self._basarili = 0
        self._cikti_klasoru = self.ayarlar.kayit_klasoru
        boyut = E_OKUYUCULAR.get(self.ayarlar.e_okuyucu.currentText(), (1072, 1448))
        self._is = DonusturmeIsi(isler, self._cikti_klasoru, boyut, parent=self)
        self._is.basladi.connect(lambda a: self._satirlar[a].durum_ayarla("calisiyor"))
        self._is.bitti.connect(self._satir_bitti)
        self._is.hata_oldu.connect(lambda a, mesaj: self._satirlar[a].durum_ayarla("hata", mesaj=mesaj))
        self._is.finished.connect(self._donusturme_bitti)
        self._calisiyor_gorunumu(True)
        self._is.start()

    def _satir_bitti(self, anahtar, yol):
        self._basarili += 1
        self._satirlar[anahtar].durum_ayarla("bitti", cikti=yol)

    def _donusturme_bitti(self):
        self._is.deleteLater()
        self._is = None
        # Durdurulduysa başlamamış satırlar yeniden açılsın
        for satir in self._satirlar.values():
            if satir.durum == "sirada":
                satir.durum_ayarla("sirada")
        self._calisiyor_gorunumu(False)
        if self._basarili and self.ayarlar.klasoru_ac.isChecked():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._cikti_klasoru)))

    def _calisiyor_gorunumu(self, calisiyor):
        for parca in (self.donustur, self.listeyi_temizle, self.ayarlar.degistir, self.ayarlar.e_okuyucu):
            parca.setEnabled(not calisiyor)
        self.donustur.setText("Dönüştürülüyor…" if calisiyor else "Dönüştür")

    def closeEvent(self, olay):
        # Çalışırken kapanırsa: elindeki kitabı bitirsin (yarım dosya kalmasın), sıradakilere başlamasın
        if self._is is not None:
            self._is.durdur()
            self._is.wait()
        super().closeEvent(olay)

    def dosya_sec(self):
        yollar, _ = QFileDialog.getOpenFileNames(self, "Dosya seç", self._son_klasor, DOSYA_SUZGECI)
        if yollar:
            self._son_klasor = str(Path(yollar[0]).parent)
            self.dosya_listesi.dosyalari_ekle(desteklenen_dosyalar(yollar))

    def _baslik_olustur(self):
        satir = QHBoxLayout()
        satir.setSpacing(22)
        satir.addWidget(Logo(), alignment=Qt.AlignTop)

        yazilar = QVBoxLayout()
        yazilar.setSpacing(2)
        baslik = QLabel("Dosya Dönüştürücü")
        baslik.setObjectName("baslik")
        alt = QLabel("Dosyanı bırak, neye çevrileceğini seç")
        alt.setObjectName("altBaslik")
        yazilar.addWidget(baslik)
        yazilar.addWidget(alt)
        satir.addLayout(yazilar)

        satir.addStretch()
        satir.addWidget(AyDugmesi(), alignment=Qt.AlignTop)
        return satir
