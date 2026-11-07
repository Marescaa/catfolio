"""Renderiza las escenas (dist/<pelaje>/<nivel>.gif) a partir de assets/gatos.

    python tools/render.py            # todos los pelajes
    python tools/render.py naranja    # solo uno

Escena de 480x176, fondo transparente, loop continuo. El gato (~46x62 px) recorre
el espacio en horizontal y vertical, se detiene en cosas y vuelve al inicio.
"""
import math, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, STEP = 480, 176, 100  # lienzo y ms por frame
COATS = ["gris", "naranja", "calico", "siames", "blanco", "esmoquin", "negro", "atigrado"]
LEVELS = ["sleep", "calm", "happy", "joyful"]
PINK = (255, 92, 122, 255)
HEART = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]

# (parada, animacion al llegar)
ROUTES = {
    "calm":   [("C", "sentado"), ("P", "sentado"), ("Y", "sentado"), ("B", "sentado")],
    "happy":  [("C", "sentado"), ("B", "lamiendose"), ("Y", "sentado"), ("Q", "lamiendose"), ("P", "sentado")],
    "joyful": [("C", "sentado"), ("R", "lamiendose"), ("P", "sentado"), ("Y", "lamiendose"),
               ("Q", "sentado"), ("B", "lamiendose")],
}
SPEED = {"calm": 3.0, "happy": 3.5, "joyful": 4.0}     # px por frame
HEARTS = {"calm": 0, "happy": 2, "joyful": 4}
STOPS = {"C": (70, 150), "Y": (350, 128), "B": (222, 164), "P": (200, 112), "Q": (430, 166), "R": (120, 118)}


# ---------- sprites ----------
def half(im):  # el arte original esta a 2x
    return im.convert("RGBA").resize((im.width // 2, im.height // 2), Image.NEAREST)

def load(coat, anim):
    im = Image.open(f"{ROOT}/assets/gatos/{coat}/{anim}.gif")
    frames = []
    for i in range(im.n_frames):
        im.seek(i)
        frames.append((half(im), im.info.get("duration", 100)))
    return frames

def clip(coat, anim, walk=False):
    raw = load(coat, anim)
    boxes = [f.getbbox() for f, _ in raw if f.getbbox()]
    box = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
    imgs = [f.crop(box) for f, _ in raw]
    if walk:  # ciclo corto (50 ms/frame) -> muestreo a 100 ms
        return imgs
    seq = []
    for im, (_, d) in zip(imgs, raw):
        seq += [im] * max(1, round(d / STEP))
    return seq


# ---------- dibujo ----------
def rect(c, x, y, w, h, col):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if 0 <= xx < W and 0 <= yy < H:
                c.putpixel((xx, yy), col)

def cushion(c, x, y):
    rect(c, x - 22, y - 8, 44, 8, (196, 108, 140, 255)); rect(c, x - 18, y - 11, 36, 3, (224, 140, 170, 255))

def yarn(c, x, y):
    for dy in range(-9, 1):
        for dx in range(-9, 10):
            if dx * dx + (dy + 5) ** 2 <= 20:
                c.putpixel((x + dx, y + dy), (92, 140, 220, 255))
    rect(c, x - 3, y - 7, 6, 1, (150, 185, 245, 255)); rect(c, x + 9, y - 1, 10, 1, (92, 140, 220, 255))

def bowl(c, x, y):
    rect(c, x - 9, y - 6, 18, 6, (120, 130, 150, 255)); rect(c, x - 7, y - 7, 14, 2, (210, 170, 110, 255))

PROPS = [(cushion, 70, 150), (yarn, 390, 128), (bowl, 250, 164)]

def heart(c, x, y):
    for r, row in enumerate(HEART):
        for k, v in enumerate(row):
            if v == "1" and 0 <= x + k < W and 0 <= y + r < H:
                c.putpixel((x + k, y + r), PINK)

def compose(spr, x, y, flip, extra=None):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s = spr.transpose(Image.FLIP_LEFT_RIGHT) if flip else spr
    pos = (int(x - s.width / 2), int(y - s.height))
    drew = False
    for fn, px, py in sorted(PROPS, key=lambda p: p[2]):  # el que esta mas atras se dibuja primero
        if not drew and py > y:
            c.alpha_composite(s, pos); drew = True
        fn(c, px, py)
    if not drew:
        c.alpha_composite(s, pos)
    if extra:
        extra(c, s)
    return c


# ---------- escenas ----------
def scene_sleep(coat):
    seq = clip(coat, "dormido")
    cx, cy = STOPS["C"][0], STOPS["C"][1] - 6
    return [compose(s, cx, cy, False) for s in seq]

def scene_walk(coat, level):
    idle = {a: clip(coat, a) for a in ("sentado", "lamiendose")}
    walk = clip(coat, "caminando", walk=True)
    stops, speed = ROUTES[level], SPEED[level]
    steps, wi = [], 0                      # (x, y, flip, sprite, beat)
    for i, (s, anim) in enumerate(stops):
        x0, y0 = STOPS[s]
        for k, spr in enumerate(idle[anim]):
            steps.append((x0, y0, False, spr, HEARTS[level] > 0 and k == 3))
        x1, y1 = STOPS[stops[(i + 1) % len(stops)][0]]
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / speed))
        for k in range(n):
            p = (k + 1) / n
            steps.append((x0 + (x1 - x0) * p, y0 + (y1 - y0) * p, x1 < x0, walk[(wi * 2) % len(walk)], False)); wi += 1
    total, nh = len(steps), HEARTS[level]
    beats = [t for t, s in enumerate(steps) if s[4]]
    frames = []
    for t, (x, y, flip, spr, _) in enumerate(steps):
        def hearts(c, s, t=t, x=x, y=y):
            for b in beats:
                for k in range(nh):
                    age = (t - b - k * 4) % total
                    if age < 18:
                        p = age / 18
                        heart(c, int(x - 3 + (k - nh / 2) * 7 + 5 * math.sin(p * 6 + k)), int(y - s.height - 6 - p * 26))
        frames.append(compose(spr, x, y, flip, hearts if nh else None))
    return frames

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
