# AllTools

<div align="center">

![AllTools Banner](https://img.shields.io/badge/AllTools-Desktop%20Suite-6366f1?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)

**A fast, modern, all-in-one desktop utility for PDF, Image, Video and Office file operations.**  
No subscriptions. No internet. Everything runs locally on your machine.

</div>

---

## ✨ Features

### 🗂️ PDF Tools (13 operations)
| Tool | Description |
|---|---|
| Merge PDFs | Combine multiple PDFs into one |
| Split PDF | Split into individual pages |
| Compress PDF | Reduce file size with garbage collection + deflate |
| Rotate PDF | Rotate all pages by 90 / 180 / 270° |
| Crop PDF | Crop page margins by percentage |
| Resize PDF | Resize pages to any point dimension (A4, Letter, A5 …) |
| Protect PDF | Add AES-256 password encryption |
| Unlock PDF | Remove password from a PDF |
| Flatten PDF | Remove form fields and annotations |
| Extract Pages | Extract a range of pages into a new PDF |
| Remove Pages | Delete specific pages from a PDF |
| Organize PDF | Re-order pages in any custom order |
| Image ↔ PDF | Convert images to PDF and PDF pages to PNG images |
| Extract Images | Pull all embedded images out of a PDF |

### 🖼️ Image Tools (7 operations)
| Tool | Description |
|---|---|
| Convert Image | Convert between PNG, JPG, WEBP, BMP, GIF and more |
| Resize Image | Resize to exact pixel dimensions |
| Crop Image | Crop to a bounding box |
| Rotate Image | Rotate by any degree |
| Flip Image | Flip horizontally or vertically |
| Enlarge / Scale | Scale up or down by a multiplier |
| GIF Maker | Animate multiple images into a GIF |

### 🎬 Video Tools
| Tool | Description |
|---|---|
| Trim Video | Cut a video between two timestamps |
| Crop Video | Crop to a pixel bounding box |

### 📄 Office Conversions
| Tool | Description |
|---|---|
| Word → PDF | Convert `.docx` to PDF (requires MS Word) |
| Excel → PDF | Convert `.xlsx` to PDF (requires MS Excel) |
| PowerPoint → PDF | Convert `.pptx` to PDF (requires MS PowerPoint) |
| PDF → Word | Convert PDF to editable `.docx` |
| PDF → Excel | Extract tables from PDF to `.xlsx` |
| PDF → PowerPoint | Convert PDF pages to `.pptx` slides |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Microsoft Office installed (only required for Word/Excel/PPT conversions)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/alltoolspdf.git
cd alltoolspdf

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Build the frontend UI
cd ui
npm install
npm run build
cd ..

# 4. Run the app
python main.py
```

### Building a standalone `.exe`

```bash
pip install pyinstaller
pyinstaller AllTools.spec
# Output: dist/AllTools/AllTools.exe
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Desktop shell | [pywebview](https://pywebview.flowrl.com/) |
| Frontend | React + Tailwind CSS + Framer Motion |
| PDF engine | [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) |
| Image engine | [Pillow](https://pillow.readthedocs.io/) |
| Video engine | [MoviePy](https://zulko.github.io/moviepy/) |
| PDF → Word | [pdf2docx](https://pdf2docx.readthedocs.io/) |
| PDF → Excel | [pdfplumber](https://github.com/jsvine/pdfplumber) + pandas |
| PDF → PPT | python-pptx + PyMuPDF rendering |
| Office → PDF | MS Office COM automation (comtypes) |

---

## 📦 Dependencies

```
pymupdf
Pillow
moviepy
pdf2docx
comtypes
pdfplumber
pandas
openpyxl
python-pptx
pywebview
```

---

## 🔒 Security

AllTools runs entirely **offline** — no data is sent to any server, cloud, or third party.  
All file operations happen locally on your machine.

Input validation is enforced on all tool parameters (numeric fields, file extensions, path safety).  
See [SECURITY.md](SECURITY.md) for the full security policy.

---

## 📂 Project Structure

```
alltoolspdf/
├── main.py                  # App entry point + pywebview API layer
├── pdf_core.py              # PDF operations (PyMuPDF)
├── img_core.py              # Image operations (Pillow)
├── video_core.py            # Video operations (MoviePy)
├── office_to_pdf_core.py    # Office → PDF (COM automation)
├── pdf_to_office_core.py    # PDF → Office (pdf2docx / pdfplumber)
├── ui/                      # React frontend
│   └── src/App.jsx
├── requirements.txt
├── AllTools.spec            # PyInstaller build spec
├── INSTRUCTIONS.txt         # End-user guide
└── SECURITY.md              # Security policy
```

---

## 📝 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Ali Qureshi**  
Built with ❤️ as a free, open-source desktop productivity tool.

> _Contributions, issues and feature requests are welcome!_
