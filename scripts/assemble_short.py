import os
import subprocess
from pathlib import Path

os.makedirs("output", exist_ok=True)

frames_pattern = "build/frames/frame_%04d.png"
out_file = "output/test_short.mp4"

if not any(Path("build/frames").glob("*.png")):
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x111827:s=1080x1920:d=3:r=24",
        "-vf", "drawtext=text='NO FRAMES FOUND':fontcolor=white:fontsize=80:borderw=6:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        out_file,
    ]
else:
    # Scale to 1080x1920 and swap bold centered captions across the 3 cuts
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "drawtext=text='TARGET FIXATION':fontcolor=yellow:fontsize=92:borderw=7:bordercolor=black:x=(w-text_w)/2:y=h*0.64:enable='between(t,0,1.0)',"
        "drawtext=text='THE ONLY TREE':fontcolor=white:fontsize=92:borderw=7:bordercolor=black:x=(w-text_w)/2:y=h*0.64:enable='between(t,1.0,2.0)',"
        "drawtext=text='STEERS RIGHT IN':fontcolor=white:fontsize=92:borderw=7:bordercolor=black:x=(w-text_w)/2:y=h*0.64:enable='between(t,2.0,3.0)'"
    )
    cmd = [
        "ffmpeg", "-y",
        "-framerate", "24",
        "-i", frames_pattern,
        "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
        out_file,
    ]

subprocess.run(cmd, check=True)
