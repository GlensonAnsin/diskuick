"""The one Diskuick logo, drawn in code so every place that shows it stays identical:
exe file icon (.ico), tray icon, window icon and in-app header.

    render_logo(size)            -> the plain logo
    render_logo(size, "active")  -> logo + small status badge (used for the tray)
"""
from PIL import Image, ImageChops, ImageDraw, ImageFilter

TOP, BOTTOM = (52, 224, 150), (13, 148, 136)         # green -> teal gradient
BADGE = {"active": (46, 204, 113), "waiting": (250, 204, 21),
         "off": (148, 163, 184), "error": (239, 68, 68)}
# Lightning bolt on a 100x100 grid
BOLT = [(61, 5), (22, 55), (45, 55), (37, 95), (79, 40), (55, 40), (69, 5)]
SS = 4  # supersampling factor for smooth edges


def _gradient(n: int) -> Image.Image:
    v = Image.linear_gradient("L").resize((n, n))                 # black -> white, top to bottom
    g = ImageChops.add(v, v.transpose(Image.TRANSPOSE), scale=2)  # average with left->right = diagonal
    return Image.composite(Image.new("RGB", (n, n), BOTTOM), Image.new("RGB", (n, n), TOP), g)


def render_logo(size: int = 256, state: str | None = None) -> Image.Image:
    n = size * SS
    u = n / 100.0
    pt = lambda p: (p[0] * u, p[1] * u)

    # rounded-square gradient plate
    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, n - 1, n - 1), radius=22 * u, fill=255)
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    img.paste(_gradient(n), (0, 0), mask)

    # faint disk ring behind the bolt (the "disk" in Diskuick), blended on its own layer
    ring = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((12 * u, 12 * u, 88 * u, 88 * u),
                                 outline=(255, 255, 255, 80), width=max(1, int(3.5 * u)))
    img = Image.alpha_composite(img, ring)

    # soft shadow, then the bolt
    sh = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([pt((x + 1.5, y + 2.5)) for x, y in BOLT], fill=(0, 40, 35, 120))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(2 * u)))
    ImageDraw.Draw(img).polygon([pt(p) for p in BOLT], fill=(255, 255, 255, 255))

    if state:  # status badge, bottom-right
        d = ImageDraw.Draw(img)
        cx, cy, r = 76 * u, 76 * u, 17 * u
        d.ellipse((cx - r - 3 * u, cy - r - 3 * u, cx + r + 3 * u, cy + r + 3 * u), fill=(15, 17, 21, 255))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=BADGE.get(state, BADGE["off"]) + (255,))

    return img.resize((size, size), Image.LANCZOS)
