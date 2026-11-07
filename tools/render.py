"""Renderiza las escenas (dist/<pelaje>/<estado>.gif) a partir de assets/gatos.

    python tools/render.py            # todos los pelajes
    python tools/render.py naranja    # solo uno

Escena de 480x200, fondo transparente y vacia, loop continuo. Con 0 commits el gato
duerme; con mas, camina por todo el espacio (horizontal y vertical), se sienta de vez
en cuando, y cuanto mas commits, mas grande es.
"""
import math, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, STEP = 480, 200, 100  # lienzo y ms por frame
COATS = ["gris", "naranja", "calico", "siames", "blanco", "esmoquin", "negro", "atigrado"]
LEVELS = ["sleep", "small", "medium", "large"]
SCALE = {"sleep": 1.0, "small": 1.0, "medium": 1.5, "large": 2.0}   # 1.0 = sprite a mitad del original
SLEEP_AT = (240, 192)

# Ruta normalizada (fx, fy, animacion | None); fx/fy en 0..1 sobre el area que le queda
# libre al gato segun su tamano. Cierra el ciclo sola.
ROUTE = [(0.08, 0.95, "sentado"), (0.35, 0.15, None), (0.62, 0.65, None), (0.92, 0.1, "sentado"),
         (0.95, 0.95, None), (0.55, 0.9, "sentado"), (0.22, 0.5, None)]


# ---------- sprites ----------
def load(coat, anim, scale):
    """Frames recortados al bbox comun, escalados (NEAREST). El arte original esta a 2x."""
    im = Image.open(f"{ROOT}/assets/gatos/{coat}/{anim}.gif")
    raw = []
    for i in range(im.n_frames):
        im.seek(i)
        raw.append((im.convert("RGBA"), im.info.get("duration", 100)))
    boxes = [f.getbbox() for f, _ in raw if f.getbbox()]
    box = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
    out = []
    for f, d in raw:
        c = f.crop(box)
        out.append((c.resize((round(c.width * scale / 2), round(c.height * scale / 2)), Image.NEAREST), d))
    return out

def clip(coat, anim, scale, walk=False):
    raw = load(coat, anim, scale)
    if walk:  # ciclo corto (50 ms/frame): se muestrea cada 100 ms
        return [f for f, _ in raw]
    seq = []
    for im, (_, d) in zip([f for f, _ in raw], raw):
        seq += [im] * max(1, round(d / STEP))
    return seq


# ---------- escenas ----------
def compose(spr, x, y, flip):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s = spr.transpose(Image.FLIP_LEFT_RIGHT) if flip else spr
    c.alpha_composite(s, (int(x - s.width / 2), int(y - s.height)))
    return c

def scene_sleep(coat):
    return [compose(s, SLEEP_AT[0], SLEEP_AT[1], False) for s in clip(coat, "dormido", SCALE["sleep"])]

def scene_walk(coat, level):
    k = SCALE[level]
    sit, walk = clip(coat, "sentado", k), clip(coat, "caminando", k, walk=True)
    sw, sh = max(f.width for f in sit + walk), max(f.height for f in sit + walk)
    xa, xb = sw / 2 + 6, W - sw / 2 - 6          # area libre de los pies
    ya, yb = sh + 4, H - 4
    pts = [(xa + fx * (xb - xa), ya + fy * (yb - ya), a) for fx, fy, a in ROUTE]
    speed = 3.0 * k
    steps, wi = [], 0
    for i, (x0, y0, anim) in enumerate(pts):
        if anim:
            steps += [(x0, y0, False, spr) for spr in sit]
        x1, y1, _ = pts[(i + 1) % len(pts)]
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / speed))
        for j in range(n):
            p = (j + 1) / n
            steps.append((x0 + (x1 - x0) * p, y0 + (y1 - y0) * p, x1 < x0, walk[(wi * 2) % len(walk)])); wi += 1
    return [compose(spr, x, y, flip) for x, y, flip, spr in steps]


def save(frames, path):
    rgb = []
    for f in frames:
        bg = Image.new("RGB", f.size, (255, 0, 255)); bg.paste(f, mask=f.split()[3]); rgb.append(bg)
    mont = Image.new("RGB", (W, H * len(rgb)))
    for i, r in enumerate(rgb):
        mont.paste(r, (0, i * H))
    pal = mont.quantize(255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    outs = []
    for f, r in zip(frames, rgb):
        q = r.quantize(palette=pal, dither=Image.Dither.NONE)
        px, a = q.load(), f.split()[3].load()
        for yy in range(H):
            for xx in range(W):
                if a[xx, yy] < 128:
                    px[xx, yy] = 255
        outs.append(q)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    outs[0].save(path, save_all=True, append_images=outs[1:], duration=STEP, loop=0,
                 transparency=255, disposal=2, optimize=False)


def main(coats):
    for coat in coats:
        for level in LEVELS:
            frames = scene_sleep(coat) if level == "sleep" else scene_walk(coat, level)
            save(frames, f"{ROOT}/dist/{coat}/{level}.gif")
        print("ok", coat)

if __name__ == "__main__":
    main(sys.argv[1:] or COATS)
