"""Render a public lecture notebook as a Hugo page bundle for the website.

Writes <out_dir>/index.html (front matter + HTML body), the plot images, and a
copy of the notebook for download. The HTML loads nothing from other sites.
Usage: python3 tools/econ294a/nb2page.py <notebook.ipynb> content/econ294a/lecture-N <front_matter.json>
The front matter JSON holds title, lecture, weight, summary and description.
"""
import html as htmllib
import io
import json
import re
import shutil
import sys
from pathlib import Path

import nbformat
from bs4 import BeautifulSoup
from nbconvert import HTMLExporter
from PIL import Image
from traitlets.config import Config

ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
HEADING = re.compile(r"^h[1-6]$")


def slugify(text, used):
    s = re.sub(r"[`'’\"]", "", text.lower())
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "section"
    base, i = s, 2
    while s in used:
        s, i = f"{base}-{i}", i + 1
    used.add(s)
    return s


def prepare(nb):
    """Page-only edits; the downloadable notebook keeps everything."""
    first = nb.cells[0]
    if first.cell_type == "markdown" and first.source.lstrip().startswith("# "):
        rest = "\n".join(first.source.lstrip().splitlines()[1:]).strip()
        if rest:
            first.source = rest          # the page header already shows the title
        else:
            nb.cells.pop(0)
    for c in nb.cells:
        for o in c.get("outputs", []):
            if o.output_type == "stream":
                o.text = ANSI.sub("", o.text)
            elif o.output_type == "error":
                o.traceback = [ANSI.sub("", t) for t in o.traceback]
    # blank exercise cells are for students to fill in; on the web they are empty boxes
    nb.cells = [c for c in nb.cells if not (c.cell_type == "code" and not c.source.strip())]
    return nb


def export(nb):
    c = Config()
    c.HTMLExporter.preprocessors = ["nbconvert.preprocessors.ExtractOutputPreprocessor"]
    c.ExtractOutputPreprocessor.output_filename_template = "fig-{cell_index}-{index}{extension}"
    c.HTMLExporter.exclude_input_prompt = True
    c.HTMLExporter.exclude_output_prompt = True
    return HTMLExporter(config=c, template_name="basic").from_notebook_node(nb)


def output_kind(sub):
    cls = sub.get("class", [])
    if "output_stream" in cls:
        return "stderr" if "output_stderr" in cls else "stream"
    if "output_error" in cls:
        return "error"
    if sub.find("img"):
        return "image"
    if sub.find("table"):
        return "table"
    if "rendered_html" in cls or "output_html" in cls:
        return "html"
    return "text"


def rebuild(body):
    src = BeautifulSoup(body, "html.parser")
    out = BeautifulSoup("", "html.parser")
    root = out.new_tag("div", attrs={"class": "post-content nb"})
    for cell in src.find_all("div", class_="cell", recursive=False):
        cls = cell.get("class", [])
        if "text_cell" in cls:
            render = cell.find("div", class_="text_cell_render")
            for child in list(render.children):
                root.append(child.extract())
            continue
        box = out.new_tag("div", attrs={"class": "nb-cell"})
        pre = cell.select_one("div.input_area div.highlight pre")
        if pre is not None:
            lead = pre.find("span")
            if lead is not None and not lead.get_text() and not lead.attrs:
                lead.decompose()
            code = out.new_tag("code", attrs={"class": "language-python"})
            for child in list(pre.children):
                code.append(child.extract())
            # drop the trailing newline nbconvert leaves inside <pre>
            if code.contents and isinstance(code.contents[-1], str):
                code.contents[-1].replace_with(code.contents[-1].rstrip("\n"))
            hl = out.new_tag("div", attrs={"class": "highlight"})
            new_pre = out.new_tag("pre")
            new_pre.append(code)
            hl.append(new_pre)
            box.append(hl)
        for area in cell.select("div.output_area"):
            sub = area.find("div", class_="output_subarea")
            if sub is None:
                continue
            kind = output_kind(sub)
            div = out.new_tag("div", attrs={"class": f"nb-out nb-{kind}"})
            for child in list(sub.children):
                div.append(child.extract())
            box.append(div)
        root.append(box)
    return out, root


def finish(out, root, figures, out_dir):
    for tag in root.find_all("a", class_="anchor-link"):
        tag.decompose()
    for tag in root.find_all(["style", "script", "button"]):
        tag.decompose()
    used, toc = set(), []
    for h in root.find_all(HEADING):
        level = min(int(h.name[1]) + 1, 6)       # page title is the only h1
        h.name = f"h{level}"
        text = " ".join(h.get_text().split())
        h["id"] = slugify(text, used)
        if level in (2, 3):
            toc.append((level, h["id"], text))
    for t in root.find_all("table"):
        for attr in ("border", "style"):
            t.attrs.pop(attr, None)
        for tr in t.find_all("tr"):
            tr.attrs.pop("style", None)
        parent = t.parent
        if not (parent.name == "div" and "nb-table" in parent.get("class", [])):
            wrap = out.new_tag("div", attrs={"class": "nb-table"})
            t.wrap(wrap)
    n = 0
    for img in root.find_all("img"):
        src = img.get("src", "")
        if src not in figures:
            raise SystemExit(f"unexpected image source {src[:60]}")
        n += 1
        name = f"fig-{n:02d}.png"
        data = figures[src]
        w, h = Image.open(io.BytesIO(data)).size
        (out_dir / name).write_bytes(data)
        img.attrs = {"src": name, "width": str(w), "height": str(h),
                     "alt": "Figure produced by the code above", "loading": "lazy", "decoding": "async"}
    for a in root.find_all("a", href=True):
        if a["href"].startswith("http"):
            a["target"] = "_blank"
            a["rel"] = "noopener"
    return toc, n


def toc_html(toc):
    if not toc:
        return ""
    parts, open_sub = ['<div class="toc"><details><summary accesskey="c" title="(Alt + C)">'
                       '<span class="details">Contents</span></summary><div class="inner"><ul>'], False
    seen_top = False
    for i, (level, hid, raw) in enumerate(toc):
        text = htmllib.escape(raw)
        if level == 2:
            seen_top = True
        elif not seen_top:           # sections before the first chapter go at the top level
            level = 2
        if level == 2:
            if open_sub:
                parts.append("</ul></li>")
                open_sub = False
            elif i:
                parts.append("</li>")
            parts.append(f'<li><a href="#{hid}" aria-label="{text}">{text}</a>')
        else:
            if not open_sub:
                parts.append("<ul>")
                open_sub = True
            parts.append(f'<li><a href="#{hid}" aria-label="{text}">{text}</a></li>')
    parts.append("</ul></li>" if open_sub else "</li>")
    parts.append("</ul></div></details></div>")
    return "".join(parts)


def main(nb_path, out_dir, fm_path):
    nb_path, out_dir = Path(nb_path), Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    fm = json.loads(Path(fm_path).read_text())
    nb = prepare(nbformat.read(nb_path, as_version=4))
    body, res = export(nb)
    out, root = rebuild(body)
    toc, nfig = finish(out, root, res.get("outputs", {}), out_dir)
    shutil.copy(nb_path, out_dir / nb_path.name)
    fm["notebook"] = nb_path.name
    front = "---\n" + "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in fm.items()) + "\n---\n"
    html = front + toc_html(toc) + "\n" + str(root) + "\n"
    for bad in ("<script", "http://", "src=\"http", "href=\"//", "src=\"//", "data:image"):
        assert bad not in html.split("---\n", 2)[-1] or bad == "http://", (bad, nb_path)
    (out_dir / "index.html").write_text(html)
    print(f"{nb_path.name}: {len(html)/1e3:,.0f} KB html, {nfig} figures, {len(toc)} toc entries")


if __name__ == "__main__":
    main(*sys.argv[1:4])
