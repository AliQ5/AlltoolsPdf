# =============================================================================
# AllTools — PDF to Office Conversions
# Author  : Ali Qureshi
# License : MIT
# =============================================================================
import os
from pdf2docx import Converter
import pdfplumber
import pandas as pd
import pymupdf as fitz  # PyMuPDF
from pptx import Presentation
from pptx.util import Inches

def pdf_to_word(input_path, output_path):
    """
    Converts a PDF to Word using pdf2docx.
    """
    cv = Converter(input_path)
    cv.convert(output_path, start=0, end=None)
    cv.close()
    return output_path

def pdf_to_excel(input_path, output_path):
    """
    Extracts tables from a PDF and saves them to an Excel file using pdfplumber and pandas.
    """
    with pdfplumber.open(input_path) as pdf:
        all_tables = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                all_tables.append(pd.DataFrame(table))
                
    if not all_tables:
        raise ValueError("No tables found in the PDF.")
        
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for i, df in enumerate(all_tables):
            df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False, header=False)
            
    return output_path

def pdf_to_ppt(input_path, output_path):
    """
    Converts a PDF to a PowerPoint by rendering each page as an image and inserting into slides.
    """
    prs = Presentation()
    
    # We want to match slide dimensions to PDF dimensions roughly
    # But for simplicity, we'll use a standard 4:3 or 16:9 ratio and fit the image.
    blank_slide_layout = prs.slide_layouts[6]
    
    doc = fitz.open(input_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Render high quality image
        zoom = 2.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        temp_img_path = f"temp_page_{page_num}.png"
        pix.save(temp_img_path)
        
        # Add slide
        slide = prs.slides.add_slide(blank_slide_layout)
        
        # Insert image (stretching to fill slide height, centered)
        # Standard pptx slide height is 7.5 inches
        slide.shapes.add_picture(temp_img_path, 0, 0, height=prs.slide_height)
        
        # Clean up temp file
        os.remove(temp_img_path)
        
    doc.close()
    prs.save(output_path)
    return output_path
