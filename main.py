#!/usr/bin/env python3
"""wallgen —— 一条命令生成独一无二的生成艺术壁纸。

用法:
    python main.py                       # 随机风格+配色，输出 wall.png
    python main.py -s aurora -p neon     # 指定风格和配色
    python main.py --style flow --palette sunset --seed 42 --size 4k
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wallgen.styles import STYLES
from wallgen.palettes import PALETTES


def parse_size(s):
    presets = {
        "hd": (1280, 720),
        "fhd": (1920, 1080),
        "2k": (2560, 1440),
        "4k": (3840, 2160),
    }
    if s in presets:
        return presets[s]
    if "x" in s:
        w, h = s.lower().split("x")
        return int(w), int(h)
    raise ValueError(f"未知尺寸: {s}")


def main():
    ap = argparse.ArgumentParser(description="🎨 wallgen —— 生成艺术壁纸生成器")
    ap.add_argument("-s", "--style", default="random", choices=["random"] + list(STYLES.keys()))
    ap.add_argument("-p", "--palette", default="random", choices=["random"] + list(PALETTES.keys()))
    ap.add_argument("--seed", type=int, default=None, help="随机种子（不传则随机）")
    ap.add_argument("--size", default="fhd", help="分辨率: hd/fhd/2k/4k 或 宽x高，如 1920x1080")
    ap.add_argument("-o", "--out", default=None, help="输出文件名")
    args = ap.parse_args()

    import random
    rng = random.Random(args.seed)
    style = rng.choice(list(STYLES.keys())) if args.style == "random" else args.style
    palette = rng.choice(list(PALETTES.keys())) if args.palette == "random" else args.palette
    seed = args.seed if args.seed is not None else rng.randint(0, 10 ** 9)
    w, h = parse_size(args.size)

    print(f"🎨 风格: {style}  |  配色: {palette}  |  种子: {seed}  |  画布: {w}x{h}")
    img = STYLES[style](w, h, palette, seed)

    out = args.out or f"wall_{style}_{palette}_{seed}.png"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    img.save(out, quality=95)
    print(f"✅ 壁纸已保存: {out}")
    print("   喜欢的话，把 seed 记下，下次能复现同款哦～")


if __name__ == "__main__":
    main()
