# =============================================================================
# AllTools — Desktop Utility Suite
# Author  : Ali Qureshi
# License : MIT
# =============================================================================
import webview
import os
import sys

# Import our logic modules
import pdf_core
import img_core
import office_to_pdf_core
import pdf_to_office_core
import video_core

class Api:
    def __init__(self):
        self.window = None

    def set_window(self, window):
        self.window = window

    # ── Native pywebview dialogs (thread-safe, no tkinter) ──

    def select_files(self, filetypes):
        joined = ";".join(filetypes)
        result = self.window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=True,
            file_types=(f'Files ({joined})', 'All files (*.*)')
        )
        return list(result) if result else []

    def select_file(self, filetypes):
        result = self.window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=(f'Files ({filetypes})', 'All files (*.*)')
        )
        return result[0] if result else None

    def select_folder(self):
        result = self.window.create_file_dialog(webview.FOLDER_DIALOG)
        return result[0] if result else None

    def save_dialog(self, default_ext, description='File'):
        result = self.window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename=f'output{default_ext}'
        )
        if not result:
            return None
        # On Windows, pywebview returns a tuple from SAVE_DIALOG — extract the string
        return result[0] if isinstance(result, (tuple, list)) else result

    # ── Common Runner helper ──
    def _run_tool(self, func, *args, success_msg="Done!"):
        try:
            res = func(*args)
            return {'success': True, 'msg': success_msg, 'result': res}
        except Exception as e:
            return {'success': False, 'msg': str(e)}

    # ── Security: Input Validation Helpers ──────────────────────────────────

    _IMG_EXTS   = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.tiff', '.tif'}
    _VIDEO_EXTS = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm'}
    _PDF_EXTS   = {'.pdf'}
    _DOCX_EXTS  = {'.docx', '.doc'}
    _XLSX_EXTS  = {'.xlsx', '.xls'}
    _PPTX_EXTS  = {'.pptx', '.ppt'}
    _IMG_FMTS   = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'gif', 'tiff', 'tif'}

    def _err(self, msg):
        """Return a standard error response."""
        return {'success': False, 'msg': msg}

    def _validate_path(self, path):
        """Reject path traversal and ensure path is a string."""
        if not isinstance(path, str):
            return False, 'Invalid file path.'
        if '..' in path.replace('\\', '/'):
            return False, 'Path traversal detected — access denied.'
        return True, None

    def _validate_ext(self, path, allowed_exts, label='file'):
        """Enforce file extension whitelist."""
        ext = os.path.splitext(path)[1].lower()
        if ext not in allowed_exts:
            return False, f'Unsupported {label} format "{ext}". Allowed: {", ".join(sorted(allowed_exts))}'
        return True, None

    def _validate_paths(self, paths, allowed_exts, label='file'):
        """Validate a list of paths."""
        if not paths:
            return False, 'No files provided.'
        for p in paths:
            ok, msg = self._validate_path(p)
            if not ok: return False, msg
            ok, msg = self._validate_ext(p, allowed_exts, label)
            if not ok: return False, msg
        return True, None

    def _validate_number(self, value, name, min_val=None, max_val=None, allow_float=False):
        """Ensure value is a valid number within optional bounds."""
        try:
            n = float(value) if allow_float else int(value)
        except (ValueError, TypeError):
            return False, f'"{name}" must be a valid number.'
        if min_val is not None and n < min_val:
            return False, f'"{name}" must be at least {min_val}.'
        if max_val is not None and n > max_val:
            return False, f'"{name}" must be at most {max_val}.'
        return True, None


    # ── Tool Runners: Video ──

    def run_trim_video(self, input_path, start_sec, end_sec):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._VIDEO_EXTS, 'video')
        if not ok: return self._err(msg)
        ok, msg = self._validate_number(start_sec, 'start_sec', min_val=0, allow_float=True)
        if not ok: return self._err(msg)
        ok, msg = self._validate_number(end_sec, 'end_sec', min_val=0, allow_float=True)
        if not ok: return self._err(msg)
        if float(end_sec) <= float(start_sec):
            return self._err('"end_sec" must be greater than "start_sec".')
        out = self.save_dialog('.mp4', 'Video File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(video_core.trim_video, input_path, out, float(start_sec), float(end_sec), success_msg="Video trimmed!")

    def run_crop_video(self, input_path, x1, y1, x2, y2):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._VIDEO_EXTS, 'video')
        if not ok: return self._err(msg)
        for name, val in [('x1', x1), ('y1', y1), ('x2', x2), ('y2', y2)]:
            ok, msg = self._validate_number(val, name, min_val=0)
            if not ok: return self._err(msg)
        if int(x2) <= int(x1) or int(y2) <= int(y1):
            return self._err('Crop box invalid: x2 must be > x1 and y2 must be > y1.')
        out = self.save_dialog('.mp4', 'Video File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(video_core.crop_video, input_path, out, int(x1), int(y1), int(x2), int(y2), success_msg="Video cropped!")

    # ── Tool Runners: Image ──

    def run_img_convert(self, input_img, fmt, output_folder):
        ok, msg = self._validate_path(input_img)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_img, self._IMG_EXTS, 'image')
        if not ok: return self._err(msg)
        fmt_clean = str(fmt).lower().strip().lstrip('.')
        if fmt_clean not in self._IMG_FMTS:
            return self._err(f'Unsupported output format "{fmt_clean}". Allowed: {", ".join(sorted(self._IMG_FMTS))}')
        return self._run_tool(img_core.convert_image, input_img, fmt_clean, output_folder, success_msg=f"Image converted to .{fmt_clean}!")

    def run_resize_image(self, input_path, width, height):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._IMG_EXTS, 'image')
        if not ok: return self._err(msg)
        ok, msg = self._validate_number(width, 'width', min_val=1, max_val=32000)
        if not ok: return self._err(msg)
        ok, msg = self._validate_number(height, 'height', min_val=1, max_val=32000)
        if not ok: return self._err(msg)
        out = self.save_dialog('.png', 'Image File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(img_core.resize_image, input_path, out, int(width), int(height), success_msg="Image resized!")

    def run_crop_image(self, input_path, left, top, right, bottom):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._IMG_EXTS, 'image')
        if not ok: return self._err(msg)
        for name, val in [('left', left), ('top', top), ('right', right), ('bottom', bottom)]:
            ok, msg = self._validate_number(val, name, min_val=0)
            if not ok: return self._err(msg)
        if int(right) <= int(left) or int(bottom) <= int(top):
            return self._err('Crop box invalid: right must be > left and bottom must be > top.')
        out = self.save_dialog('.png', 'Image File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(img_core.crop_image, input_path, out, int(left), int(top), int(right), int(bottom), success_msg="Image cropped!")

    def run_rotate_image(self, input_path, degrees):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._IMG_EXTS, 'image')
        if not ok: return self._err(msg)
        ok, msg = self._validate_number(degrees, 'degrees', min_val=-360, max_val=360)
        if not ok: return self._err(msg)
        out = self.save_dialog('.png', 'Image File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(img_core.rotate_image, input_path, out, int(degrees), success_msg="Image rotated!")

    def run_flip_image(self, input_path, direction):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._IMG_EXTS, 'image')
        if not ok: return self._err(msg)
        if str(direction).strip().lower() not in ('horizontal', 'vertical'):
            return self._err('Direction must be "horizontal" or "vertical".')
        out = self.save_dialog('.png', 'Image File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(img_core.flip_image, input_path, out, direction, success_msg="Image flipped!")

    def run_enlarge_image(self, input_path, scale):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._IMG_EXTS, 'image')
        if not ok: return self._err(msg)
        ok, msg = self._validate_number(scale, 'scale', min_val=0.01, max_val=100, allow_float=True)
        if not ok: return self._err(msg)
        out = self.save_dialog('.png', 'Image File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(img_core.enlarge_image, input_path, out, float(scale), success_msg="Image enlarged!")

    def run_make_gif(self, image_paths, duration):
        ok, msg = self._validate_paths(image_paths, self._IMG_EXTS, 'image')
        if not ok: return self._err(msg)
        ok, msg = self._validate_number(duration, 'duration', min_val=1, max_val=60000)
        if not ok: return self._err(msg)
        out = self.save_dialog('.gif', 'GIF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(img_core.make_gif, image_paths, out, int(duration), success_msg="GIF created!")

    # ── Tool Runners: PDF ──

    def run_img_to_pdf(self, img_paths):
        ok, msg = self._validate_paths(img_paths, self._IMG_EXTS, 'image')
        if not ok: return self._err(msg)
        out = self.save_dialog('.pdf', 'PDF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(pdf_core.img_to_pdf, img_paths, out, success_msg="PDF created!")

    def run_pdf_to_img(self, pdf_path, output_folder):
        ok, msg = self._validate_path(pdf_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(pdf_path, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        return self._run_tool(pdf_core.pdf_to_img, pdf_path, output_folder, success_msg="Images extracted!")

    def run_compress_pdf(self, input_pdf):
        ok, msg = self._validate_path(input_pdf)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_pdf, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        out = self.save_dialog('.pdf', 'PDF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(pdf_core.compress_pdf, input_pdf, out, success_msg="PDF compressed!")

    def run_merge_pdfs(self, input_paths):
        ok, msg = self._validate_paths(input_paths, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        if len(input_paths) < 2:
            return self._err('Please select at least 2 PDF files to merge.')
        out = self.save_dialog('.pdf', 'PDF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(pdf_core.merge_pdfs, input_paths, out, success_msg="PDFs merged!")

    def run_split_pdf(self, input_path, output_folder):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        return self._run_tool(pdf_core.split_pdf, input_path, output_folder, success_msg="PDF split!")

    def run_flatten_pdf(self, input_path):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        out = self.save_dialog('.pdf', 'PDF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(pdf_core.flatten_pdf, input_path, out, success_msg="PDF flattened!")

    def run_resize_pdf(self, input_path, width_pt, height_pt):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        ok, msg = self._validate_number(width_pt, 'width_pt', min_val=1, max_val=5000, allow_float=True)
        if not ok: return self._err(msg)
        ok, msg = self._validate_number(height_pt, 'height_pt', min_val=1, max_val=5000, allow_float=True)
        if not ok: return self._err(msg)
        out = self.save_dialog('.pdf', 'PDF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(pdf_core.resize_pdf, input_path, out, float(width_pt), float(height_pt), success_msg="PDF resized!")

    def run_unlock_pdf(self, input_path, password):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        out = self.save_dialog('.pdf', 'PDF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(pdf_core.unlock_pdf, input_path, out, password, success_msg="PDF unlocked!")

    def run_rotate_pdf(self, input_path, degrees):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        ok, msg = self._validate_number(degrees, 'degrees', min_val=0, max_val=360)
        if not ok: return self._err(msg)
        if int(degrees) not in (0, 90, 180, 270):
            return self._err('"degrees" must be 0, 90, 180 or 270.')
        out = self.save_dialog('.pdf', 'PDF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(pdf_core.rotate_pdf, input_path, out, int(degrees), success_msg="PDF rotated!")

    def run_protect_pdf(self, input_path, password):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        if not password or len(str(password).strip()) < 4:
            return self._err('Password must be at least 4 characters.')
        out = self.save_dialog('.pdf', 'PDF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(pdf_core.protect_pdf, input_path, out, password, success_msg="PDF protected!")

    def run_crop_pdf(self, input_path, left, top, right, bottom):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        for name, val in [('left_pct', left), ('top_pct', top), ('right_pct', right), ('bottom_pct', bottom)]:
            ok, msg = self._validate_number(val, name, min_val=0, max_val=100, allow_float=True)
            if not ok: return self._err(msg)
        if float(left) + float(right) >= 100 or float(top) + float(bottom) >= 100:
            return self._err('Crop percentages too large — nothing would remain after cropping.')
        out = self.save_dialog('.pdf', 'PDF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(pdf_core.crop_pdf, input_path, out, float(left), float(top), float(right), float(bottom), success_msg="PDF cropped!")

    def run_organize_pdf(self, input_path, order_str):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        out = self.save_dialog('.pdf', 'PDF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        try:
            order = [int(p.strip()) - 1 for p in order_str.split(',') if p.strip()]
        except ValueError:
            return {'success': False, 'msg': 'Invalid page order format.'}
        return self._run_tool(pdf_core.organize_pdf, input_path, out, order, success_msg="PDF organized!")
        
    def run_remove_pages(self, input_path, pages_str):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        out = self.save_dialog('.pdf', 'PDF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        try:
            pages = [int(p.strip()) - 1 for p in pages_str.split(',') if p.strip()]
        except ValueError:
            return {'success': False, 'msg': 'Invalid page numbers format.'}
        return self._run_tool(pdf_core.remove_pages, input_path, out, pages, success_msg="Pages removed!")

    def run_extract_pages(self, input_path, ranges_str):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        out = self.save_dialog('.pdf', 'PDF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        try:
            ranges = []
            for part in ranges_str.split(','):
                part = part.strip()
                if not part: continue
                if '-' in part:
                    start, end = part.split('-')
                    ranges.append((int(start) - 1, int(end) - 1))
                else:
                    ranges.append((int(part) - 1, int(part) - 1))
        except ValueError:
            return {'success': False, 'msg': 'Invalid page ranges format.'}
        return self._run_tool(pdf_core.extract_pages, input_path, out, ranges, success_msg="Pages extracted!")

    def run_extract_images_from_pdf(self, input_path, output_folder):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        return self._run_tool(pdf_core.extract_images_from_pdf, input_path, output_folder, success_msg="Images extracted from PDF!")

    # ── Office → PDF ──
    def run_word_to_pdf(self, input_path):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._DOCX_EXTS, 'Word Document')
        if not ok: return self._err(msg)
        out = self.save_dialog('.pdf', 'PDF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(office_to_pdf_core.word_to_pdf, input_path, out, success_msg="Word converted!")

    def run_excel_to_pdf(self, input_path):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._XLSX_EXTS, 'Excel Document')
        if not ok: return self._err(msg)
        out = self.save_dialog('.pdf', 'PDF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(office_to_pdf_core.excel_to_pdf, input_path, out, success_msg="Excel converted!")

    def run_ppt_to_pdf(self, input_path):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._PPTX_EXTS, 'PowerPoint Document')
        if not ok: return self._err(msg)
        out = self.save_dialog('.pdf', 'PDF File')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(office_to_pdf_core.ppt_to_pdf, input_path, out, success_msg="PowerPoint converted!")

    # ── PDF → Office ──
    def run_pdf_to_word(self, input_path):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        out = self.save_dialog('.docx', 'Word Document')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(pdf_to_office_core.pdf_to_word, input_path, out, success_msg="Converted to Word!")

    def run_pdf_to_excel(self, input_path):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        out = self.save_dialog('.xlsx', 'Excel Spreadsheet')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(pdf_to_office_core.pdf_to_excel, input_path, out, success_msg="Converted to Excel!")

    def run_pdf_to_ppt(self, input_path):
        ok, msg = self._validate_path(input_path)
        if not ok: return self._err(msg)
        ok, msg = self._validate_ext(input_path, self._PDF_EXTS, 'PDF')
        if not ok: return self._err(msg)
        out = self.save_dialog('.pptx', 'PowerPoint Presentation')
        if not out: return {'success': False, 'msg': 'Cancelled'}
        return self._run_tool(pdf_to_office_core.pdf_to_ppt, input_path, out, success_msg="Converted to PowerPoint!")


if __name__ == '__main__':
    api = Api()

    if getattr(sys, 'frozen', False):
        url = os.path.join(sys._MEIPASS, 'ui', 'dist', 'index.html')
    else:
        dist_path = os.path.join(os.path.dirname(__file__), 'ui', 'dist', 'index.html')
        url = dist_path if os.path.exists(dist_path) else 'http://localhost:5173'

    window = webview.create_window(
        'AllTools',
        url=url,
        js_api=api,
        width=1000,
        height=680,
        min_size=(800, 560),
        background_color='#09090b'
    )
    api.set_window(window)
    webview.start()
