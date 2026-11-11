# Dosya Dönüştürücü (File Converter)

**English** | [Türkçe](README.tr.md)

A desktop file converter for e-books. It converts between EPUB and PDF, and adds a cover sized for your e-reader's screen to EPUB books, or fixes the existing one. Built with PySide6 (Qt).

> ⚠️ **Work in progress.** The core features work; the missing parts will come in future updates. **The app's interface is currently Turkish only** — an English interface is planned.

## Screenshots

![Main window](screenshots/main-window.png)

| No cover | Image picked | Has cover |
|---|---|---|
| ![No cover](screenshots/no-cover.png) | ![Image picked](screenshots/no-cover-selected.png) | ![Has cover](screenshots/has-cover.png) |

## Features

- **Add / fix EPUB covers** — the cover is resized to the selected e-reader's resolution (Kobo Clara, Kobo Libra, Kindle, Kindle Paperwhite, PocketBook), with *Fill* and *Fit* preview options.
- **Fix book title and author** — from the cover window.
- **EPUB → PDF**
- **PDF → EPUB** — lossy: only the text is carried over; images and page layout are lost. The app marks this with a "Lossy" label.
- **Drag and drop** to add files.
- **Never touches the original** — output is always written as a new file to the chosen save folder (default: `Documents/Kitaplar`). If a file with the same name exists, a new name like `name (2).epub` is used.

## Installation

Requires Python 3.10 or newer.

```bash
git clone https://github.com/mimiumm/dosya-donusturucu.git
cd dosya-donusturucu
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

To open the interface:

```bash
python gui_qt.py
```

To convert a single file from the command line:

```bash
python main.py book.epub book.pdf
```

## Roadmap

- [ ] MOBI, AZW3 and DOCX support
- [ ] "Convert all to…" (batch target selection)
- [ ] English interface
- [ ] Dark theme
- [ ] CBZ and other formats
- [ ] Ready-to-use packages (PyInstaller)

## License

[AGPL-3.0](LICENSE)

© 2026 mimiumm
