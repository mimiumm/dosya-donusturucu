from html import escape
from pathlib import Path

import pymupdf as fitz  # PyMuPDF ('import fitz' eskidi, terminale uyarı yazıyordu)
from ebooklib import epub


def pdf_to_epub(src, dst, lang="tr"):
    doc = fitz.open(src)
    stem = Path(src).stem

    book = epub.EpubBook()
    book.set_identifier(f"conv-{stem}")
    book.set_title(doc.metadata.get("title") or stem)
    book.set_language(lang)
    if doc.metadata.get("author"):
        book.add_author(doc.metadata["author"])

    chapters = []
    for i, page in enumerate(doc, start=1):
        blocks = page.get_text("blocks")
        paras = [b[4].strip().replace("\n", " ")
                 for b in blocks if b[6] == 0 and b[4].strip()]
        body = "".join(f"<p>{escape(p)}</p>" for p in paras)
        ch = epub.EpubHtml(title=f"Sayfa {i}", file_name=f"sayfa_{i}.xhtml", lang=lang)
        ch.content = f"<h2>Sayfa {i}</h2>{body}"
        book.add_item(ch)
        chapters.append(ch)

    book.toc = chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + chapters
    epub.write_epub(dst, book)


def epub_to_pdf(src, dst, width=595, height=842, fontsize=11):
    doc = fitz.open(src)
    doc.layout(width=width, height=height, fontsize=fontsize)
    pdf = fitz.open("pdf", doc.convert_to_pdf())
    pdf.save(dst)