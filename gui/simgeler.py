"""Kodla çizilen simgeler: logo, ay, yükleme, uyarı, resim."""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QPushButton, QWidget

from .tema import ANA_DUGME, BAGLANTI, SOLUK_YAZI, YAZI


def hilal_yolu(orta, r):
    """Ay simgesi için hilal biçimli yol."""
    tam = QPainterPath()
    tam.addEllipse(orta, r, r)
    kesik = QPainterPath()
    kesik.addEllipse(orta + QPointF(r * 0.53, -r * 0.47), r * 0.85, r * 0.85)
    return tam.subtracted(kesik)


class Logo(QWidget):
    """Pembe kare içinde gülen yüz."""

    def __init__(self, boyut=42):
        super().__init__()
        self.setFixedSize(boyut, boyut)

    def paintEvent(self, olay):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        b = self.width()
        p.setPen(Qt.NoPen)

        # Dış pembe kare ve içteki beyaz kare
        p.setBrush(QColor(ANA_DUGME))
        p.drawRoundedRect(QRectF(0, 0, b, b), b * 0.24, b * 0.24)
        ic = b * 0.17
        p.setBrush(QColor("#FFFFFF"))
        p.drawRoundedRect(QRectF(ic, ic, b - 2 * ic, b - 2 * ic), b * 0.14, b * 0.14)

        # Yanaklar
        p.setBrush(QColor("#F6C3DC"))
        p.drawEllipse(QPointF(b * 0.27, b * 0.62), b * 0.055, b * 0.055)
        p.drawEllipse(QPointF(b * 0.73, b * 0.62), b * 0.055, b * 0.055)

        # Gözler
        p.setBrush(QColor(YAZI))
        p.drawEllipse(QPointF(b * 0.36, b * 0.48), b * 0.06, b * 0.06)
        p.drawEllipse(QPointF(b * 0.64, b * 0.48), b * 0.06, b * 0.06)

        # Gülümseme
        kalem = QPen(QColor(YAZI), b * 0.045, Qt.SolidLine, Qt.RoundCap)
        p.setPen(kalem)
        p.setBrush(Qt.NoBrush)
        p.drawArc(QRectF(b * 0.42, b * 0.52, b * 0.16, b * 0.12), 200 * 16, 140 * 16)


class AyDugmesi(QPushButton):
    """Karanlık mod için yuvarlak ay düğmesi (şimdilik sadece görünüş)."""

    def __init__(self):
        super().__init__()
        self.setObjectName("ayDugmesi")
        self.setFixedSize(46, 46)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Karanlık mod")

    def paintEvent(self, olay):
        super().paintEvent(olay)  # yuvarlak zemin stil metninden gelir
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        orta = QPointF(self.width() / 2, self.height() / 2)
        p.setPen(QPen(QColor(SOLUK_YAZI), 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        p.drawPath(hilal_yolu(orta, 8.5))


class YuklemeSimgesi(QWidget):
    """Yukarı ok ve tepsi."""

    def __init__(self, boyut=34):
        super().__init__()
        self.setFixedSize(boyut, boyut)

    def paintEvent(self, olay):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        b = self.width()
        p.setPen(QPen(QColor(BAGLANTI), b * 0.09, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        # ok
        p.drawLine(QPointF(b * 0.5, b * 0.1), QPointF(b * 0.5, b * 0.62))
        p.drawPolyline([QPointF(b * 0.3, b * 0.3), QPointF(b * 0.5, b * 0.1), QPointF(b * 0.7, b * 0.3)])
        # tepsi
        tepsi = QPainterPath(QPointF(b * 0.1, b * 0.6))
        tepsi.lineTo(b * 0.1, b * 0.82)
        tepsi.quadTo(b * 0.1, b * 0.9, b * 0.18, b * 0.9)
        tepsi.lineTo(b * 0.82, b * 0.9)
        tepsi.quadTo(b * 0.9, b * 0.9, b * 0.9, b * 0.82)
        tepsi.lineTo(b * 0.9, b * 0.6)
        p.drawPath(tepsi)


class SeritSimgesi(QWidget):
    """Uyarı şeridinin başındaki simge: '!' daire ya da onay işareti."""

    def __init__(self, tur, renk):
        super().__init__()
        self.tur, self.renk = tur, renk
        self.setFixedSize(22, 22)

    def paintEvent(self, olay):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(self.renk), 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        if self.tur == "uyari":
            p.drawEllipse(QRectF(2, 2, 18, 18))
            p.drawLine(QPointF(11, 6.5), QPointF(11, 12))
            p.drawPoint(QPointF(11, 15.5))
        else:
            p.drawPolyline([QPointF(4, 11.5), QPointF(9, 16), QPointF(18, 6)])


class ResimSimgesi(QWidget):
    """Çerçeve içinde dağ ve güneş."""

    def __init__(self, boyut=30):
        super().__init__()
        self.setFixedSize(boyut, boyut)

    def paintEvent(self, olay):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        b = self.width()
        p.setPen(QPen(QColor(BAGLANTI), b * 0.08, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawRoundedRect(QRectF(b * 0.08, b * 0.08, b * 0.84, b * 0.84), b * 0.16, b * 0.16)
        p.drawEllipse(QPointF(b * 0.34, b * 0.34), b * 0.07, b * 0.07)
        p.drawPolyline([QPointF(b * 0.12, b * 0.84), QPointF(b * 0.62, b * 0.42), QPointF(b * 0.9, b * 0.68)])
