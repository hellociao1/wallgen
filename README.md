# 🎨 wallgen · 一条命令生成独一无二的生成艺术壁纸

> 每次运行都产出一张**全网仅此一张**的 4K 艺术壁纸。零素材、零版权问题，你的桌面你做主。

![flow](samples/sample_flow.png)

## ✨ 为什么用它

- 🎲 **每次都不一样** —— 随机种子决定画面，永远不重样
- 🖼 **最高 4K** —— 直接当桌面壁纸 / 手机壁纸 / 视频背景
- 🪶 **零依赖美术素材** —— 纯算法实时生成，不联网、不打包大图
- 🔁 **可复现** —— 记下 seed，随时复刻你最爱的那一张
- 🐍 **纯 Python** —— 只有 numpy + Pillow，三行装好

## 🚀 快速开始

```bash
git clone https://github.com/hellociao1/wallgen.git
cd wallgen
pip install -r requirements.txt

python main.py                 # 随机风格 + 随机配色，出一张壁纸
```

就这样！壁纸会保存成 `wall_<风格>_<配色>_<种子>.png`。

## 🎛 常用姿势

```bash
# 指定风格 + 配色
python main.py -s aurora -p neon

# 固定种子复刻同款
python main.py -s flow -p sunset --seed 42

# 出 4K 大图
python main.py --style nebula --palette ocean --size 4k -o my_wallpaper.png
```

### 参数

| 参数 | 说明 | 可选值 |
|------|------|--------|
| `-s, --style` | 艺术风格 | `flow` `aurora` `mandala` `nebula`（或 `random`）|
| `-p, --palette` | 配色方案 | `sunset` `ocean` `candy` `forest` `neon` `mono` `peach` `gold` |
| `--seed` | 随机种子 | 任意整数，不传则随机 |
| `--size` | 分辨率 | `hd` `fhd` `2k` `4k` 或 `宽x高`（如 `2560x1440`）|
| `-o, --out` | 输出文件名 | 默认自动命名 |

## 🖼 画廊

| 🌊 flow 流场 | 🌌 aurora 极光 |
|---|---|
| ![flow](samples/sample_flow.png) | ![aurora](samples/sample_aurora.png) |

| 🌸 mandala 曼陀罗 | 🪐 nebula 星云 |
|---|---|
| ![mandala](samples/sample_mandala.png) | ![nebula](samples/sample_nebula.png) |

## 🧩 作为库调用

```python
from wallgen.styles import flow_field
img = flow_field(1920, 1080, "neon", seed=42)
img.save("my.png")
```

## 🗂 结构

```
wallgen/
├── main.py            # CLI 入口
├── requirements.txt
├── wallgen/
│   ├── palettes.py    # 8 套预设配色
│   └── styles.py      # 4 种生成艺术引擎
└── samples/          # 示例图
```

## 📄 License

MIT —— 生成的壁纸版权归你，随便用！
