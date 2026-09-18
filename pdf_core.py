# =============================================================================
# AllTools — PDF Core Operations
# Author  : Ali Qureshi
# License : MIT
# =============================================================================
import os
import pymupdf as fitz
from PIL import Image

# ── Existing tools ──────────────────────────────────────────

def img_to_pdf(image_paths, output_path):
    """Convert a list of images to a single PDF."""
    if not image_paths:
        raise ValueError("No images provided.")
    doc = fitz.open()
    for img_path in image_paths:
        img = fitz.open(img_path)
        pdfbytes = img.convert_to_pdf()
        img.close()
        img_pdf = fitz.open("pdf", pdfbytes)
        doc.insert_pdf(img_pdf)
        img_pdf.close()
    doc.save(output_path)
    doc.close()

def pdf_to_img(pdf_path, output_folder, dpi=150):
    """Convert each page of a PDF to a PNG image."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    doc = fitz.open(pdf_path)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    saved_files = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=mat)
        output_file = os.path.join(output_folder, f"{base_name}_page_{page_num + 1}.png")
        pix.save(output_file)
        saved_files.append(output_file)
    doc.close()
    return saved_files

def compress_pdf(input_path, output_path):
    """Compress a PDF by removing unused objects and deflating streams."""
    doc = fitz.open(input_path)
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()
    return output_path

# ── New PDF tools ────────────────────────────────────────────

def merge_pdfs(input_paths, output_path):
    """Merge multiple PDFs into one."""
    doc = fitz.open()
    for path in input_paths:
        src = fitz.open(path)
        doc.insert_pdf(src)
        src.close()
    doc.save(output_path)
    doc.close()

def split_pdf(input_path, output_folder):
    """Split a PDF into individual pages."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    doc = fitz.open(input_path)
    base = os.path.splitext(os.path.basename(input_path))[0]
    out_paths = []
    for i in range(len(doc)):
        out = fitz.open()
        out.insert_pdf(doc, from_page=i, to_page=i)
        out_path = os.path.join(output_folder, f"{base}_page_{i + 1}.pdf")
        out.save(out_path)
        out.close()
        out_paths.append(out_path)
    doc.close()
    return out_paths

def extract_pages(input_path, output_path, page_ranges):
    """Extract specific pages from a PDF. page_ranges: list of (start, end) tuples (0-indexed)."""
    doc = fitz.open(input_path)
    out = fitz.open()
    for start, end in page_ranges:
        out.insert_pdf(doc, from_page=start, to_page=end)
    out.save(output_path)
    out.close()
    doc.close()

def remove_pages(input_path, output_path, page_numbers):
    """Remove specific pages (0-indexed list) from a PDF."""
    doc = fitz.open(input_path)
    doc.delete_pages(page_numbers)
    doc.save(output_path)
    doc.close()

def rotate_pdf(input_path, output_path, degrees):
    """Rotate all pages by degrees (90, 180, 270)."""
    doc = fitz.open(input_path)
    for page in doc:
        page.set_rotation(degrees)
    doc.save(output_path)
    doc.close()

def protect_pdf(input_path, output_path, user_password, owner_password=None):
    """Add password protection to a PDF."""
    doc = fitz.open(input_path)
    perm = fitz.PDF_PERM_PRINT | fitz.PDF_PERM_COPY
    doc.save(
        output_path,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw=user_password,
        owner_pw=owner_password or user_password,
        permissions=perm
    )
    doc.close()

def unlock_pdf(input_path, output_path, password=''):
    """Remove password protection from a PDF."""
    doc = fitz.open(input_path)
    if doc.is_encrypted:
        if not doc.authenticate(password):
            raise ValueError("Incorrect password.")
    doc.save(output_path, encryption=fitz.PDF_ENCRYPT_NONE)
    doc.close()

def flatten_pdf(input_path, output_path):
    """Flatten form fields in a PDF."""
    doc = fitz.open(input_path)
    for page in doc:
        # Flatten by removing annotations (form fields)
        page.clean_contents()
        annots = [a for a in page.annots()]
        for annot in annots:
            page.delete_annot(annot)
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()

def resize_pdf(input_path, output_path, width_pt, height_pt):
    """Resize all pages to given dimensions in points (1 pt = 1/72 inch).
    Uses show_pdf_page to correctly scale content into the new page size.
    """
    src = fitz.open(input_path)
    doc = fitz.open()
    new_rect = fitz.Rect(0, 0, width_pt, height_pt)
    for page_num in range(len(src)):
        new_page = doc.new_page(width=width_pt, height=height_pt)
        new_page.show_pdf_page(new_rect, src, page_num)
    doc.save(output_path)
    doc.close()
    src.close()
    return output_path

def crop_pdf(input_path, output_path, left_pct, top_pct, right_pct, bottom_pct):
    """Crop all pages by percentages (0–100) from each edge."""
    doc = fitz.open(input_path)
    for page in doc:
        r = page.rect
        crop = fitz.Rect(
            r.x0 + r.width  * left_pct   / 100,
            r.y0 + r.height * top_pct    / 100,
            r.x1 - r.width  * right_pct  / 100,
            r.y1 - r.height * bottom_pct / 100,
        )
        page.set_cropbox(crop)
    doc.save(output_path)
    doc.close()

def extract_images_from_pdf(input_path, output_folder):
    """Extract all embedded images from a PDF."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    doc = fitz.open(input_path)
    count = 0
    for page_num, page in enumerate(doc):
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image['image']
            ext = base_image['ext']
            out_path = os.path.join(output_folder, f"page{page_num+1}_img{img_index+1}.{ext}")
            with open(out_path, 'wb') as f:
                f.write(img_bytes)
            count += 1
    doc.close()
    return count

def organize_pdf(input_path, output_path, page_order):
    """Re-order pages. page_order: list of 0-based page indices in desired order."""
    doc = fitz.open(input_path)
    out = fitz.open()
    for idx in page_order:
        out.insert_pdf(doc, from_page=idx, to_page=idx)
    out.save(output_path)
    out.close()
    doc.close()
