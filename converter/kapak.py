"""Kitap kapaklarıyla ilgili işler: EPUB'da kapak var mı, kapak resmi, kitap adı ve yazar;
kapağı düzeltilmiş yeni bir EPUB yazma."""

import os
import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

from lxml import etree
from PySide6.QtCore import QBuffer, QByteArray, QIODevice, Qt
from PySide6.QtGui import QColor, QImage, QPainter

from .yollar import benzersiz_yol

EN_BUYUK_KAPAK = 30 * 1024 * 1024  # bundan büyük "kapak" resmi okunmaz
OPF = "http://www.idpf.org/2007/opf"
DC = "http://purl.org/dc/elements/1.1/"
# Bu şifreleme türleri yalnızca yazı tiplerini gizler; kitabın kendisi korumalı değildir
YAZI_TIPI_GIZLEME = {"http://www.idpf.org/2008/embedding", "http://ns.adobe.com/pdf/enc#RC"}


class KapakHatasi(Exception):
    """Yeni EPUB yazılamadığında; mesajı kullanıcıya gösterilebilir."""


def epub_bilgileri(yol):
    """EPUB'dan kapak durumunu, kapak resminin yerini, kitap adını ve yazarı okur.

    Döndürür: {"kapak": "var" | "yok", "kapak_yolu": EPUB içindeki yol ya da None,
               "kitap_adi": str, "yazar": str}
    Dosya okunamazsa (bozuk ya da EPUB değil) None döndürür.
    """
    try:
        with zipfile.ZipFile(yol) as z:
            dosyalar = set(z.namelist())
            kapsayici = ET.fromstring(z.read("META-INF/container.xml"))
            rootfile = kapsayici.find(".//{*}rootfile")
            if rootfile is None or not rootfile.get("full-path"):
                return None
            opf_yolu = rootfile.get("full-path")
            opf = ET.fromstring(z.read(opf_yolu))
    except (zipfile.BadZipFile, KeyError, ET.ParseError, OSError):
        return None

    kapak_yolu = _kapak_resmini_bul(opf, posixpath.dirname(opf_yolu), dosyalar)
    metadata = opf.find("{*}metadata")
    if metadata is None:
        metadata = opf

    def metin(oge):
        return " ".join((oge.text or "").split())

    baslik = metadata.find("{*}title")
    yazarlar = [metin(o) for o in metadata.iterfind("{*}creator") if metin(o)]
    return {
        "kapak": "var" if kapak_yolu else "yok",
        "kapak_yolu": kapak_yolu,
        "kitap_adi": metin(baslik) if baslik is not None else "",
        "yazar": ", ".join(yazarlar),
    }


def epub_kapak_durumu(yol):
    """EPUB'da e-okuyucuların göreceği bir kapak tanımlı mı? "var", "yok" ya da okunamadıysa None."""
    bilgi = epub_bilgileri(yol)
    return bilgi["kapak"] if bilgi else None


def epub_kapak_resmi(yol, resim_yolu):
    """EPUB içindeki kapak resminin baytlarını döndürür; okunamazsa None."""
    try:
        with zipfile.ZipFile(yol) as z:
            if z.getinfo(resim_yolu).file_size > EN_BUYUK_KAPAK:
                return None
            return z.read(resim_yolu)
    except (zipfile.BadZipFile, KeyError, OSError):
        return None


def _kapak_resmini_bul(opf, opf_klasoru, dosyalar):
    """Kapak resminin EPUB içindeki yolunu bulur; yoksa None.

    Kapak sayılanlar, sırayla:
      1. EPUB 3: properties="cover-image" olan resim
      2. EPUB 2: <meta name="cover" content="..."> ile gösterilen resim
      3. Yedek: id'si ya da dosya adı "cover" içeren resim
    Resim dosyası EPUB'un içinde gerçekten bulunmalı.
    """

    def tam_yol(href):
        href = unquote(href.split("#", 1)[0])
        return posixpath.normpath(posixpath.join(opf_klasoru, href))

    # Manifest'teki resimler: id → (EPUB içindeki yol, properties)
    resimler = {}
    for oge in opf.iterfind(".//{*}item"):
        if (oge.get("media-type") or "").startswith("image/") and oge.get("href"):
            resimler[oge.get("id") or ""] = (tam_yol(oge.get("href")), (oge.get("properties") or "").split())

    # 1. EPUB 3
    for yol_, ozellikler in resimler.values():
        if "cover-image" in ozellikler and yol_ in dosyalar:
            return yol_

    # 2. EPUB 2 (content bazen id yerine dosya yolu olur)
    for meta in opf.iterfind(".//{*}meta"):
        if meta.get("name") == "cover" and meta.get("content"):
            icerik = meta.get("content")
            if icerik in resimler and resimler[icerik][0] in dosyalar:
                return resimler[icerik][0]
            for yol_, _ in resimler.values():
                if yol_ == tam_yol(icerik) and yol_ in dosyalar:
                    return yol_

    # 3. Yedek: adında "cover" geçen resim
    for kimlik, (yol_, _) in resimler.items():
        if ("cover" in kimlik.lower() or "cover" in posixpath.basename(yol_).lower()) and yol_ in dosyalar:
            return yol_

    return None


# --- Kapağı düzeltilmiş yeni EPUB ---


def kapak_resmi_hazirla(veri, genislik, yukseklik, sigdir=False):
    """Resmi e-okuyucu boyutuna getirir ve JPG baytı döndürür.

    Doldur (varsayılan): ekranı kaplar, taşan kenarlar kırpılır.
    Sığdır: resim bütün görünür, kalan yer beyaz olur.
    """
    resim = QImage.fromData(veri)
    if resim.isNull():
        raise KapakHatasi("Kapak resmi açılamadı.")
    kip = Qt.KeepAspectRatio if sigdir else Qt.KeepAspectRatioByExpanding
    olcekli = resim.scaled(genislik, yukseklik, kip, Qt.SmoothTransformation)
    sonuc = QImage(genislik, yukseklik, QImage.Format_RGB32)
    sonuc.fill(QColor("white"))  # saydam yerler ve Sığdır boşlukları beyaz olsun
    p = QPainter(sonuc)
    p.drawImage((genislik - olcekli.width()) // 2, (yukseklik - olcekli.height()) // 2, olcekli)
    p.end()
    bayt = QByteArray()
    tampon = QBuffer(bayt)
    tampon.open(QIODevice.WriteOnly)
    if not sonuc.save(tampon, "JPG", 90):
        raise KapakHatasi("Kapak resmi kaydedilemedi.")
    return bytes(bayt)


def epub_kapakli_yaz(kaynak, hedef_klasor, boyut, gorsel_yolu=None, sigdir=False, kitap_adi=None, yazar=None):
    """Kaynak EPUB'un kopyasını hedef_klasor'e yazar; orijinale dokunmaz. Yazılan dosyanın yolunu döndürür.

    boyut:       (genişlik, yükseklik) — e-okuyucu ekranı
    gorsel_yolu: kullanıcının seçtiği kapak resmi. Yoksa kitabın kendi kapağı kullanılır;
                 kitabın kapağı da yoksa kitap kapaksız kopyalanır.
    sigdir:      False → Doldur (kenarlar kırpılır), True → Sığdır (beyaz boşluk)
    kitap_adi, yazar: None → kitaptaki hâli korunur; metin → kitaba yazılır.
    Hata olursa KapakHatasi verir ve yarım dosya bırakmaz.
    """
    kaynak = Path(kaynak).resolve()
    hedef_klasor = Path(hedef_klasor)
    bilgi = epub_bilgileri(kaynak)
    if bilgi is None:
        raise KapakHatasi("EPUB okunamadı (bozuk ya da EPUB değil).")

    try:
        with zipfile.ZipFile(kaynak) as z:
            _korumali_mi(z)
            ogeler = [(oge, z.read(oge.filename)) for oge in z.infolist() if not oge.is_dir()]
            kapsayici = ET.fromstring(z.read("META-INF/container.xml"))
            opf_yolu = kapsayici.find(".//{*}rootfile").get("full-path")
            eski_kapak = z.read(bilgi["kapak_yolu"]) if bilgi["kapak_yolu"] else None
    except (zipfile.BadZipFile, KeyError, OSError, ET.ParseError) as hata:
        raise KapakHatasi(f"EPUB okunamadı: {hata}") from hata

    # Kapak: önce kullanıcının seçtiği, yoksa kitabın kendi kapağı
    if gorsel_yolu:
        try:
            kapak_verisi = Path(gorsel_yolu).read_bytes()
        except OSError as hata:
            raise KapakHatasi(f"Seçilen kapak resmi okunamadı: {Path(gorsel_yolu).name}") from hata
    else:
        kapak_verisi = eski_kapak
    yeni_kapak = kapak_resmi_hazirla(kapak_verisi, *boyut, sigdir=sigdir) if kapak_verisi else None

    dosyalar = {oge.filename for oge, _ in ogeler}
    opf_verisi = dict((oge.filename, veri) for oge, veri in ogeler)[opf_yolu]
    opf_verisi, kapak_dosyasi, sayfa_dosyasi, sayfa = _opf_duzenle(
        opf_verisi, opf_yolu, dosyalar, yeni_kapak is not None, kitap_adi, yazar, boyut)

    # Önce geçici adla yaz, bitince asıl ada taşı: yarım dosya kalmasın
    hedef_klasor.mkdir(parents=True, exist_ok=True)
    hedef = benzersiz_yol(hedef_klasor, kaynak.name)
    if hedef.resolve() == kaynak:  # olmaz ama orijinalin üzerine asla yazılmasın
        raise KapakHatasi("Hedef dosya orijinalle aynı.")
    gecici = hedef.with_name(f".{hedef.name}.yaziliyor")
    try:
        with zipfile.ZipFile(gecici, "w") as cikti:
            # EPUB kuralı: 'mimetype' ilk dosya olmalı ve sıkıştırılmamalı
            cikti.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
            for oge, veri in ogeler:
                if oge.filename == "mimetype":
                    continue
                if oge.filename == opf_yolu:
                    veri = opf_verisi
                cikti.writestr(oge.filename, veri, compress_type=zipfile.ZIP_DEFLATED)
            if yeni_kapak is not None:
                cikti.writestr(kapak_dosyasi, yeni_kapak, compress_type=zipfile.ZIP_DEFLATED)
            if sayfa is not None:
                cikti.writestr(sayfa_dosyasi, sayfa, compress_type=zipfile.ZIP_DEFLATED)
        os.replace(gecici, hedef)
    except OSError as hata:
        gecici.unlink(missing_ok=True)
        raise KapakHatasi(f"Dosya yazılamadı: {hata}") from hata
    return hedef


def _korumali_mi(z):
    """DRM korumalı kitapsa KapakHatasi verir (yazı tipi gizleme koruma sayılmaz)."""
    try:
        sifreleme = etree.fromstring(z.read("META-INF/encryption.xml"), _guvenli_ayristirici())
    except KeyError:
        return
    for yontem in sifreleme.iterfind(".//{*}EncryptionMethod"):
        if yontem.get("Algorithm") not in YAZI_TIPI_GIZLEME:
            raise KapakHatasi("Bu kitap DRM korumalı; değiştirilemez.")


def _guvenli_ayristirici():
    return etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False)


def _opf_ogesi(ust, etiket, sira=None, **ozellikler):
    """OPF ad alanında öğe ekler (öneki yazarken _opf_onekini_kaldir düzeltir)."""
    oge = etree.SubElement(ust, f"{{{OPF}}}{etiket}")
    for ad, deger in ozellikler.items():
        oge.set(ad.replace("_", "-"), deger)
    if sira is not None:
        ust.insert(sira, oge)
    return oge


def _opf_onekini_kaldir(kok, veri):
    """'<opf:meta …>' gibi önekli OPF öğelerini '<meta …>' olarak yazar.

    Kobo önekli satırları tanımıyor. lxml, kitapta 'xmlns:opf' tanımlıysa yeni öğelere bu öneki
    kendiliğinden veriyor. Önek, yalnızca o noktada varsayılan ad alanı da OPF ise kaldırılır
    (XML'de anlam aynı kalır); değilse dosyaya dokunulmaz.
    """
    onekliler = [o for o in kok.iter(etree.Element) if o.prefix == "opf"]
    if not onekliler:
        return veri
    if not all(etree.QName(o).namespace == OPF and o.nsmap.get(None) == OPF for o in onekliler):
        return veri
    return re.sub(rb"<(/?)opf:", rb"<\1", veri)


def _kapak_sayfasi(epub3, resim_href, genislik, yukseklik):
    """Yalnızca kapak resmini tam ekran, oranını bozmadan gösteren sayfa (calibre'nin SVG yöntemi)."""
    bas = ('<!DOCTYPE html>' if epub3 else
           '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">')
    epub_ns = ' xmlns:epub="http://www.idpf.org/2007/ops"' if epub3 else ""
    govde = ' epub:type="cover"' if epub3 else ""
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'{bas}\n'
        f'<html xmlns="http://www.w3.org/1999/xhtml"{epub_ns}>\n'
        '<head>\n'
        '<title>Kapak</title>\n'
        '<style type="text/css">@page { margin: 0 } html, body { margin: 0; padding: 0; height: 100%; '
        'text-align: center }</style>\n'
        '</head>\n'
        f'<body{govde}>\n'
        '<div style="height: 100%; text-align: center">\n'
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" '
        f'width="100%" height="100%" viewBox="0 0 {genislik} {yukseklik}" preserveAspectRatio="xMidYMid meet">\n'
        f'<image width="{genislik}" height="{yukseklik}" xlink:href="{resim_href}"/>\n'
        '</svg>\n'
        '</div>\n'
        '</body>\n'
        '</html>\n'
    ).encode("utf-8")


def _opf_duzenle(opf_verisi, opf_yolu, dosyalar, kapak_eklenecek, kitap_adi, yazar, boyut):
    """OPF'i düzenler.

    Döndürür: (yeni OPF baytı, kapak resminin EPUB içindeki yolu, kapak sayfasının yolu, kapak sayfası baytı)
    Kapak eklenmeyecekse son üçü None.
    """
    try:
        kok = etree.fromstring(opf_verisi, _guvenli_ayristirici())
    except etree.XMLSyntaxError as hata:
        raise KapakHatasi(f"Kitabın içerik listesi (OPF) okunamadı: {hata}") from hata
    metadata = kok.find(f"{{{OPF}}}metadata")
    manifest = kok.find(f"{{{OPF}}}manifest")
    if metadata is None or manifest is None:
        raise KapakHatasi("Kitabın içerik listesi (OPF) eksik.")
    epub3 = (kok.get("version") or "").startswith("3")

    kapak_dosyasi = sayfa_dosyasi = sayfa = None
    if kapak_eklenecek:
        # Benzersiz adlar ve kimlikler (resim + kapak sayfası)
        opf_klasoru = posixpath.dirname(opf_yolu)
        kimlikler = {oge.get("id") for oge in kok.iter() if oge.get("id")}

        def epub_ici(href_):
            return posixpath.join(opf_klasoru, href_) if opf_klasoru else href_

        n, ek = 1, ""
        while True:
            href = f"kapak-donusturucu{ek}.jpg"
            sayfa_href = f"kapak-donusturucu{ek}.xhtml"
            kimlik = f"kapak-donusturucu{ek}"
            sayfa_kimlik = f"kapak-sayfasi-donusturucu{ek}"
            if (epub_ici(href) not in dosyalar and epub_ici(sayfa_href) not in dosyalar
                    and kimlik not in kimlikler and sayfa_kimlik not in kimlikler):
                break
            n += 1
            ek = f"-{n}"
        kapak_dosyasi = epub_ici(href)
        sayfa_dosyasi = epub_ici(sayfa_href)

        # Eski kapak işaretlerini kaldır, yenisini ekle
        for oge in manifest.iterfind(f"{{{OPF}}}item"):
            ozellikler = (oge.get("properties") or "").split()
            if "cover-image" in ozellikler:
                ozellikler.remove("cover-image")
                if ozellikler:
                    oge.set("properties", " ".join(ozellikler))
                else:
                    del oge.attrib["properties"]
        yeni = _opf_ogesi(manifest, "item", id=kimlik, href=href, media_type="image/jpeg")
        if epub3:
            yeni.set("properties", "cover-image")

        # <meta name="cover"> EPUB 2'de kural, EPUB 3'te de Kobo/Kindle için gerekli.
        # Eskisi (önekli olsa bile) kaldırılır, öneksiz yenisi yazılır.
        for m in list(metadata.iterfind(f"{{{OPF}}}meta")):
            if m.get("name") == "cover":
                metadata.remove(m)
        _opf_ogesi(metadata, "meta", name="cover", content=kimlik)

        # Kapak sayfası: manifest + okuma sırasının en başı + guide'da type="cover"
        sayfa_ogesi = _opf_ogesi(manifest, "item", id=sayfa_kimlik, href=sayfa_href,
                                 media_type="application/xhtml+xml")
        if epub3:
            sayfa_ogesi.set("properties", "svg")
        sayfa = _kapak_sayfasi(epub3, href, *boyut)

        spine = kok.find(f"{{{OPF}}}spine")
        if spine is None:
            raise KapakHatasi("Kitabın okuma sırası (spine) eksik.")
        guide = kok.find(f"{{{OPF}}}guide")
        if guide is None:  # OPF sırası: metadata, manifest, spine, guide
            guide = _opf_ogesi(kok, "guide", sira=list(kok).index(spine) + 1)
        # Kitapta zaten kapak olarak işaretli bir sayfa varsa okuma sırasından çıkar (dosyası kalır)
        for ref in list(guide.iterfind(f"{{{OPF}}}reference")):
            if (ref.get("type") or "").lower() != "cover":
                continue
            eski_yol = posixpath.normpath(posixpath.join(opf_klasoru, unquote((ref.get("href") or "").split("#")[0])))
            for oge in manifest.iterfind(f"{{{OPF}}}item"):
                if posixpath.normpath(posixpath.join(opf_klasoru, unquote(oge.get("href") or ""))) == eski_yol:
                    for itemref in list(spine.iterfind(f"{{{OPF}}}itemref")):
                        if itemref.get("idref") == oge.get("id"):
                            spine.remove(itemref)
            guide.remove(ref)
        _opf_ogesi(spine, "itemref", sira=0, idref=sayfa_kimlik, linear="yes")
        _opf_ogesi(guide, "reference", sira=0, type="cover", title="Kapak", href=sayfa_href)

    if kitap_adi is not None:
        baslik = metadata.find(f"{{{DC}}}title")
        if baslik is None:
            baslik = etree.SubElement(metadata, f"{{{DC}}}title")
        baslik.text = kitap_adi

    if yazar is not None:
        eskiler = metadata.findall(f"{{{DC}}}creator")
        eski_kimlikler = {"#" + y.get("id") for y in eskiler if y.get("id")}
        for y in eskiler:
            metadata.remove(y)
        # EPUB 3'te eski yazarlara bağlı ek bilgiler (rol vb.) de kalkmalı
        for m in list(metadata.iterfind(f"{{{OPF}}}meta")):
            if m.get("refines") in eski_kimlikler:
                metadata.remove(m)
        if yazar:
            etree.SubElement(metadata, f"{{{DC}}}creator").text = yazar

    veri = _opf_onekini_kaldir(kok, etree.tostring(kok, xml_declaration=True, encoding="utf-8"))
    return veri, kapak_dosyasi, sayfa_dosyasi, sayfa
