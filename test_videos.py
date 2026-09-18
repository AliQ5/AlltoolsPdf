"""
Comprehensive test script for all video features in video_core.py
Tests trim_video and crop_video with the test video in Test/.

Video: Screen Recording 2026-08-18 105303.mp4
  Duration : 126.89 s
  Size     : 846 x 106 px
  FPS      : 30
"""

import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(__file__))
import video_core

try:
    from moviepy import VideoFileClip
    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DIR    = os.path.join(PROJECT_DIR, "Test")
OUTPUT_DIR  = os.path.join(TEST_DIR, "video_output")
VIDEO       = os.path.join(TEST_DIR, "Screen Recording 2026-08-18 105303.mp4")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Known video properties
VIDEO_DURATION = 126.89
VIDEO_W        = 846
VIDEO_H        = 106

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


def file_exists_and_not_empty(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0


def verify_video_exists(path):
    """Check the output file exists, is non-empty, and is openable."""
    if not file_exists_and_not_empty(path):
        return False, f"Output file missing or empty: {path}"
    if HAS_MOVIEPY:
        try:
            clip = VideoFileClip(path)
            clip.close()
        except Exception as e:
            return False, f"Cannot open video: {e}"
    return True, "OK"


def get_duration(path):
    if not HAS_MOVIEPY:
        return None
    clip = VideoFileClip(path)
    d = clip.duration
    clip.close()
    return d


def get_size(path):
    if not HAS_MOVIEPY:
        return None, None
    clip = VideoFileClip(path)
    w, h = clip.size
    clip.close()
    return w, h


# ── 1. TRIM VIDEO ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("1. TRIM VIDEO")
print("="*60)

# Normal trim: first 10 seconds
trim_out1 = os.path.join(OUTPUT_DIR, "trimmed_0_10.mp4")
def verify_trim_10s(path):
    ok, msg = verify_video_exists(path)
    if not ok: return ok, msg
    d = get_duration(path)
    if d is None: return True, "OK (no moviepy check)"
    # allow ±0.5 s tolerance
    if not (9.0 <= d <= 11.0):
        return False, f"Expected ~10s but got {d:.2f}s"
    return True, f"Duration = {d:.2f}s OK"

run_test(
    "Trim 0s -> 10s (first 10 seconds)",
    video_core.trim_video,
    VIDEO, trim_out1, 0, 10,
    verify=verify_trim_10s
)

# Trim middle segment
trim_out2 = os.path.join(OUTPUT_DIR, "trimmed_30_60.mp4")
def verify_trim_30s(path):
    ok, msg = verify_video_exists(path)
    if not ok: return ok, msg
    d = get_duration(path)
    if d is None: return True, "OK"
    if not (29.0 <= d <= 31.0):
        return False, f"Expected ~30s but got {d:.2f}s"
    return True, f"Duration = {d:.2f}s OK"

run_test(
    "Trim 30s -> 60s (30-second middle segment)",
    video_core.trim_video,
    VIDEO, trim_out2, 30, 60,
    verify=verify_trim_30s
)

# Trim near end
trim_out3 = os.path.join(OUTPUT_DIR, "trimmed_120_126.mp4")
def verify_trim_6s(path):
    ok, msg = verify_video_exists(path)
    if not ok: return ok, msg
    d = get_duration(path)
    if d is None: return True, "OK"
    if not (4.0 <= d <= 8.0):
        return False, f"Expected ~6s but got {d:.2f}s"
    return True, f"Duration = {d:.2f}s OK"

run_test(
    "Trim 120s -> 126s (near end)",
    video_core.trim_video,
    VIDEO, trim_out3, 120, 126,
    verify=verify_trim_6s
)

# Trim single second
trim_out4 = os.path.join(OUTPUT_DIR, "trimmed_5_6.mp4")
run_test(
    "Trim 5s -> 6s (1 second clip)",
    video_core.trim_video,
    VIDEO, trim_out4, 5, 6,
    verify=verify_video_exists
)

# Trim from start
trim_out5 = os.path.join(OUTPUT_DIR, "trimmed_0_5.mp4")
run_test(
    "Trim 0s -> 5s (from very beginning)",
    video_core.trim_video,
    VIDEO, trim_out5, 0, 5,
    verify=verify_video_exists
)


# ── 2. CROP VIDEO ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("2. CROP VIDEO")
print("="*60)

# Full-width half-height crop (top half)
crop_out1 = os.path.join(OUTPUT_DIR, "cropped_full_top_half.mp4")
def verify_crop_full_top(path):
    ok, msg = verify_video_exists(path)
    if not ok: return ok, msg
    w, h = get_size(path)
    if w is None: return True, "OK"
    exp_w, exp_h = VIDEO_W, VIDEO_H // 2
    if (w, h) != (exp_w, exp_h):
        return False, f"Expected {exp_w}x{exp_h} but got {w}x{h}"
    return True, f"Size = {w}x{h} OK"

run_test(
    f"Crop full-width top half (0,0 -> {VIDEO_W},{VIDEO_H//2})",
    video_core.crop_video,
    VIDEO, crop_out1, 0, 0, VIDEO_W, VIDEO_H // 2,
    verify=verify_crop_full_top
)

# Centre crop
cx1, cy1, cx2, cy2 = 200, 20, 650, 90
crop_out2 = os.path.join(OUTPUT_DIR, "cropped_center.mp4")
def verify_crop_center(path):
    ok, msg = verify_video_exists(path)
    if not ok: return ok, msg
    w, h = get_size(path)
    if w is None: return True, "OK"
    exp_w, exp_h = cx2 - cx1, cy2 - cy1
    if (w, h) != (exp_w, exp_h):
        return False, f"Expected {exp_w}x{exp_h} but got {w}x{h}"
    return True, f"Size = {w}x{h} OK"

run_test(
    f"Crop centre region ({cx1},{cy1} -> {cx2},{cy2})",
    video_core.crop_video,
    VIDEO, crop_out2, cx1, cy1, cx2, cy2,
    verify=verify_crop_center
)

# Left quarter crop
crop_out3 = os.path.join(OUTPUT_DIR, "cropped_left_quarter.mp4")
def verify_crop_left_q(path):
    ok, msg = verify_video_exists(path)
    if not ok: return ok, msg
    w, h = get_size(path)
    if w is None: return True, "OK"
    exp_w = VIDEO_W // 4
    if w != exp_w:
        return False, f"Expected width {exp_w} but got {w}"
    return True, f"Width = {w} OK"

run_test(
    f"Crop left quarter (0,0 -> {VIDEO_W//4},{VIDEO_H})",
    video_core.crop_video,
    VIDEO, crop_out3, 0, 0, VIDEO_W // 4, VIDEO_H,
    verify=verify_crop_left_q
)

# Right quarter crop
crop_out4 = os.path.join(OUTPUT_DIR, "cropped_right_quarter.mp4")
run_test(
    f"Crop right quarter ({VIDEO_W*3//4},0 -> {VIDEO_W},{VIDEO_H})",
    video_core.crop_video,
    VIDEO, crop_out4, VIDEO_W * 3 // 4, 0, VIDEO_W, VIDEO_H,
    verify=verify_video_exists
)

# Small crop (square-ish)
crop_out5 = os.path.join(OUTPUT_DIR, "cropped_small_square.mp4")
run_test(
    "Crop small region (100,10 -> 200,90)",
    video_core.crop_video,
    VIDEO, crop_out5, 100, 10, 200, 90,
    verify=verify_video_exists
)


# ── 3. COMBINED: Trim THEN Crop ───────────────────────────────────────────────
print("\n" + "="*60)
print("3. COMBINED: TRIM then CROP")
print("="*60)

# First trim to 10s, then crop that clip
trim_for_crop = os.path.join(OUTPUT_DIR, "trim_for_crop.mp4")
final_crop    = os.path.join(OUTPUT_DIR, "trim_then_crop.mp4")

def combined_trim_crop(video, trim_out, crop_out):
    video_core.trim_video(video, trim_out, 0, 10)
    video_core.crop_video(trim_out, crop_out, 0, 0, VIDEO_W // 2, VIDEO_H)
    return crop_out

run_test(
    "Trim 0->10s then crop left half (pipeline)",
    combined_trim_crop,
    VIDEO, trim_for_crop, final_crop,
    verify=verify_video_exists
)


# ── 4. EDGE CASES ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("4. EDGE CASES")
print("="*60)

# Very short trim (0.5s)
trim_edge1 = os.path.join(OUTPUT_DIR, "trimmed_0_0.5.mp4")
run_test(
    "Trim 0s -> 0.5s (very short clip)",
    video_core.trim_video,
    VIDEO, trim_edge1, 0, 0.5,
    verify=verify_video_exists
)

# Trim exact last second
trim_edge2 = os.path.join(OUTPUT_DIR, "trimmed_last_second.mp4")
run_test(
    "Trim last second (125->126s)",
    video_core.trim_video,
    VIDEO, trim_edge2, 125, 126,
    verify=verify_video_exists
)

# Narrow crop (just a few rows of pixels)
crop_edge1 = os.path.join(OUTPUT_DIR, "cropped_thin_strip.mp4")
run_test(
    "Crop thin horizontal strip (0,40 -> 846,60)",
    video_core.crop_video,
    VIDEO, crop_edge1, 0, 40, VIDEO_W, 60,
    verify=verify_video_exists
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

print(f"\nOutput videos saved to: {OUTPUT_DIR}")
