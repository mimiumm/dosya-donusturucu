"""Kitap ve kapak ayarları penceresi (kapak var / kapak yok)."""

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImageReader, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .bilesenler import KesikCerceve, dugme, etiket
from .simgeler import ResimSimgesi, SeritSimgesi, hilal_yolu
from .tema import GIRIS_ZEMIN, KAPAK_MOR, KENAR, TURUNCU_YAZI, YESIL_YAZI
from .veriler import E_OKUYUCULAR

# Kapak olarak seçilebilen resim türleri (Qt'nin açabildikleriyle sınırlı)
_YAYGIN_RESIMLER = ["png", "jpg", "jpeg", "webp", "gif", "bmp", "tif", "tiff"]
GORSEL_UZANTILARI = [
    u for u in _YAYGIN_RESIMLER if u.encode() in {bytes(f) for f in QImageReader.supportedImageFormats()}
]
GORSEL_SUZGECI = "Resimler (" + " ".join(f"*.{u}" for u in GORSEL_UZANTILARI) + ")"

# Kapağı olan kitapta, yeni görsel seçilmemişken sağdaki yazı
_KAPAK_NOTU = "Senin bir şey yapmana gerek yok. Kapağı değiştirmek istersen:"


def gorsel_mi(yol):
    return Path(yol).suffix.lower().lstrip(".") in GORSEL_UZANTILARI


def gorsel_yukle(yol):
    """Resmi açar (fotoğraflardaki döndürme bilgisine uyar); açılamazsa None."""
    okuyucu = QImageReader(str(yol))
    okuyucu.setAutoTransform(True)
    resim = okuyucu.read()
    return None if resim.isNull() else QPixmap.fromImage(resim)


class KapakOnizleme(QWidget):
    """Kitabın kapağı. Görsel verilmezse mor bir yer tutucu çizer.

    Doldur (varsayılan): kenarlar kırpılır. Sığdır: resim bütün görünür, kalan yer beyaz kalır.
    """

    def __init__(self, gorsel=None):
        super().__init__()
        self.gorsel = gorsel  # QPixmap ya da None
        self.sigdir = False
        self.setFixedSize(180, 244)

    def gorsel_ayarla(self, gorsel):
        self.gorsel = gorsel
        self.update()

    def sigdir_ayarla(self, sigdir):
        self.sigdir = sigdir
        self.update()

    def paintEvent(self, olay):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        alan = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        yol = QPainterPath()
        yol.addRoundedRect(alan, 12, 12)
        p.setClipPath(yol)
        if self.gorsel is not None and not self.gorsel.isNull():
            if self.sigdir:
                p.fillPath(yol, QColor("#FFFFFF"))
                kip = Qt.KeepAspectRatio
            else:
                kip = Qt.KeepAspectRatioByExpanding
            olcekli = self.gorsel.scaled(self.size(), kip, Qt.SmoothTransformation)
            x = (self.width() - olcekli.width()) / 2
            y = (self.height() - olcekli.height()) / 2
            p.drawPixmap(QPointF(x, y), olcekli)
            # İnce çerçeve: beyaz boşluk beyaz pencerede kaybolmasın
            p.setClipping(False)
            p.setPen(QPen(QColor(KENAR), 1))
            p.setBrush(Qt.NoBrush)
            p.drawPath(yol)
            return
        p.fillPath(yol, QColor(KAPAK_MOR))
        p.setPen(QPen(QColor("#FFFFFF"), 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPath(hilal_yolu(QPointF(self.width() / 2, self.height() / 2 - 26), 13))
        yazi = QFont(self.font())
        yazi.setPixelSize(15)
        yazi.setBold(True)
        p.setFont(yazi)
        p.drawText(QRectF(0, self.height() / 2, self.width(), 30), Qt.AlignCenter, "Kitabın kendi kapağı")


class KapakPenceresi(QDialog):
    """Kitap ve kapak ayarları. kapak_var=False → kullanıcı görsel seçer.

    Kaydet kitaba bir şey yazmaz; seçimler secimler() ile alınıp satırda hatırlanır.
    secimler: daha önce kaydedilmiş seçimler (pencere bunlarla açılır).
    """

    def __init__(self, dosya_adi, kapak_var, kitap_adi="", yazar="", e_okuyucu="Kobo Clara",
                 kapak_gorseli=None, secimler=None, parent=None):
        super().__init__(parent)
        self.setObjectName("kapakPenceresi")
        self.setWindowTitle(dosya_adi)
        self.setModal(True)
        self.setAcceptDrops(True)  # resim pencerenin her yerine bırakılabilir
        self.resize(760, 560)
        gen, yuk = E_OKUYUCULAR.get(e_okuyucu, (1072, 1448))
        self.secilen_gorsel_yolu = None  # kaydetme bağlanınca kullanılacak

        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(28, 22, 28, 24)
        duzen.setSpacing(18)

        # Başlık + kapatma
        ust = QHBoxLayout()
        ust.addWidget(etiket(dosya_adi, "pencereBasligi"))
        ust.addStretch()
        kapat = QPushButton("✕")
        kapat.setObjectName("sil")
        kapat.setFixedSize(30, 30)
        kapat.setCursor(Qt.PointingHandCursor)
        kapat.clicked.connect(self.reject)
        ust.addWidget(kapat)
        duzen.addLayout(ust)

        # Uyarı şeridi
        serit = QFrame()
        serit.setObjectName("seritYesil" if kapak_var else "seritTuruncu")
        serit_duzen = QHBoxLayout(serit)
        serit_duzen.setContentsMargins(16, 14, 16, 14)
        serit_duzen.setSpacing(12)
        if kapak_var:
            serit_duzen.addWidget(SeritSimgesi("onay", YESIL_YAZI))
            metin = "Bu kitabın kapağı var."
        else:
            serit_duzen.addWidget(SeritSimgesi("uyari", TURUNCU_YAZI))
            metin = "Bu kitabın kapağı yok. Bir görsel seç, kapak olsun."
        self.kapak_var = kapak_var
        self.serit_yazi = QLabel(metin)
        self.serit_yazi.setWordWrap(True)
        serit_duzen.addWidget(self.serit_yazi, 1)
        duzen.addWidget(serit)

        # Gövde: solda kapak, sağda alanlar
        govde = QHBoxLayout()
        govde.setSpacing(28)

        sol = QVBoxLayout()
        sol.setSpacing(12)
        self.onizleme = KapakOnizleme(kapak_gorseli)
        self.onizleme_notu = etiket(f"{e_okuyucu} ekranında böyle görünecek", "kucukNot")
        self.birak = None
        if kapak_var:
            sol.addWidget(self.onizleme)
            sol.addWidget(self.onizleme_notu, alignment=Qt.AlignHCenter)
        else:
            self.birak = KesikCerceve(yaricap=12, zemin=GIRIS_ZEMIN)
            self.birak.setFixedSize(180, 244)
            ic = QVBoxLayout(self.birak)
            ic.addStretch()
            ic.addWidget(ResimSimgesi(), alignment=Qt.AlignHCenter)
            ic.addSpacing(8)
            ic.addWidget(etiket("Görseli buraya bırak", "gorselBirak"), alignment=Qt.AlignHCenter)
            ic.addStretch()
            sol.addWidget(self.birak)
            # Görsel seçilince kesik çizgili alanın yerine önizleme gelir
            sol.addWidget(self.onizleme)
            sol.addWidget(self.onizleme_notu, alignment=Qt.AlignHCenter)
            self.onizleme.hide()
            self.onizleme_notu.hide()
            self.gorsel_sec = dugme("Görsel seç", "ana")
            self.gorsel_sec.setStyleSheet("min-height: 44px; border-radius: 22px;")
            self.gorsel_sec.clicked.connect(self.gorsel_sec_penceresi)
            sol.addWidget(self.gorsel_sec)
        sol.addStretch()
        govde.addLayout(sol)

        sag = QVBoxLayout()
        sag.setSpacing(8)
        alanlar = QGridLayout()
        alanlar.setHorizontalSpacing(14)
        alanlar.setVerticalSpacing(8)
        alanlar.addWidget(etiket("Kitap adı", "alanBasligi"), 0, 0)
        alanlar.addWidget(etiket("Yazar", "alanBasligi"), 0, 1)
        self.kitap_adi = QLineEdit(kitap_adi)
        self.kitap_adi.setPlaceholderText("Kitap adını yaz")
        self.yazar = QLineEdit(yazar)
        self.yazar.setPlaceholderText("Yazar adını yaz")
        for kutu in (self.kitap_adi, self.yazar):
            kutu.setAcceptDrops(False)  # bırakılan resim yol olarak yazılmasın, pencereye gitsin
        alanlar.addWidget(self.kitap_adi, 1, 0)
        alanlar.addWidget(self.yazar, 1, 1)
        sag.addLayout(alanlar)
        sag.addSpacing(14)

        sag.addWidget(etiket("Kapak ekrana tam oturmazsa" if kapak_var else "Görsel kapağa tam oturmazsa",
                             "alanBasligi"))
        segment = QFrame()
        segment.setObjectName("segment")
        seg_duzen = QHBoxLayout(segment)
        seg_duzen.setContentsMargins(4, 4, 4, 4)
        seg_duzen.setSpacing(4)
        self.oturtma = QButtonGroup(self)
        for i, yazi in enumerate(["Doldur (kenarlar kırpılır)", "Sığdır (boşluk kalır)"]):
            d = QPushButton(yazi)
            d.setObjectName("segmentDugme")
            d.setCheckable(True)
            d.setCursor(Qt.PointingHandCursor)
            d.setChecked(i == 0)
            self.oturtma.addButton(d, i)
            seg_duzen.addWidget(d)
        # 0 = Doldur, 1 = Sığdır
        self.oturtma.idToggled.connect(lambda kimlik, secili: secili and self.onizleme.sigdir_ayarla(kimlik == 1))
        sag.addWidget(segment, alignment=Qt.AlignLeft)
        sag.addSpacing(10)

        if kapak_var:
            self.kendi_kapagi = kapak_gorseli  # Temizle'ye basılınca bu geri gelir
            self.kapak_notu = etiket(_KAPAK_NOTU)
            self.kapak_notu.setWordWrap(True)
            sag.addWidget(self.kapak_notu)
            sag.addSpacing(6)
            dugmeler = QHBoxLayout()
            dugmeler.setSpacing(10)
            self.baska_gorsel = dugme("Başka görsel seç", "cerceve")
            self.baska_gorsel.clicked.connect(self.gorsel_sec_penceresi)
            self.temizle_dugmesi = dugme("Temizle", "cerceve")
            self.temizle_dugmesi.clicked.connect(self.temizle)
            self.temizle_dugmesi.hide()  # yalnızca yeni görsel seçilince görünür
            dugmeler.addWidget(self.baska_gorsel)
            dugmeler.addWidget(self.temizle_dugmesi)
            dugmeler.addStretch()
            sag.addLayout(dugmeler)
        else:
            not_ = etiket(f"Seçtiğin görsel otomatik olarak {e_okuyucu} boyutuna ({gen} × {yuk}) getirilir.")
            not_.setWordWrap(True)
            sag.addWidget(not_)
            sag.addSpacing(6)
            self.hepsine_kullan = QCheckBox("Bu görseli kapağı olmayan tüm kitaplara kullan")
            sag.addWidget(self.hepsine_kullan)
        # Açılamayan resim seçilince görünür
        self.gorsel_uyari = etiket("", "gorselUyari")
        self.gorsel_uyari.setWordWrap(True)
        self.gorsel_uyari.hide()
        sag.addSpacing(6)
        sag.addWidget(self.gorsel_uyari)
        sag.addStretch()
        govde.addLayout(sag, 1)
        duzen.addLayout(govde, 1)

        # Alt düğmeler
        alt = QHBoxLayout()
        alt.setSpacing(12)
        alt.addStretch()
        vazgec = dugme("Vazgeç", "cerceve")
        kaydet = dugme("Kaydet", "ana")
        for d in (vazgec, kaydet):
            d.setMinimumWidth(96)
            d.setStyleSheet("font-size: 16px; min-height: 46px; border-radius: 23px; padding: 0 24px;")
            alt.addWidget(d)
        vazgec.clicked.connect(self.reject)
        kaydet.clicked.connect(self.accept)  # seçimleri satır alır (secimler())
        duzen.addLayout(alt)

        if secimler:
            self._secimleri_geri_yukle(secimler)

    # --- Kaydedilen seçimler ---

    def secimler(self):
        """Kaydet'e basıldığında satırın hatırlayacağı seçimler."""
        return {
            "gorsel_yolu": self.secilen_gorsel_yolu,
            "sigdir": self.onizleme.sigdir,
            "kitap_adi": self.kitap_adi.text().strip(),
            "yazar": self.yazar.text().strip(),
        }

    def _secimleri_geri_yukle(self, secimler):
        self.kitap_adi.setText(secimler.get("kitap_adi", ""))
        self.yazar.setText(secimler.get("yazar", ""))
        self.oturtma.button(1 if secimler.get("sigdir") else 0).setChecked(True)
        if secimler.get("gorsel_yolu"):
            self.gorsel_ayarla(secimler["gorsel_yolu"])  # dosya silinmişse uyarı çıkar

    # --- Görsel seçme ---

    def gorsel_sec_penceresi(self):
        yol, _ = QFileDialog.getOpenFileName(self, "Görsel seç", str(Path.home()), GORSEL_SUZGECI)
        if yol:
            self.gorsel_ayarla(yol)

    def gorsel_ayarla(self, yol):
        """Seçilen ya da bırakılan resmi önizlemeye koyar. Açılamazsa uyarı gösterir, önizleme değişmez."""
        gorsel = gorsel_yukle(yol)
        if gorsel is None:
            self.gorsel_uyari.setText(f"Bu görsel açılamadı: {Path(yol).name}")
            self.gorsel_uyari.show()
            return False
        self.gorsel_uyari.hide()
        self.secilen_gorsel_yolu = str(yol)
        self.onizleme.gorsel_ayarla(gorsel)
        if self.kapak_var:
            self.serit_yazi.setText("Kapak seçtiğin görselle değiştirilecek.")
            self.kapak_notu.setText("Farklı bir görsel seçebilir ya da kitabın kendi kapağına dönebilirsin:")
            self.temizle_dugmesi.show()
        if self.birak is not None:
            self.birak.hide()
            self.onizleme.show()
            self.onizleme_notu.show()
            self.gorsel_sec.setText("Başka görsel seç")
        return True

    def temizle(self):
        """Seçilen görseli bırakır, kitabın kendi kapağına döner (yalnızca kapağı olan kitapta)."""
        self.secilen_gorsel_yolu = None
        self.onizleme.gorsel_ayarla(self.kendi_kapagi)
        self.gorsel_uyari.hide()
        self.serit_yazi.setText("Bu kitabın kapağı var.")
        self.kapak_notu.setText(_KAPAK_NOTU)
        self.temizle_dugmesi.hide()

    # --- Sürükle-bırak ---

    @staticmethod
    def _birakilan_gorsel(olay):
        for url in olay.mimeData().urls():
            if url.isLocalFile() and gorsel_mi(url.toLocalFile()):
                return url.toLocalFile()
        return None

    def _vurgula(self, acik):
        if self.birak is not None and self.birak.isVisible():
            self.birak.vurgulu = acik
            self.birak.update()

    def dragEnterEvent(self, olay):
        if olay.mimeData().hasUrls() and self._birakilan_gorsel(olay):
            olay.acceptProposedAction()
            self._vurgula(True)
        else:
            olay.ignore()

    def dragLeaveEvent(self, olay):
        self._vurgula(False)

    def dropEvent(self, olay):
        self._vurgula(False)
        yol = self._birakilan_gorsel(olay)
        if yol:
            olay.acceptProposedAction()
            self.gorsel_ayarla(yol)
