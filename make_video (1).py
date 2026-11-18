"""Burns the text onto the diya video and keeps the original song untouched.
Needs: Python 3, Pillow (pip install pillow) and ffmpeg.
Run:   python make_video.py input.mp4 diyas_spark.mp4
"""
import subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC = sys.argv[1] if len(sys.argv) > 1 else "diyas.mp4"
OUT = sys.argv[2] if len(sys.argv) > 2 else "diyas_spark.mp4"
TEXT = "this is exactly how you brought back my spark"
BUTTER = (251, 240, 190)          # butter yellow #FBF0BE
NIGHT = (18, 13, 41)              # dark indigo used for the soft fade
# Palatino-style font. Change this path to any italic serif font on your computer.
FONT = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrepagella-bolditalic.otf"

# 1. read the video size
w, h = map(int, subprocess.check_output(
    ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
     "stream=width,height", "-of", "csv=p=0", SRC], text=True).strip().split(","))

# 2. make one transparent picture: soft dark fade at the bottom + the text
layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
fade_h = int(h * 0.30)
for i in range(fade_h):
    alpha = int(166 * (i / fade_h))            # 0 at the top of the fade, 65% at the bottom
    ImageDraw.Draw(layer).line([(0, h - fade_h + i), (w, h - fade_h + i)], fill=NIGHT + (alpha,))
font = ImageFont.truetype(FONT, int(w * 0.036))
box = ImageDraw.Draw(layer).textbbox((0, 0), TEXT, font=font)
x, y = (w - (box[2] - box[0])) // 2 - box[0], int(h * 0.94) - box[3]
shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
ImageDraw.Draw(shadow).text((x, y + 3), TEXT, font=font, fill=(0, 0, 0, 190))
layer = Image.alpha_composite(layer, shadow.filter(ImageFilter.GaussianBlur(7)))
ImageDraw.Draw(layer).text((x, y), TEXT, font=font, fill=BUTTER + (255,))
layer.save("text_layer.png")

# 3. put it on the video; -c:a copy keeps the music exactly as it was
subprocess.run(["ffmpeg", "-y", "-i", SRC, "-i", "text_layer.png",
                "-filter_complex", "[0:v][1:v]overlay=0:0,format=yuv420p[v]",
                "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "17",
                "-preset", "slow", "-c:a", "copy", "-movflags", "+faststart", OUT], check=True)
print("Saved", OUT)
