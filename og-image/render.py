"""把 og-image/og.html 渲染成 static/og.jpg（分享链接时的预览图）。

用法（在仓库根目录）：python3 og-image/render.py
需要 Playwright（含 Chromium）、Pillow，以及 Inter / Inter Display 字体。
"""
import io
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "og-image" / "og.html"
OUT = ROOT / "static" / "og.jpg"
PHOTO = ROOT / "static" / "picture.jpeg"
W, H = 1200, 630
MIN_MARGIN = 60  # 照片和文字离左右边缘至少这么远，否则说明文字太长

# 缺字体时 Chromium 会悄悄换成别的字体，先检查（没有 fontconfig 的系统跳过）
if shutil.which("fc-match"):
    for spec, family in (("Inter Display:bold", "Inter Display"), ("Inter", "Inter")):
        found = subprocess.run(["fc-match", "-f", "%{family}", spec],
                               capture_output=True, text=True).stdout
        if family not in found:
            sys.exit(f"缺少字体 {family}（fc-match 给的是 {found!r}）")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    page.goto(SRC.as_uri())
    page.evaluate("document.fonts.ready")
    left, right, photo_ok = page.evaluate("""() => {
        const img = document.querySelector('.photo');
        const t = document.querySelector('.text').getBoundingClientRect();
        return [img.getBoundingClientRect().left, innerWidth - t.right,
                img.complete && img.naturalWidth > 0];
    }""")
    png = page.screenshot()
    browser.close()

if not photo_ok:
    sys.exit(f"照片没加载出来：{PHOTO}")
if min(left, right) < MIN_MARGIN:
    sys.exit(f"左右边距 {left:.0f}px / {right:.0f}px，太挤了：缩短文字或调小字号")

img = Image.open(io.BytesIO(png)).convert("RGB")
img.save(OUT, "JPEG", quality=88, progressive=True, optimize=True, subsampling=0,
         icc_profile=Image.open(PHOTO).info.get("icc_profile"))  # 沿用照片的 sRGB 配置文件
print(f"{OUT.relative_to(ROOT)}：{img.width}×{img.height}，{OUT.stat().st_size / 1024:.0f} KB，"
      f"左右边距 {left:.0f}px / {right:.0f}px")
