"""
Comprehensive test script for all PDF and Word features.

Test files:
  PDF  : Test/Pdf-File.pdf   (10 pages, A4, 595x842 pt, images on every page)
  DOCX : Test/Word-File.docx

Modules tested:
  pdf_core.py         - 13 functions
  office_to_pdf_core  - word_to_pdf   (excel/ppt skipped: no test files)
  pdf_to_office_core  - pdf_to_word, pdf_to_excel, pdf_to_ppt
"""

import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(__file__))
import pdf_core
import office_to_pdf_core
import pdf_to_office_core

try:
    import pymupdf as fitz
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DIR    = os.path.join(PROJECT_DIR, "Test")
OUT_DIR     = os.path.join(TEST_DIR, "pdf_output")

PDF  = os.path.join(TEST_DIR, "Pdf-File.pdf")
DOCX = os.path.join(TEST_DIR, "Word-File.docx")

PDF_PAGES  = 10
PDF_W_PT   = 595.3
PDF_H_PT   = 841.9

os.makedirs(OUT_DIR, exist_ok=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
results = []

def run_test(name, func, *args, verify=None):
    try:
        result = func(*args)
        if verify:
            ok, detail = verify(result)
            if not ok:
                raise AssertionError(detail)
        status = "PASS"
        detail = f"-> {result}"
    except Exception as e:
        status = "FAIL"
        detail = f"-> {e}"
        traceback.print_exc()

    icon = "  [PASS]" if status == "PASS" else "  [FAIL]"
    print(f"{icon}  {name}")
    print(f"         {detail}")
    results.append((name, status))


def file_ok(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0


def verify_file(path):
    if not file_ok(path):
        return False, f"Missing or empty: {path}"
    return True, "OK"


def pdf_page_count(path):
    doc = fitz.open(path)
    n = len(doc)
    doc.close()
    return n


def verify_pdf(path, expected_pages=None):
    ok, msg = verify_file(path)
    if not ok:
        return ok, msg
    if HAS_FITZ:
        try:
            doc = fitz.open(path)
            n = len(doc)
            doc.close()
            if expected_pages is not None and n != expected_pages:
                return False, f"Expected {expected_pages} pages but got {n}"
            return True, f"{n} page(s) OK"
        except Exception as e:
            return False, f"Cannot open PDF: {e}"
    return True, "OK"


def verify_pdf_exists(path):
    return verify_pdf(path)


# ── 1. IMG -> PDF ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("1. IMAGES -> PDF  (img_to_pdf)")
print("="*60)

# We'll render a couple of pages from the test PDF as PNGs and then re-convert them
temp_img1 = os.path.join(OUT_DIR, "_temp_page1.png")
temp_img2 = os.path.join(OUT_DIR, "_temp_page2.png")

if HAS_FITZ:
    doc = fitz.open(PDF)
    doc.load_page(0).get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(temp_img1)
    doc.load_page(1).get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(temp_img2)
    doc.close()

img_to_pdf_out1 = os.path.join(OUT_DIR, "from_single_image.pdf")
run_test(
    "Single image -> PDF",
    pdf_core.img_to_pdf,
    [temp_img1], img_to_pdf_out1,
    verify=lambda r: verify_pdf(img_to_pdf_out1, expected_pages=1)
)

img_to_pdf_out2 = os.path.join(OUT_DIR, "from_two_images.pdf")
run_test(
    "Two images -> PDF (2-page)",
    pdf_core.img_to_pdf,
    [temp_img1, temp_img2], img_to_pdf_out2,
    verify=lambda r: verify_pdf(img_to_pdf_out2, expected_pages=2)
)


# ── 2. PDF -> IMAGES ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("2. PDF -> IMAGES  (pdf_to_img)")
print("="*60)

pdf_to_img_dir = os.path.join(OUT_DIR, "pdf_pages")

def verify_pdf_to_img(result):
    if not isinstance(result, list) or len(result) == 0:
        return False, f"Expected list of paths, got: {result}"
    if len(result) != PDF_PAGES:
        return False, f"Expected {PDF_PAGES} images but got {len(result)}"
    for p in result:
        if not file_ok(p):
            return False, f"Missing image: {p}"
    return True, f"{len(result)} images extracted OK"

run_test(
    f"PDF -> {PDF_PAGES} PNG images (one per page)",
    pdf_core.pdf_to_img,
    PDF, pdf_to_img_dir,
    verify=verify_pdf_to_img
)


# ── 3. COMPRESS PDF ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("3. COMPRESS PDF  (compress_pdf)")
print("="*60)

compress_out = os.path.join(OUT_DIR, "compressed.pdf")

def verify_compress(path):
    ok, msg = verify_pdf(path, expected_pages=PDF_PAGES)
    if not ok:
        return ok, msg
    orig = os.path.getsize(PDF)
    comp = os.path.getsize(path)
    ratio = comp / orig * 100
    return True, f"Original={orig//1024}KB -> Compressed={comp//1024}KB ({ratio:.0f}%)"

run_test(
    "Compress PDF (garbage collect + deflate)",
    pdf_core.compress_pdf,
    PDF, compress_out,
    verify=verify_compress
)


# ── 4. MERGE PDFs ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("4. MERGE PDFs  (merge_pdfs)")
print("="*60)

# Split off first 3 pages to merge back together
split_dir = os.path.join(OUT_DIR, "split_pages")
pdf_core.split_pdf(PDF, split_dir)   # produce individual pages first

p1 = os.path.join(split_dir, "Pdf-File_page_1.pdf")
p2 = os.path.join(split_dir, "Pdf-File_page_2.pdf")
p3 = os.path.join(split_dir, "Pdf-File_page_3.pdf")

merge_out = os.path.join(OUT_DIR, "merged_3pages.pdf")
run_test(
    "Merge 3 single-page PDFs -> 3-page PDF",
    pdf_core.merge_pdfs,
    [p1, p2, p3], merge_out,
    verify=lambda r: verify_pdf(merge_out, expected_pages=3)
)

merge_self_out = os.path.join(OUT_DIR, "merged_self_double.pdf")
run_test(
    "Merge PDF with itself -> doubled page count (20 pages)",
    pdf_core.merge_pdfs,
    [PDF, PDF], merge_self_out,
    verify=lambda r: verify_pdf(merge_self_out, expected_pages=PDF_PAGES * 2)
)


# ── 5. SPLIT PDF ──────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("5. SPLIT PDF  (split_pdf)")
print("="*60)

split_out_dir = os.path.join(OUT_DIR, "split_full")

def verify_split(result):
    if not isinstance(result, list):
        return False, f"Expected list, got: {result}"
    if len(result) != PDF_PAGES:
        return False, f"Expected {PDF_PAGES} files, got {len(result)}"
    for p in result:
        if not file_ok(p):
            return False, f"Missing: {p}"
        n = pdf_page_count(p)
        if n != 1:
            return False, f"Expected 1 page in {p}, got {n}"
    return True, f"Split into {len(result)} single-page PDFs OK"

run_test(
    f"Split {PDF_PAGES}-page PDF into {PDF_PAGES} single-page files",
    pdf_core.split_pdf,
    PDF, split_out_dir,
    verify=verify_split
)


# ── 6. EXTRACT PAGES ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("6. EXTRACT PAGES  (extract_pages)")
print("="*60)

extract_out1 = os.path.join(OUT_DIR, "extract_pages_1to3.pdf")
run_test(
    "Extract pages 1-3 (0-indexed: 0-2) -> 3-page PDF",
    pdf_core.extract_pages,
    PDF, extract_out1, [(0, 2)],
    verify=lambda r: verify_pdf(extract_out1, expected_pages=3)
)

extract_out2 = os.path.join(OUT_DIR, "extract_pages_5and8to10.pdf")
run_test(
    "Extract page 5 + pages 8-10 -> 4-page PDF",
    pdf_core.extract_pages,
    PDF, extract_out2, [(4, 4), (7, 9)],
    verify=lambda r: verify_pdf(extract_out2, expected_pages=4)
)

extract_out3 = os.path.join(OUT_DIR, "extract_single_page5.pdf")
run_test(
    "Extract single page (page 5 only) -> 1-page PDF",
    pdf_core.extract_pages,
    PDF, extract_out3, [(4, 4)],
    verify=lambda r: verify_pdf(extract_out3, expected_pages=1)
)


# ── 7. REMOVE PAGES ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("7. REMOVE PAGES  (remove_pages)")
print("="*60)

remove_out1 = os.path.join(OUT_DIR, "removed_page1.pdf")
run_test(
    "Remove page 1 (0-indexed) -> 9-page PDF",
    pdf_core.remove_pages,
    PDF, remove_out1, [0],
    verify=lambda r: verify_pdf(remove_out1, expected_pages=PDF_PAGES - 1)
)

remove_out2 = os.path.join(OUT_DIR, "removed_pages_1_3_5.pdf")
run_test(
    "Remove pages 1,3,5 (0-indexed: 0,2,4) -> 7-page PDF",
    pdf_core.remove_pages,
    PDF, remove_out2, [0, 2, 4],
    verify=lambda r: verify_pdf(remove_out2, expected_pages=PDF_PAGES - 3)
)


# ── 8. ROTATE PDF ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("8. ROTATE PDF  (rotate_pdf)")
print("="*60)

for deg in [90, 180, 270]:
    rot_out = os.path.join(OUT_DIR, f"rotated_{deg}.pdf")
    run_test(
        f"Rotate all pages by {deg} degrees",
        pdf_core.rotate_pdf,
        PDF, rot_out, deg,
        verify=lambda r, p=rot_out: verify_pdf(p, expected_pages=PDF_PAGES)
    )


# ── 9. PROTECT & UNLOCK PDF ───────────────────────────────────────────────────
print("\n" + "="*60)
print("9. PROTECT PDF  (protect_pdf)")
print("="*60)

protected_out = os.path.join(OUT_DIR, "protected.pdf")
run_test(
    "Protect PDF with password 'test123'",
    pdf_core.protect_pdf,
    PDF, protected_out, "test123",
    verify=lambda r: verify_file(protected_out)
)

# Verify it is actually encrypted
def verify_is_encrypted(path):
    ok, msg = verify_file(path)
    if not ok: return ok, msg
    if HAS_FITZ:
        doc = fitz.open(path)
        enc = doc.is_encrypted
        doc.close()
        if not enc:
            return False, "File is NOT encrypted!"
        return True, "File is encrypted OK"
    return True, "OK"

run_test(
    "Verify protected PDF is encrypted",
    lambda: protected_out,
    verify=verify_is_encrypted
)

print("\n" + "="*60)
print("10. UNLOCK PDF  (unlock_pdf)")
print("="*60)

unlocked_out = os.path.join(OUT_DIR, "unlocked.pdf")
run_test(
    "Unlock protected PDF with correct password 'test123'",
    pdf_core.unlock_pdf,
    protected_out, unlocked_out, "test123",
    verify=lambda r: verify_pdf(unlocked_out, expected_pages=PDF_PAGES)
)

# Wrong password should fail
def wrong_password_test():
    try:
        pdf_core.unlock_pdf(protected_out, os.path.join(OUT_DIR, "should_fail.pdf"), "wrongpass")
        return False, "Should have raised an error!"
    except Exception:
        return True, "Correctly raised error for wrong password"

run_test(
    "Unlock with WRONG password -> should fail gracefully",
    lambda: None,
    verify=lambda r: wrong_password_test()
)


# ── 11. FLATTEN PDF ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("11. FLATTEN PDF  (flatten_pdf)")
print("="*60)

flatten_out = os.path.join(OUT_DIR, "flattened.pdf")
run_test(
    "Flatten PDF (remove form fields / annotations)",
    pdf_core.flatten_pdf,
    PDF, flatten_out,
    verify=lambda r: verify_pdf(flatten_out, expected_pages=PDF_PAGES)
)


# ── 12. RESIZE PDF ────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("12. RESIZE PDF  (resize_pdf)")
print("="*60)

# A4 -> Letter (612 x 792 pt)
resize_out1 = os.path.join(OUT_DIR, "resized_letter.pdf")
run_test(
    "Resize A4 PDF -> US Letter (612x792 pt)",
    pdf_core.resize_pdf,
    PDF, resize_out1, 612, 792,
    verify=lambda r: verify_pdf(resize_out1, expected_pages=PDF_PAGES)
)

# A4 -> A5 (420 x 595 pt)
resize_out2 = os.path.join(OUT_DIR, "resized_a5.pdf")
run_test(
    "Resize A4 PDF -> A5 (420x595 pt)",
    pdf_core.resize_pdf,
    PDF, resize_out2, 420, 595,
    verify=lambda r: verify_pdf(resize_out2, expected_pages=PDF_PAGES)
)


# ── 13. CROP PDF ──────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("13. CROP PDF  (crop_pdf)")
print("="*60)

crop_out1 = os.path.join(OUT_DIR, "cropped_10pct_all_sides.pdf")
run_test(
    "Crop 10% from all sides",
    pdf_core.crop_pdf,
    PDF, crop_out1, 10, 10, 10, 10,
    verify=lambda r: verify_pdf(crop_out1, expected_pages=PDF_PAGES)
)

crop_out2 = os.path.join(OUT_DIR, "cropped_top_half.pdf")
run_test(
    "Crop bottom 50% (show top half only)",
    pdf_core.crop_pdf,
    PDF, crop_out2, 0, 0, 0, 50,
    verify=lambda r: verify_pdf(crop_out2, expected_pages=PDF_PAGES)
)


# ── 14. EXTRACT IMAGES FROM PDF ───────────────────────────────────────────────
print("\n" + "="*60)
print("14. EXTRACT IMAGES FROM PDF  (extract_images_from_pdf)")
print("="*60)

extract_img_dir = os.path.join(OUT_DIR, "extracted_images")

def verify_extracted_images(count):
    if not isinstance(count, int) or count == 0:
        return False, f"Expected >0 images, got: {count}"
    files = [f for f in os.listdir(extract_img_dir) if not f.startswith('.')]
    if len(files) != count:
        return False, f"File count mismatch: reported {count} but found {len(files)} files"
    return True, f"Extracted {count} images OK"

run_test(
    "Extract all embedded images from PDF",
    pdf_core.extract_images_from_pdf,
    PDF, extract_img_dir,
    verify=verify_extracted_images
)


# ── 15. ORGANIZE PDF ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("15. ORGANIZE PDF  (organize_pdf)")
print("="*60)

# Reverse all pages
reverse_order = list(range(PDF_PAGES - 1, -1, -1))
organize_out1 = os.path.join(OUT_DIR, "organized_reversed.pdf")
run_test(
    "Organize: reverse page order (10->1)",
    pdf_core.organize_pdf,
    PDF, organize_out1, reverse_order,
    verify=lambda r: verify_pdf(organize_out1, expected_pages=PDF_PAGES)
)

# Custom order: pages 5,1,3,2,4 (0-indexed)
custom_order = [4, 0, 2, 1, 3]
organize_out2 = os.path.join(OUT_DIR, "organized_custom_5pages.pdf")
run_test(
    "Organize: custom order [5,1,3,2,4] -> 5-page PDF",
    pdf_core.organize_pdf,
    PDF, organize_out2, custom_order,
    verify=lambda r: verify_pdf(organize_out2, expected_pages=5)
)


# ── 16. WORD -> PDF ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("16. WORD -> PDF  (word_to_pdf)")
print("="*60)

word_to_pdf_out = os.path.join(OUT_DIR, "word_converted.pdf")
run_test(
    "Word (.docx) -> PDF via MS Word COM",
    office_to_pdf_core.word_to_pdf,
    DOCX, word_to_pdf_out,
    verify=lambda r: verify_pdf(word_to_pdf_out)
)


# ── 17. PDF -> WORD ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("17. PDF -> WORD  (pdf_to_word)")
print("="*60)

pdf_to_word_out = os.path.join(OUT_DIR, "pdf_to_word.docx")
run_test(
    "PDF -> Word (.docx) via pdf2docx",
    pdf_to_office_core.pdf_to_word,
    PDF, pdf_to_word_out,
    verify=lambda r: verify_file(pdf_to_word_out)
)


# ── 18. PDF -> EXCEL ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("18. PDF -> EXCEL  (pdf_to_excel)")
print("="*60)

pdf_to_excel_out = os.path.join(OUT_DIR, "pdf_to_excel.xlsx")
run_test(
    "PDF -> Excel (.xlsx) - extracts tables",
    pdf_to_office_core.pdf_to_excel,
    PDF, pdf_to_excel_out,
    verify=lambda r: verify_file(pdf_to_excel_out)
)


# ── 19. PDF -> PPT ────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("19. PDF -> POWERPOINT  (pdf_to_ppt)")
print("="*60)

pdf_to_ppt_out = os.path.join(OUT_DIR, "pdf_to_ppt.pptx")

def verify_pptx(path):
    ok, msg = verify_file(path)
    if not ok: return ok, msg
    try:
        from pptx import Presentation
        prs = Presentation(path)
        n = len(prs.slides)
        if n != PDF_PAGES:
            return False, f"Expected {PDF_PAGES} slides but got {n}"
        return True, f"{n} slides OK"
    except Exception as e:
        return False, str(e)

run_test(
    f"PDF ({PDF_PAGES} pages) -> PowerPoint ({PDF_PAGES} slides)",
    pdf_to_office_core.pdf_to_ppt,
    PDF, pdf_to_ppt_out,
    verify=verify_pptx
)


# ── SUMMARY ───────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

passed = sum(1 for _, s in results if s == "PASS")
failed = sum(1 for _, s in results if s == "FAIL")
total  = len(results)

print(f"  Total : {total}")
print(f"  Pass  : {passed}")
print(f"  Fail  : {failed}")
print()

if failed:
    print("Failed tests:")
    for name, status in results:
        if status == "FAIL":
            print(f"  - {name}")
else:
    print("All tests passed!")

print(f"\nOutput files saved to: {OUT_DIR}")
