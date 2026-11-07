"""Builds docs/coats-light.png and docs/coats-dark.png: every coat in every state."""
import os, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R

STATES = ["sleep", "small", "medium", "large"]
CELL_W, CELL_H, LABEL_W, HEAD_H, PAD = 150, 150, 90, 34, 8

def font(size):
    for name in ("DejaVuSans.ttf", "arial.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()

def still(coat, state):
    if state == "sleep":
        return R.clip(coat, "sleeping", R.SCALE["sleep"])[0]
    return R.clip(coat, "sitting", R.SCALE[state])[0]

def sheet(dark):
    bg, fg, muted = ((13, 17, 23), (230, 237, 243), (139, 151, 168)) if dark else ((255, 255, 255), (28, 35, 48), (91, 102, 120))
    w = LABEL_W + CELL_W * len(STATES) + PAD * 2
    h = HEAD_H + CELL_H * len(R.COATS) + PAD * 2
    im = Image.new("RGBA", (w, h), bg + (255,))
    d = ImageDraw.Draw(im)
    f, fb = font(15), font(14)
    for j, s in enumerate(STATES):
        d.text((PAD + LABEL_W + j * CELL_W + CELL_W / 2, PAD + 10), s, fill=fg, font=f, anchor="mm")
    for i, coat in enumerate(R.COATS):
        y0 = PAD + HEAD_H + i * CELL_H
        d.text((PAD + 8, y0 + CELL_H / 2), coat, fill=muted, font=fb, anchor="lm")
        if i:
            d.line([(PAD, y0), (w - PAD, y0)], fill=(42, 51, 64) if dark else (217, 222, 230))
        for j, s in enumerate(STATES):
            spr = still(coat, s)
            im.alpha_composite(spr, (int(PAD + LABEL_W + j * CELL_W + (CELL_W - spr.width) / 2),
                                     int(y0 + CELL_H - 12 - spr.height)))
    return im.convert("RGB")

if __name__ == "__main__":
    out = os.path.join(R.ROOT, "docs")
    os.makedirs(out, exist_ok=True)
    sheet(False).save(f"{out}/coats-light.png", optimize=True)
    sheet(True).save(f"{out}/coats-dark.png", optimize=True)
    print("ok")
