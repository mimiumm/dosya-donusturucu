"""Uygulamayı kurar (tema, yazı tipi, renk paleti) ve ana pencereyi açar."""

import sys

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

from .ana_pencere import AnaPencere
from .tema import ARKA_PLAN, BAGLANTI, GIRIS_ZEMIN, STIL, YAZI, YAZI_TIPLERI


def uygulama_olustur():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")  # her sistemde aynı görünsün
    palet = app.palette()
    palet.setColor(QPalette.Window, QColor(ARKA_PLAN))
    palet.setColor(QPalette.Base, QColor(GIRIS_ZEMIN))
    palet.setColor(QPalette.Text, QColor(YAZI))
    palet.setColor(QPalette.WindowText, QColor(YAZI))
    palet.setColor(QPalette.ButtonText, QColor(YAZI))
    palet.setColor(QPalette.Highlight, QColor(BAGLANTI))
    palet.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palet)
    yazi = QFont()
    yazi.setFamilies(YAZI_TIPLERI)
    app.setFont(yazi)
    app.setStyleSheet(STIL)
    return app


def main():
    app = uygulama_olustur()
    pencere = AnaPencere()
    pencere.show()
    sys.exit(app.exec())
