# =============================================================================
# AllTools — Image Core Operations
# Author  : Ali Qureshi
# License : MIT
# =============================================================================
import os
from PIL import Image, ImageSequence

def convert_image(input_path, output_format, output_folder):
    """Convert an image to the specified output format."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    fmt = output_format.lower().replace('.', '')
    output_path = os.path.join(output_folder, f"{base_name}.{fmt}")
    img = Image.open(input_path)
    if fmt in ['jpg', 'jpeg'] and img.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        mask = img.split()[3] if len(img.split()) == 4 else None
        bg.paste(img, mask=mask)
        img = bg
    img.save(output_path)
    return output_path

def resize_image(input_path, output_path, width, height):
    """Resize image to given dimensions (px)."""
    img = Image.open(input_path)
    img = img.resize((int(width), int(height)), Image.LANCZOS)
    img.save(output_path)
    return output_path

def crop_image(input_path, output_path, left, top, right, bottom):
    """Crop image to bounding box."""
    img = Image.open(input_path)
    img = img.crop((int(left), int(top), int(right), int(bottom)))
    img.save(output_path)
    return output_path

def rotate_image(input_path, output_path, degrees):
    """Rotate image by degrees (counter-clockwise)."""
    img = Image.open(input_path)
    img = img.rotate(int(degrees), expand=True)
    img.save(output_path)
    return output_path

def flip_image(input_path, output_path, direction='horizontal'):
    """Flip image horizontally or vertically."""
    img = Image.open(input_path)
    if direction == 'horizontal':
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    else:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_path)
    return output_path

def enlarge_image(input_path, output_path, scale):
    """Scale image by a multiplier (e.g. 2 = 2x)."""
    img = Image.open(input_path)
    w, h = img.size
    img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    img.save(output_path)
    return output_path

def make_gif(image_paths, output_path, duration=500, loop=0):
    """Create an animated GIF from a list of images."""
    frames = [Image.open(p).convert('RGBA') for p in image_paths]
    if not frames:
        raise ValueError("No images provided.")
    frames[0].save(
        output_path,
        format='GIF',
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=loop
    )
    return output_path
