"""Make the public copy of a lecture notebook downloaded from Colab.

Removes Colab metadata (including the account name and ID Colab stores in every
executed cell), Colab's interactive-table scripts, pip progress output and
execution counts, and compresses plot images. Outputs are kept.
Usage: python3 tools/econ294a/clean_notebook.py <in.ipynb> <out.ipynb>
"""
import base64
import io
import json
import re
import sys

import nbformat
from bs4 import BeautifulSoup
from PIL import Image

def src(cell):
    s = cell.get("source", "")
    return "".join(s) if isinstance(s, list) else s


def psnr(a, b):
    import math
    pa, pb = a.convert("RGB").tobytes(), b.convert("RGB").tobytes()
    n = len(pa)
    mse = sum((x - y) ** 2 for x, y in zip(pa[::7], pb[::7])) / max(1, len(pa[::7]))
    return 99.0 if mse == 0 else 10 * math.log10(255 ** 2 / mse)


def compress_png(b64):
    raw = base64.b64decode(b64)
    im = Image.open(io.BytesIO(raw))
    im.load()
    if im.mode in ("RGBA", "LA", "P"):
        rgba = im.convert("RGBA")
        bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        bg.alpha_composite(rgba)
        im = bg.convert("RGB")
    else:
        im = im.convert("RGB")
    q = im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    buf = io.BytesIO()
    if psnr(im, q) >= 38:
        q.save(buf, "PNG", optimize=True)
    else:  # gradients/colormaps: keep full colour, just recompress
        im.save(buf, "PNG", optimize=True)
    out = buf.getvalue()
    return base64.b64encode(out if len(out) < len(raw) else raw).decode()


def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    if "sk-container" in html:          # scikit-learn estimator diagram: keep text/plain
        return None
    table = soup.find("table", class_="dataframe")
    if table is not None and ("colab-df" in html or soup.find("script")):
        wrapper = table.parent
        for tag in wrapper.find_all(["script", "button"]):
            tag.decompose()
        for tag in wrapper.find_all(class_=re.compile(r"colab-df")):
            tag.decompose()
        return str(wrapper)
    for tag in soup.find_all(["script", "button"]):
        tag.decompose()
    return str(soup)


def main(path_in, path_out):
    nb = nbformat.read(path_in, as_version=4)
    nb.metadata = nbformat.from_dict({k: v for k, v in nb.metadata.items()
                                      if k in ("kernelspec", "language_info")})
    for c in nb.cells:
        c.metadata = nbformat.from_dict({k: v for k, v in c.metadata.items() if k == "tags"})
        if c.cell_type != "code":
            continue
        c.execution_count = None
        if src(c).lstrip().startswith(("!pip", "%pip")):
            c.outputs = []
            continue
        kept = []
        for o in c.outputs:
            if o.output_type == "execute_result":
                o.execution_count = None
            if o.output_type in ("execute_result", "display_data"):
                data = o.get("data", {})
                for k in [k for k in data if "colaboratory" in k or "widget" in k]:
                    del data[k]
                if "text/html" in data:
                    h = clean_html(src({"source": data["text/html"]}))
                    if h is None:
                        del data["text/html"]
                    else:
                        data["text/html"] = h
                if "image/png" in data:
                    data["image/png"] = compress_png(src({"source": data["image/png"]}))
                if not data:
                    continue
            kept.append(o)
        c.outputs = kept
    nbformat.validate(nb)
    nbformat.write(nb, path_out)
    raw = open(path_out).read()
    for needle in ("displayName", "userId", "executionInfo", "colab-df", "google.colab", "<script"):
        assert needle not in raw, (path_out, needle)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
