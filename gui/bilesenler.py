"""Birçok yerde kullanılan küçük arayüz parçaları."""

from PySide6.QtCore import QEvent, QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QComboBox, QFrame, QLabel, QPushButton

from .tema import BAGLANTI, GIRIS_ZEMIN, KESIK_CIZGI, SOLUK_YAZI


def dugme(metin, tur="ikincil"):
    """Şablondaki hap biçimli düğme. tur: ana, ikincil ya da cerceve."""
    d = QPushButton(metin)
    d.setProperty("tur", tur)
    d.setCursor(Qt.PointingHandCursor)
    return d


def etiket(metin, ad="etiket"):
    e = QLabel(metin)
    e.setObjectName(ad)
    return e


class Secim(QComboBox):
    """Açılır liste; sağına küçük bir aşağı ok çizer."""

    def paintEvent(self, olay):
        super().paintEvent(olay)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(SOLUK_YAZI), 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        x, y = self.width() - 20, self.height() / 2
        p.drawPolyline([QPointF(x - 4, y - 2), QPointF(x, y + 2), QPointF(x + 4, y - 2)])


class KesikCerceve(QFrame):
    """Kesik çizgili, köşeleri yuvarlak alan (bırakma alanları için)."""

    def __init__(self, yaricap=26, zemin=None):
        super().__init__()
        self.yaricap = yaricap
        self.zemin = zemin
        self.vurgulu = False  # üstüne dosya sürüklenirken True

    def paintEvent(self, olay):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        kalem = QPen(QColor(BAGLANTI if self.vurgulu else KESIK_CIZGI), 2)
        kalem.setDashPattern([3, 3])
        p.setPen(kalem)
        zemin = GIRIS_ZEMIN if self.vurgulu else self.zemin
        p.setBrush(QColor(zemin) if zemin else Qt.NoBrush)
        p.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), self.yaricap, self.yaricap)


class KisaltilanEtiket(QLabel):
    """Sığmayan metnin sonunu '…' ile kısaltır; tam metin ipucunda görünür."""

    def __init__(self, metin):
        super().__init__()
        self.tam_metin = metin
        self.setToolTip(metin)
        self.setMinimumWidth(60)

    def sizeHint(self):
        olcu = self.fontMetrics()
        return QSize(olcu.horizontalAdvance(self.tam_metin) + 2, olcu.height()).grownBy(self.contentsMargins())

    def changeEvent(self, olay):
        super().changeEvent(olay)
        # Stil metni yazı tipini değiştirince genişliği yeniden hesaplat
        if olay.type() in (QEvent.FontChange, QEvent.StyleChange):
            self.updateGeometry()

    def minimumSizeHint(self):
        boyut = self.sizeHint()
        boyut.setWidth(60)
        return boyut

    def resizeEvent(self, olay):
        super().resizeEvent(olay)
        self.setText(self.fontMetrics().elidedText(self.tam_metin, Qt.ElideMiddle, self.width()))
