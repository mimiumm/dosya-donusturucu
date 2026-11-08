"""Dosyaların sürüklenip bırakıldığı ya da seçildiği alan."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QVBoxLayout

from .bilesenler import KesikCerceve, dugme, etiket
from .simgeler import YuklemeSimgesi
from .tema import UST_YUKSEKLIK
from .veriler import desteklenen_dosyalar


class BirakmaAlani(KesikCerceve):
    """Dosya bırakma alanı. Bırakılan desteklenen dosyaları sinyalle bildirir."""

    dosyalar_birakildi = Signal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setFixedHeight(UST_YUKSEKLIK)
        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(24, 20, 24, 20)
        duzen.setSpacing(10)
        duzen.addStretch()
        duzen.addWidget(YuklemeSimgesi(), alignment=Qt.AlignHCenter)
        duzen.addSpacing(10)
        duzen.addWidget(etiket("Dosyalarını buraya bırak", "birakBasligi"), alignment=Qt.AlignHCenter)
        duzen.addWidget(etiket("PDF, EPUB, MOBI, AZW3, DOCX ve daha fazlası"), alignment=Qt.AlignHCenter)
        duzen.addSpacing(6)
        self.dosya_sec = dugme("Dosya seç")
        self.dosya_sec.setMinimumWidth(114)
        self.dosya_sec.setMinimumHeight(44)
        duzen.addWidget(self.dosya_sec, alignment=Qt.AlignHCenter)
        duzen.addStretch()

    @staticmethod
    def _yollar(olay):
        return desteklenen_dosyalar(u.toLocalFile() for u in olay.mimeData().urls() if u.isLocalFile())

    def _vurgula(self, acik):
        self.vurgulu = acik
        self.update()

    def dragEnterEvent(self, olay):
        if olay.mimeData().hasUrls() and self._yollar(olay):
            olay.acceptProposedAction()
            self._vurgula(True)
        else:
            olay.ignore()

    def dragLeaveEvent(self, olay):
        self._vurgula(False)

    def dropEvent(self, olay):
        self._vurgula(False)
        yollar = self._yollar(olay)
        if yollar:
            olay.acceptProposedAction()
            self.dosyalar_birakildi.emit(yollar)
