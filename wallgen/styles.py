"""生成艺术风格引擎 —— 每种风格返回一张 PIL Image。"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .palettes import sample_gradient


def _noise(x, y, seed):
    """轻量伪流场噪声（无需外部依赖），返回弧度角。"""
    return (np.sin(x * 1.7 + seed) + np.cos(y * 1.3 - seed * 0.7)
            + np.sin((x + y) * 0.9 + seed * 1.3)) * math.pi


# ---------------------------------------------------------------------------
# 1. 流场粒子 —— 成千上万粒子顺着噪声场流动，留下发光轨迹
# ---------------------------------------------------------------------------
def flow_field(w, h, palette, seed, particles=900, steps=400):
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", (w, h), (12, 12, 20))
    draw = ImageDraw.Draw(img, "RGBA")

    px = rng.uniform(0, w, particles)
    py = rng.uniform(0, h, particles)
    ct = rng.uniform(0, 1, particles)

    scale = 0.0022
    for _ in range(steps):
        ang = _noise(px * scale, py * scale, seed)
        nx = px + np.cos(ang) * 2.2
        ny = py + np.sin(ang) * 2.2
        # 每段线段按粒子色采样
        for i in range(particles):
            c = sample_gradient(palette, ct[i])
            a = int(28)
            draw.line([(px[i], py[i]), (nx[i], ny[i])],
                      fill=(int(c[0]), int(c[1]), int(c[2]), a))
        px, ny_ = nx, ny
        py = ny_
        # 出界重生
        mask = (px < 0) | (px > w) | (py < 0) | (py > h)
        px[mask] = rng.uniform(0, w, mask.sum())
        py[mask] = rng.uniform(0, h, mask.sum())
        ct[mask] = rng.uniform(0, 1, mask.sum())

    img = img.filter(ImageFilter.GaussianBlur(0.6))
    return img


# ---------------------------------------------------------------------------
# 2. 极光 —— 一条条柔和的彩色光带起伏飘动
# ---------------------------------------------------------------------------
def aurora(w, h, palette, seed, bands=6):
    rng = np.random.default_rng(seed)
    y = np.linspace(0, h, h)
    x = np.linspace(0, w, w)
    xx, yy = np.meshgrid(x, y)

    arr = np.zeros((h, w, 3), dtype=np.float64)
    weight = np.zeros((h, w, 1), dtype=np.float64)
    for b in range(bands):
        cy = rng.uniform(h * 0.15, h * 0.85)
        amp = rng.uniform(40, 140)
        freq = rng.uniform(0.002, 0.006)
        phase = rng.uniform(0, math.tau)
        band_y = cy + amp * np.sin(xx * freq + phase)
        spread = rng.uniform(30, 90)
        d = np.exp(-((yy - band_y) ** 2) / (2 * spread ** 2))
        t = (b + 0.5) / bands
        col = sample_gradient(palette, t)
        arr += d[..., None] * col[None, None, :]
        weight += d[..., None]

    # 加一个深邃底色
    base = np.array([8, 10, 24], dtype=np.float64)
    arr = arr / (weight + 1e-6)
    arr = np.where(weight > 0.02, arr, base)
    arr = np.clip(arr, 0, 255).astype(np.uint8)

    # 加点星星
    img = Image.fromarray(arr, "RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(120):
        sx, sy = rng.uniform(0, w), rng.uniform(0, h * 0.6)
        r = rng.uniform(0.4, 1.6)
        draw.ellipse([sx - r, sy - r, sx + r, sy + r],
                     fill=(255, 255, 255, int(rng.uniform(80, 200))))
    return img.filter(ImageFilter.GaussianBlur(0.4))


# ---------------------------------------------------------------------------
# 3. 曼陀罗 —— 中心对称的几何花纹
# ---------------------------------------------------------------------------
def mandala(w, h, palette, seed, rays=24, rings=12):
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", (w, h), (8, 8, 14))
    draw = ImageDraw.Draw(img, "RGBA")
    cx, cy = w / 2, h / 2
    max_r = min(w, h) * 0.48

    for r in range(rings):
        rad = max_r * (r + 1) / rings
        t = r / rings
        col = sample_gradient(palette, t)
        alpha = int(200 - 120 * (r / rings))
        # 每格花瓣：交替画扇形填充 + 放射线
        for k in range(rays):
            a0 = math.tau * k / rays
            a1 = math.tau * (k + 0.5) / rays
            x1 = cx + math.cos(a0) * rad * 0.5
            y1 = cy + math.sin(a0) * rad * 0.5
            x2 = cx + math.cos(a1) * rad
            y2 = cy + math.sin(a1) * rad
            draw.polygon([(cx, cy), (x1, y1), (x2, y2)],
                         fill=(int(col[0]), int(col[1]), int(col[2]), int(alpha * 0.18)))
            draw.line([(cx + math.cos(a0) * rad * 0.5, cy + math.sin(a0) * rad * 0.5),
                       (cx + math.cos(a0) * rad, cy + math.sin(a0) * rad)],
                      fill=(int(col[0]), int(col[1]), int(col[2]), alpha), width=2)
        draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                     outline=(int(col[0]), int(col[1]), int(col[2]), int(alpha * 0.6)),
                     width=2)
    return img.filter(ImageFilter.GaussianBlur(0.6))


# ---------------------------------------------------------------------------
# 4. 星云 —— 弥散的彩色云雾 + 繁星
# ---------------------------------------------------------------------------
def nebula(w, h, palette, seed, clouds=10):
    rng = np.random.default_rng(seed)
    # 深邃黑底
    arr = np.full((h, w, 3), 6, dtype=np.float64)
    for _ in range(clouds):
        cx, cy = rng.uniform(0, w), rng.uniform(0, h)
        sigma = rng.uniform(100, 320)
        t = rng.uniform(0, 1)
        col = sample_gradient(palette, t)
        yy, xx = np.mgrid[0:h, 0:w]
        d = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * sigma ** 2))
        # 用最大值叠加，避免多团云糊成纯白
        layer = (d[..., None] * col[None, None, :])
        arr = np.maximum(arr, layer)

    arr = np.clip(arr, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, "RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(500):
        sx, sy = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.uniform(0.3, 1.8)
        b = int(rng.uniform(120, 255))
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(b, b, b, int(b)))
    return img.filter(ImageFilter.GaussianBlur(0.8))


STYLES = {
    "flow": flow_field,
    "aurora": aurora,
    "mandala": mandala,
    "nebula": nebula,
}
