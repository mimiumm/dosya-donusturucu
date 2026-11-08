"""Çıktı dosyası adları için ortak yardımcılar."""

from pathlib import Path


def benzersiz_yol(klasor, dosya_adi):
    """klasor/dosya_adi boşsa onu, doluysa 'ad (2).uzantı', 'ad (3).uzantı' … döndürür."""
    aday = Path(klasor) / dosya_adi
    kok, uzanti = aday.stem, aday.suffix
    n = 2
    while aday.exists():
        aday = Path(klasor) / f"{kok} ({n}){uzanti}"
        n += 1
    return aday
