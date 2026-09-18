"""
Comprehensive test script for all image features in img_core.py
Tests all 7 image operations with the 3 test images in the Test/ folder.
"""

import os
import sys
import traceback
from PIL import Image

# Add project root to path so we can import img_core
sys.path.insert(0, os.path.dirname(__file__))
import img_core

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_DIR  = os.path.dirname(os.path.abspath(__file__))
TEST_DIR     = os.path.join(PROJECT_DIR, "Test")
OUTPUT_DIR   = os.path.join(PROJECT_DIR, "Test", "output")

IMG1 = os.path.join(TEST_DIR, "img1.png")  # ~2.5 MB PNG
IMG2 = os.path.join(TEST_DIR, "img2.png")  # ~12 MB PNG
IMG3 = os.path.join(TEST_DIR, "img3.jpg")  # ~370 KB JPG

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
PASS = "  PASS"
FAIL = "  FAIL"

results = []

def run_test(name, func, *args, verify=None):
    """Run a single test case and capture results."""
    try:
        result = func(*args)
        if verify:
            ok, detail = verify(result)
            if not ok:
                raise AssertionError(detail)
        status = PASS
        detail = f"-> {result}"
    except Exception as e:
        status = FAIL
        detail = f"-> {e}"
        traceback.print_exc()

    print(f"{status}  {name}")
    print(f"       {detail}")
    results.append((name, status.strip()))


def file_exists_and_not_empty(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0


def verify_image_exists(path):
    if not file_exists_and_not_empty(path):
        return False, f"Output file missing or empty: {path}"
    try:
        Image.open(path).verify()
        return True, "OK"
    except Exception as e:
        return False, str(e)


# ── 1. Image Convert ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("1. IMAGE CONVERT")
print("="*60)

run_test("Convert img1.png -> JPG",  img_core.convert_image, IMG1, "jpg",  OUTPUT_DIR, verify=lambda p: verify_image_exists(p))
run_test("Convert img2.png -> WEBP", img_core.convert_image, IMG2, "webp", OUTPUT_DIR, verify=lambda p: verify_image_exists(p))
run_test("Convert img3.jpg -> PNG",  img_core.convert_image, IMG3, "png",  OUTPUT_DIR, verify=lambda p: verify_image_exists(p))
run_test("Convert img3.jpg -> BMP",  img_core.convert_image, IMG3, "bmp",  OUTPUT_DIR, verify=lambda p: verify_image_exists(p))
run_test("Convert img1.png -> GIF",  img_core.convert_image, IMG1, "gif",  OUTPUT_DIR, verify=lambda p: verify_image_exists(p))


# ── 2. Resize Image ────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("2. RESIZE IMAGE")
print("="*60)

resize_out1 = os.path.join(OUTPUT_DIR, "img1_resized_800x600.png")
run_test("Resize img1.png -> 800x600", img_core.resize_image, IMG1, resize_out1, 800, 600, verify=lambda p: verify_image_exists(p))

resize_out2 = os.path.join(OUTPUT_DIR, "img3_resized_200x200.png")
run_test("Resize img3.jpg -> 200x200", img_core.resize_image, IMG3, resize_out2, 200, 200, verify=lambda p: verify_image_exists(p))

def verify_size_800x600(path):
    ok, msg = verify_image_exists(path)
    if not ok: return ok, msg
    w, h = Image.open(path).size
    return (True, "OK") if (w, h) == (800, 600) else (False, f"Expected 800x600 but got {w}x{h}")

resize_out3 = os.path.join(OUTPUT_DIR, "img2_resized_800x600.png")
run_test("Resize img2.png -> 800x600 (dimension check)", img_core.resize_image, IMG2, resize_out3, 800, 600, verify=verify_size_800x600)


# ── 3. Crop Image ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("3. CROP IMAGE")
print("="*60)

crop_out1 = os.path.join(OUTPUT_DIR, "img1_cropped.png")
run_test("Crop img1.png (0,0 -> 400,300)", img_core.crop_image, IMG1, crop_out1, 0, 0, 400, 300, verify=lambda p: verify_image_exists(p))

crop_out2 = os.path.join(OUTPUT_DIR, "img3_cropped.png")
run_test("Crop img3.jpg (50,50 -> 200,200)", img_core.crop_image, IMG3, crop_out2, 50, 50, 200, 200, verify=lambda p: verify_image_exists(p))

def verify_crop_size(path):
    ok, msg = verify_image_exists(path)
    if not ok: return ok, msg
    w, h = Image.open(path).size
    return (True, "OK") if (w, h) == (150, 150) else (False, f"Expected 150x150 crop but got {w}x{h}")

crop_out3 = os.path.join(OUTPUT_DIR, "img3_cropped_verify.png")
run_test("Crop img3.jpg (size verify 150x150)", img_core.crop_image, IMG3, crop_out3, 50, 50, 200, 200, verify=verify_crop_size)


# ── 4. Rotate Image ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("4. ROTATE IMAGE")
print("="*60)

for deg in [90, 180, 270, 45]:
    rot_out = os.path.join(OUTPUT_DIR, f"img3_rotated_{deg}.png")
    run_test(f"Rotate img3.jpg by {deg}deg", img_core.rotate_image, IMG3, rot_out, deg, verify=lambda p: verify_image_exists(p))


# ── 5. Flip Image ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("5. FLIP IMAGE")
print("="*60)

flip_h_out = os.path.join(OUTPUT_DIR, "img1_flipped_h.png")
run_test("Flip img1.png horizontally", img_core.flip_image, IMG1, flip_h_out, 'horizontal', verify=lambda p: verify_image_exists(p))

flip_v_out = os.path.join(OUTPUT_DIR, "img1_flipped_v.png")
run_test("Flip img1.png vertically", img_core.flip_image, IMG1, flip_v_out, 'vertical', verify=lambda p: verify_image_exists(p))

flip_jpg_out = os.path.join(OUTPUT_DIR, "img3_flipped_h.png")
run_test("Flip img3.jpg horizontally", img_core.flip_image, IMG3, flip_jpg_out, 'horizontal', verify=lambda p: verify_image_exists(p))


# ── 6. Enlarge Image ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("6. ENLARGE (SCALE) IMAGE")
print("="*60)

enlarge_out1 = os.path.join(OUTPUT_DIR, "img3_2x.png")
run_test("Enlarge img3.jpg x2", img_core.enlarge_image, IMG3, enlarge_out1, 2.0, verify=lambda p: verify_image_exists(p))

enlarge_out2 = os.path.join(OUTPUT_DIR, "img3_0.5x.png")
run_test("Shrink img3.jpg x0.5", img_core.enlarge_image, IMG3, enlarge_out2, 0.5, verify=lambda p: verify_image_exists(p))

def verify_double_size(scaled_path):
    orig_w, orig_h = Image.open(IMG3).size
    ok, msg = verify_image_exists(scaled_path)
    if not ok: return ok, msg
    w, h = Image.open(scaled_path).size
    return (True, "OK") if (w, h) == (orig_w * 2, orig_h * 2) else (False, f"Expected {orig_w*2}x{orig_h*2} but got {w}x{h}")

enlarge_out3 = os.path.join(OUTPUT_DIR, "img3_2x_verify.png")
run_test("Enlarge img3.jpg x2 (dimension check)", img_core.enlarge_image, IMG3, enlarge_out3, 2.0, verify=verify_double_size)


# ── 7. Make GIF ───────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("7. MAKE GIF (Animated)")
print("="*60)

gif_out = os.path.join(OUTPUT_DIR, "animated.gif")
run_test("Create GIF from img1+img3 (500ms)", img_core.make_gif, [IMG1, IMG3], gif_out, 500, verify=lambda p: verify_image_exists(p))

gif_out3 = os.path.join(OUTPUT_DIR, "animated_all3.gif")
run_test("Create GIF from all 3 images (300ms)", img_core.make_gif, [IMG1, IMG2, IMG3], gif_out3, 300, verify=lambda p: verify_image_exists(p))

gif_out_loop = os.path.join(OUTPUT_DIR, "animated_loop.gif")
run_test("Create looping GIF (loop=0, infinite)", img_core.make_gif, [IMG1, IMG3], gif_out_loop, 200, 0, verify=lambda p: verify_image_exists(p))


# ── 8. Edge / Error Cases ─────────────────────────────────────────────────────
print("\n" + "="*60)
print("8. EDGE & ERROR CASES")
print("="*60)

# Alpha-flatten PNG -> JPG
run_test("RGBA PNG -> JPG (alpha flatten, no crash)", img_core.convert_image, IMG1, "jpg", OUTPUT_DIR, verify=lambda p: verify_image_exists(p))

# Extreme small resize
tiny_out = os.path.join(OUTPUT_DIR, "img3_1x1.png")
run_test("Resize img3.jpg -> 1x1 (extreme small)", img_core.resize_image, IMG3, tiny_out, 1, 1, verify=lambda p: verify_image_exists(p))

# 0 degree rotation (no-op)
rot0_out = os.path.join(OUTPUT_DIR, "img3_rot0.png")
run_test("Rotate img3.jpg by 0deg (no-op)", img_core.rotate_image, IMG3, rot0_out, 0, verify=lambda p: verify_image_exists(p))

# Single-image GIF
gif_single_out = os.path.join(OUTPUT_DIR, "single_frame.gif")
run_test("Make GIF from single image", img_core.make_gif, [IMG3], gif_single_out, 1000, verify=lambda p: verify_image_exists(p))


# ── Summary ────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
passed = sum(1 for _, s in results if "PASS" in s)
failed = sum(1 for _, s in results if "FAIL" in s)
total  = len(results)

print(f"  Total : {total}")
print(f"  Pass  : {passed}")
print(f"  Fail  : {failed}")
print()

if failed:
    print("Failed tests:")
    for name, status in results:
        if "FAIL" in status:
            print(f"  - {name}")
else:
    print("All tests passed!")

print(f"\nOutput images saved to: {OUTPUT_DIR}")
