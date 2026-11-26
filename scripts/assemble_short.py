import os
import subprocess
from pathlib import Path

os.makedirs("output", exist_ok=True)

frames_pattern = "build/frames/frame_%04d.png"
out_file = "output/test_short.mp4"

# If no frames exist (e.g., local dry run), generate a solid color fallback
if not any(Path("build/frames").glob("*.png")):
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x111827:s=1080x1920:d=3:r=30",
        "-vf", "drawtext=text='TEST SHORT':fontcolor=white:fontsize=90:borderw=6:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        out_file,
    ]
else:
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "drawtext=text='WATCH THIS':fontcolor=white:fontsize=92:borderw=6:bordercolor=black:x=(w-text_w)/2:y=h*0.65"
    )
    cmd = [
        "ffmpeg", "-y",
        "-framerate", "30",
        "-i", frames_pattern,
        "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
        out_file,
    ]

subprocess.run(cmd, check=True)
