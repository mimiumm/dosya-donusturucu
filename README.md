# Dosya Dönüştürücü

🇹🇷 **Türkçe** | 🇬🇧 [English](README.en.md)

E-kitaplar için masaüstü dosya dönüştürücü. EPUB ve PDF dosyalarını birbirine çevirir, EPUB kitaplara e-okuyucunuzun ekranına uygun kapak ekler ya da mevcut kapağı düzeltir. PySide6 (Qt) ile yazılmıştır.

> ⚠️ **Geliştirme aşamasında.** Temel özellikler çalışıyor, eksik kısımlar güncellemelerle eklenecek. Arayüz şimdilik yalnızca Türkçe.

## Görünüm

Tasarım taslakları:

![Ana pencere](tasar%C4%B1m%20%C5%9Fablon/C%20%C2%B7%20Lavanta%20%28%C3%A7ok%20formatl%C4%B1%29%402x.png)

| Kapak yok → kullanıcı seçer | Kapak var → kalır, boyutu ayarlanır |
|---|---|
| ![Kapak yok](tasar%C4%B1m%20%C5%9Fablon/Durum%201%20%C2%B7%20Kapak%20yok%20%E2%86%92%20kullan%C4%B1c%C4%B1%20se%C3%A7er%402x.png) | ![Kapak var](tasar%C4%B1m%20%C5%9Fablon/Durum%202%20%C2%B7%20Kapak%20var%20%E2%86%92%20kal%C4%B1r%2C%20boyutu%20ayarlan%C4%B1r%402x.png) |

## Özellikler

- **EPUB kapak ekleme / düzeltme** — kapak, seçilen e-okuyucunun çözünürlüğüne getirilir (Kobo Clara, Kobo Libra, Kindle, Kindle Paperwhite, PocketBook). *Doldur* ve *Sığdır* seçenekleriyle önizleme.
- **Kitap adı ve yazar düzeltme** — kapak penceresinden.
- **EPUB → PDF**
- **PDF → EPUB** — kayıplıdır: yalnızca yazılar aktarılır, resimler ve sayfa düzeni kaybolur. Uygulama bunu "Kayıplı" etiketiyle gösterir.
- **Sürükle-bırak** ile dosya ekleme.
- **Orijinal dosyaya dokunmaz** — çıktı her zaman seçilen kayıt klasörüne yeni dosya olarak yazılır (varsayılan: `Belgeler/Kitaplar`). Aynı adlı dosya varsa `ad (2).epub` gibi yeni ad verilir.

## Kurulum

Python 3.10 veya üstü gerekir.

```bash
git clone https://github.com/mimiumm/dosya-donusturucu.git
cd dosya-donusturucu
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Kullanım

Arayüzü açmak için:

```bash
python gui_qt.py
```

Komut satırından tek dosya dönüştürmek için:

```bash
python main.py kitap.epub kitap.pdf
```

## Yol haritası

- [ ] MOBI, AZW3 ve DOCX desteği
- [ ] "Tümünü şuna çevir" (toplu hedef seçimi)
- [ ] İngilizce arayüz
- [ ] Koyu tema
- [ ] CBZ ve diğer formatlar
- [ ] Hazır paketler (PyInstaller)

## Lisans

[MIT](LICENSE)
