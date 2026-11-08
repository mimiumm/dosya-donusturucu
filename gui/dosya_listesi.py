"""'Sıradaki dosyalar' kartı ve listedeki her dosyanın satırı."""

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from converter.kapak import epub_bilgileri, epub_kapak_resmi
from converter.registry import donusturucu, kayipli_mi

from .bilesenler import KisaltilanEtiket, Secim, dugme, etiket
from .kapak_penceresi import KapakPenceresi
from .veriler import (
    HEDEFLER,
    KAPAGA_GORE_BAGLANTI,
    KAPAGA_GORE_HEDEF,
    KAPAK_HEDEFLERI,
    TOPLU_HEDEFLER,
    hedef_uzantisi,
)


class DosyaSatiri(QWidget):
    """Listede tek bir dosya: rozet, ad, kapak etiketi, hedef seçimi, durum ve sil."""

    def __init__(self, bilgi):
        super().__init__()
        self.bilgi = bilgi
        # Satır ezilmesin; liste karta sığmazsa kaydırılır
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        satir = QHBoxLayout(self)
        satir.setContentsMargins(0, 0, 0, 0)
        satir.setSpacing(12)

        rozet = etiket(bilgi["tur"], "rozet")
        rozet.setAlignment(Qt.AlignCenter)
        rozet.setFixedSize(46, 42)
        satir.addWidget(rozet)

        # Ad + kapak etiketi, altında bağlantı
        orta = QVBoxLayout()
        orta.setSpacing(2)
        ust = QHBoxLayout()
        ust.setSpacing(8)
        ad = KisaltilanEtiket(bilgi["ad"])
        ad.setObjectName("dosyaAdi")
        ust.addWidget(ad)  # yer daralırsa ad kısalır, etiket adın hemen yanında kalır
        self.kapak_etiketi = etiket("", "yesilEtiket")
        ust.addWidget(self.kapak_etiketi, alignment=Qt.AlignVCenter)
        # Seçili hedef kayıplıysa görünür (ör. PDF → EPUB); açıklaması ipucunda
        self.kayip_etiketi = etiket("!  Kayıplı", "turuncuEtiket")
        ust.addWidget(self.kayip_etiketi, alignment=Qt.AlignVCenter)
        ust.addStretch(1)
        orta.addLayout(ust)

        # Yalnızca kapağı kontrol edilebilen EPUB'larda görünür
        self.baglanti = QPushButton(bilgi.get("baglanti", ""))
        self.baglanti.setVisible(bool(bilgi.get("baglanti")))
        self.baglanti.setObjectName("baglanti")
        self.baglanti.setCursor(Qt.PointingHandCursor)
        yazi = self.baglanti.font()
        yazi.setUnderline(True)
        self.baglanti.setFont(yazi)
        self.baglanti.clicked.connect(self.kapak_penceresini_ac)
        orta.addWidget(self.baglanti, alignment=Qt.AlignLeft)
        satir.addLayout(orta, 1)
        self._kapak_gorunumunu_guncelle()

        self.hedef = Secim()
        self.hedef.setObjectName("hedefSecim")
        self.hedef.addItems(HEDEFLER.get(bilgi["tur"], []))
        if bilgi.get("hedef"):
            self.hedef.setCurrentText(bilgi["hedef"])
        satir.addWidget(self.hedef)

        # Durum: hepsi bir kez kurulur, durum_ayarla() hangisinin görüneceğini seçer
        self.durum_sirada = etiket("Sırada", "griEtiket")
        self.durum_cubuk = QProgressBar()
        self.durum_cubuk.setRange(0, 0)  # süresi bilinmiyor: dönen çubuk, uydurma yüzde yok
        self.durum_cubuk.setTextVisible(False)
        self.durum_cubuk.setFixedWidth(100)
        self.durum_cubuk.setToolTip("Dönüştürülüyor…")
        self.durum_bitti = etiket("✓  Bitti", "yesilEtiket")
        self.klasorde_goster = dugme("Klasörde göster")
        self.klasorde_goster.setStyleSheet("min-height: 32px; border-radius: 16px; padding: 0 12px; font-size: 13px;")
        self.klasorde_goster.clicked.connect(self._klasorde_goster)
        self.durum_hata = etiket("!  Hata", "turuncuEtiket")
        self.durum_desteklenmiyor = etiket("Henüz desteklenmiyor", "griEtiket")
        self.durum_desteklenmiyor.setToolTip("Bu hedef henüz yapılamıyor; şimdilik yalnızca 'EPUB kalsın' seçenekleri çalışıyor.")
        for parca in (self.durum_sirada, self.durum_cubuk, self.durum_bitti, self.klasorde_goster,
                      self.durum_hata, self.durum_desteklenmiyor):
            satir.addWidget(parca, alignment=Qt.AlignVCenter)
        self.durum = None
        self.cikti_yolu = None

        self.sil = QPushButton("✕")
        self.sil.setObjectName("sil")
        self.sil.setFixedSize(28, 28)
        self.sil.setCursor(Qt.PointingHandCursor)
        self.sil.setToolTip("Listeden çıkar")
        satir.addWidget(self.sil)

        self.durum_ayarla("sirada")
        self._kayip_guncelle()
        # Hedef değişince: kayıplı etiketi güncellenir; bitmiş ya da hatalı satır yeniden sıraya girer
        self.hedef.currentTextChanged.connect(lambda _: self._kayip_guncelle())
        self.hedef.currentTextChanged.connect(lambda _: self._siraya_al())


    def kapak_penceresini_ac(self):
        pencere = self.window()
        ayarlar = getattr(pencere, "ayarlar", None)
        e_okuyucu = ayarlar.e_okuyucu.currentText() if ayarlar else "Kobo Clara"
        b = self.bilgi
        kapak_var = b.get("kapak") == "var"

        # Kapak resmi yalnızca pencere açılınca okunur; açılamazsa önizlemede yer tutucu görünür
        kapak_gorseli = None
        if kapak_var and b.get("kapak_yolu"):
            veri = epub_kapak_resmi(b["yol"], b["kapak_yolu"])
            if veri:
                gorsel = QPixmap()
                if gorsel.loadFromData(veri):
                    kapak_gorseli = gorsel

        pencere_ = KapakPenceresi(
            b["ad"],
            kapak_var=kapak_var,
            kitap_adi=b.get("kitap_adi", ""),
            yazar=b.get("yazar", ""),
            e_okuyucu=e_okuyucu,
            kapak_gorseli=kapak_gorseli,
            secimler=b.get("secimler"),
            parent=pencere,
        )
        # Kaydet: seçimler yalnızca bu satır için hatırlanır, kitaba bir şey yazılmaz
        if pencere_.exec() == QDialog.Accepted:
            b["secimler"] = pencere_.secimler()
            self._kapak_gorunumunu_guncelle()
            self._siraya_al()

    # --- Durum ---

    def durum_ayarla(self, durum, mesaj="", cikti=None):
        """durum: "sirada", "calisiyor", "bitti", "hata" ya da "desteklenmiyor"."""
        self.durum = durum
        self.cikti_yolu = cikti
        self.durum_sirada.setVisible(durum == "sirada")
        self.durum_cubuk.setVisible(durum == "calisiyor")
        self.durum_bitti.setVisible(durum == "bitti")
        self.klasorde_goster.setVisible(durum == "bitti")
        self.durum_hata.setVisible(durum == "hata")
        self.durum_desteklenmiyor.setVisible(durum == "desteklenmiyor")
        self.durum_hata.setToolTip(mesaj)
        ipucu = str(cikti) if cikti else ""
        if cikti and self._kayip_uyarisi():
            ipucu += f"\nKayıplı dönüştürüldü: {self._kayip_uyarisi()}"
        self.durum_bitti.setToolTip(ipucu)
        # Çalışırken satır değiştirilemez
        calisiyor = durum == "calisiyor"
        for parca in (self.sil, self.baglanti, self.hedef):
            parca.setEnabled(not calisiyor)

    def kuyruga_al(self):
        """Dönüştür sırasına girdi: işi bitene kadar ✕, bağlantı ve hedef kapalı."""
        for parca in (self.sil, self.baglanti, self.hedef):
            parca.setEnabled(False)

    def _siraya_al(self):
        if self.durum in ("bitti", "hata", "desteklenmiyor"):
            self.durum_ayarla("sirada")

    def _klasorde_goster(self):
        if self.cikti_yolu:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(self.cikti_yolu).parent)))

    def _kaynak_uzantisi(self):
        return "." + self.bilgi["tur"].lower()

    def _kayip_uyarisi(self):
        """Seçili hedef kayıplıysa açıklaması, değilse boş metin."""
        uzanti = hedef_uzantisi(self.hedef.currentText())
        if not uzanti or not kayipli_mi(self._kaynak_uzantisi(), uzanti):
            return ""
        return donusturucu(self._kaynak_uzantisi(), uzanti)["uyari"]

    def _kayip_guncelle(self):
        uyari = self._kayip_uyarisi()
        self.kayip_etiketi.setVisible(bool(uyari))
        self.kayip_etiketi.setToolTip(f"Kayıplı dönüşüm: {uyari}" if uyari else "")

    def donusturme_isi(self):
        """Dönüştür için gereken bilgiler; bu satırın hedefi henüz yapılamıyorsa None.

        "kapak": EPUB kalır, kapağı işlenir. Kitap adı/yazar yalnızca kullanıcı Kaydet ile
                 değiştirdiyse verilir (yoksa None → kitaptaki kalır).
        "donustur": başka biçime dönüştürülür (kapak/ad/yazar seçimleri uygulanmaz).
        """
        hedef = self.hedef.currentText()
        if self.bilgi["tur"] != "EPUB" or hedef not in KAPAK_HEDEFLERI:
            uzanti = hedef_uzantisi(hedef)
            if uzanti and donusturucu(self._kaynak_uzantisi(), uzanti):
                return {"tur": "donustur", "kaynak": self.bilgi["yol"], "hedef_uzanti": uzanti}
            return None
        secim = self.bilgi.get("secimler") or {}
        kitap_adi = secim.get("kitap_adi")
        yazar = secim.get("yazar")
        return {
            "tur": "kapak",
            "kaynak": self.bilgi["yol"],
            "gorsel_yolu": secim.get("gorsel_yolu"),
            "sigdir": bool(secim.get("sigdir")),
            "kitap_adi": kitap_adi if kitap_adi is not None and kitap_adi != self.bilgi.get("kitap_adi", "") else None,
            "yazar": yazar if yazar is not None and yazar != self.bilgi.get("yazar", "") else None,
        }

    def _kapak_gorunumunu_guncelle(self):
        """Kapak etiketi ve bağlantı: kitabın kapağına ve kaydedilen seçime göre."""
        b = self.bilgi
        kapak = b.get("kapak")
        if kapak is None:  # PDF ya da okunamayan EPUB
            self.kapak_etiketi.hide()
            return
        yeni_kapak = bool((b.get("secimler") or {}).get("gorsel_yolu"))
        if yeni_kapak:
            metin, ad = ("✓  Yeni kapak seçildi" if kapak == "var" else "✓  Kapak seçildi"), "yesilEtiket"
        elif kapak == "var":
            metin, ad = "✓  Kapağı var", "yesilEtiket"  # kısa tutuldu: satır karta sığsın
        else:
            metin, ad = "!  Kapağı yok", "turuncuEtiket"
        self.kapak_etiketi.setText(metin)
        self.kapak_etiketi.setToolTip(
            "Dönüştürünce kapak e-okuyucu boyutuna getirilir." if kapak == "var" or yeni_kapak else ""
        )
        if self.kapak_etiketi.objectName() != ad:
            self.kapak_etiketi.setObjectName(ad)
            self.kapak_etiketi.style().unpolish(self.kapak_etiketi)  # yeni renk uygulansın
            self.kapak_etiketi.style().polish(self.kapak_etiketi)
        self.kapak_etiketi.show()
        if b.get("baglanti"):
            self.baglanti.setText("Kapağa bak" if yeni_kapak else b["baglanti"])


class DosyaListesiKarti(QFrame):
    """'Sıradaki dosyalar' kartı."""

    def __init__(self):
        super().__init__()
        self.setObjectName("kart")
        duzen = QVBoxLayout(self)
        duzen.setContentsMargins(20, 18, 20, 18)
        duzen.setSpacing(14)

        ust = QHBoxLayout()
        ust.setSpacing(10)
        ust.addWidget(etiket("Sıradaki dosyalar", "kartBasligi"))
        self.sayac = etiket("0", "sayac")
        ust.addWidget(self.sayac, alignment=Qt.AlignVCenter)
        ust.addStretch()
        ust.addWidget(etiket("Tümünü şuna çevir"))
        self.toplu_hedef = Secim()
        self.toplu_hedef.setObjectName("hapSecim")
        self.toplu_hedef.addItems(TOPLU_HEDEFLER)
        self.toplu_hedef.setMinimumWidth(130)
        ust.addWidget(self.toplu_hedef)
        duzen.addLayout(ust)

        # Satırlar kaydırılabilir bir alanda
        liste = QWidget()
        liste.setObjectName("liste")
        self.satirlar = QVBoxLayout(liste)
        self.satirlar.setContentsMargins(0, 4, 0, 4)
        self.satirlar.setSpacing(18)
        self.satirlar.addStretch()  # satırlar bunun önüne eklenir

        # Liste boşken görünen yazı
        self.bos_yazi = etiket("Henüz dosya yok", "bosYazi")
        self.bos_yazi.setAlignment(Qt.AlignCenter)

        kaydirma = self.kaydirma = QScrollArea()
        kaydirma.setWidgetResizable(True)
        kaydirma.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        kaydirma.setWidget(liste)
        duzen.addWidget(kaydirma, 1)
        duzen.addWidget(self.bos_yazi, 1)
        self._yollar = set()  # eklenmiş dosyaların tam yolları
        self._gorunumu_guncelle()

    def dosyalari_ekle(self, yollar):
        """Dosyaları listeye ekler; zaten listede olanları atlar. Eklenen sayısını döndürür."""
        eklenen = 0
        for yol in yollar:
            tam = Path(yol).resolve()
            if tam in self._yollar:
                continue
            self._yollar.add(tam)
            bilgi = {"ad": tam.name, "tur": tam.suffix[1:].upper(), "yol": str(tam)}
            if bilgi["tur"] == "EPUB":
                epub = epub_bilgileri(tam)  # okunamadıysa None → etiket ve bağlantı yok
                if epub:
                    kapak = epub["kapak"]
                    bilgi.update(
                        kapak=kapak,
                        kapak_yolu=epub["kapak_yolu"],
                        kitap_adi=epub["kitap_adi"],
                        yazar=epub["yazar"],
                        hedef=KAPAGA_GORE_HEDEF[kapak],
                        baglanti=KAPAGA_GORE_BAGLANTI[kapak],
                    )
            self.satir_ekle(bilgi)
            eklenen += 1
        return eklenen

    def temizle(self):
        """Bütün satırları kaldırır."""
        while self._satir_sayisi() > 0:
            satir = self.satirlar.takeAt(0).widget()
            satir.deleteLater()
        self._yollar.clear()
        self._gorunumu_guncelle()

    def satir_ekle(self, bilgi):
        """Listeye bir DosyaSatiri ekler ve sayacı günceller."""
        satir = DosyaSatiri(bilgi)
        satir.sil.clicked.connect(lambda: self.satir_sil(satir))
        self.satirlar.insertWidget(self.satirlar.count() - 1, satir)
        self._gorunumu_guncelle()
        return satir

    def satir_sil(self, satir):
        """Tek bir satırı listeden çıkarır; aynı dosya sonra yeniden eklenebilir."""
        self.satirlar.removeWidget(satir)
        satir.deleteLater()
        if satir.bilgi.get("yol"):
            self._yollar.discard(Path(satir.bilgi["yol"]))
        self._gorunumu_guncelle()

    def satirlar_listesi(self):
        """Listedeki bütün DosyaSatiri'lar, sırasıyla."""
        return [self.satirlar.itemAt(i).widget() for i in range(self._satir_sayisi())]

    def _satir_sayisi(self):
        return self.satirlar.count() - 1  # sondaki boşluk sayılmaz

    def _gorunumu_guncelle(self):
        sayi = self._satir_sayisi()
        self.sayac.setText(str(sayi))
        self.bos_yazi.setVisible(sayi == 0)
        self.kaydirma.setVisible(sayi > 0)
