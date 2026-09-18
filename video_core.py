# =============================================================================
# AllTools — Video Core Operations
# Author  : Ali Qureshi
# License : MIT
# =============================================================================
import os
from moviepy import VideoFileClip

def trim_video(input_path, output_path, start_sec, end_sec):
    """Trim a video between start and end seconds."""
    clip = VideoFileClip(input_path).subclipped(start_sec, end_sec)
    clip.write_videofile(output_path, logger=None)
    clip.close()
    return output_path

def crop_video(input_path, output_path, x1, y1, x2, y2):
    """Crop a video to a bounding box (x1,y1) -> (x2,y2) in pixels."""
    clip = VideoFileClip(input_path).cropped(x1=x1, y1=y1, x2=x2, y2=y2)
    clip.write_videofile(output_path, logger=None)
    clip.close()
    return output_path
