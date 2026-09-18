"""
Generates the AllTools.ico app icon using Pillow.
Run this once: python generate_icon.py
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    sizes = [16, 32,48, 64, 128, 256]
    images = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (24, 24, 27, 255))  # zinc-900
        draw = ImageDraw.Draw(img)

        pad = size * 0.12
        mid = size / 2
        
        # --- Draw two document shapes with an arrow ---
        # Left doc
        doc_w = size * 0.28
        doc_h = size * 0.38
        fold = size * 0.07
        
        x0 = pad
        y0 = mid - doc_h / 2
        x1 = x0 + doc_w
        y1 = y0 + doc_h

        # doc body (zinc-600 gray)
        draw.polygon([
            (x0, y0 + fold),
            (x0 + fold, y0),
            (x1, y0),
            (x1, y1),
            (x0, y1)
        ], fill=(82, 82, 91, 255))

        # fold corner
        draw.polygon([
            (x0, y0 + fold),
            (x0 + fold, y0),
            (x0 + fold, y0 + fold)
        ], fill=(113, 113, 122, 255))

        # doc lines (zinc-400)
        lc = (161, 161, 170, 200)
        lpad = size * 0.05
        ls = y0 + fold + lpad
        step = (y1 - ls - lpad) / 3
        for i in range(3):
            ly = ls + i * step
            draw.line([(x0 + lpad, ly), (x1 - lpad, ly)], fill=lc, width=max(1, int(size * 0.025)))

        # Right doc (blue)
        rx0 = size - pad - doc_w
        ry0 = y0
        rx1 = size - pad
        ry1 = y1

        draw.polygon([
            (rx0, ry0 + fold),
            (rx0 + fold, ry0),
            (rx1, ry0),
            (rx1, ry1),
            (rx0, ry1)
        ], fill=(59, 130, 246, 255))  # blue-500

        draw.polygon([
            (rx0, ry0 + fold),
            (rx0 + fold, ry0),
            (rx0 + fold, ry0 + fold)
        ], fill=(96, 165, 250, 255))  # blue-400

        # Arrow in center (white)
        arr_cx = mid
        arr_cy = mid
        arr_w = size * 0.12
        arr_h = size * 0.1
        tip_x = arr_cx + arr_w / 2
        tail_x = arr_cx - arr_w / 2
        half_h = arr_h / 2
        head_h = arr_h * 0.8

        draw.polygon([
            (tail_x, arr_cy - half_h * 0.5),
            (arr_cx, arr_cy - half_h * 0.5),
            (arr_cx, arr_cy - half_h),
            (tip_x, arr_cy),
            (arr_cx, arr_cy + half_h),
            (arr_cx, arr_cy + half_h * 0.5),
            (tail_x, arr_cy + half_h * 0.5),
        ], fill=(255, 255, 255, 255))

        images.append(img)

    # Save as ICO with all sizes
    images[0].save(
        "alltools.ico",
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )
    print("alltools.ico created successfully!")

if __name__ == "__main__":
    create_icon()
