#!/usr/bin/env python3
"""Check that the paper pages on the site still match the English CV.

The title and abstract of each paper in content/papers/ are copied from the English CV
(static/Li_Yuchao_CV.pdf, which the CV sync updates from Overleaf). This script checks
that each title and abstract still appears in the CV's text. Case, punctuation, spaces
and line breaks are ignored, so line-break hyphenation in the PDF does not matter (and a
change that only touches punctuation is not reported).

Papers with `draft: true` or `cv_check: false` in their front matter are skipped.

Usage: python3 tools/check_papers.py [--cv PDF] [--papers DIR] [--report FILE]
Needs pypdf. Writes the report (Markdown) to --report and prints it. Under GitHub Actions
it also writes status=ok|mismatch|skip to $GITHUB_OUTPUT. The exit code is 0 unless the
script itself fails.
"""

import argparse
import html
import os
import re
import sys
import unicodedata
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent


def norm(text):
    """Lowercase letters and digits only (accents and ligatures decomposed)."""
    return re.sub(r"[^0-9a-z]", "", unicodedata.normalize("NFKD", text).casefold())


def plain(markdown):
    """Markdown/HTML to plain text with single spaces."""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", markdown)  # images
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # links keep their text
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(html.unescape(text).split())


def front_matter(text):
    m = re.match(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)(.*)\Z", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def field(fm, key):
    m = re.search(rf"^{key}:[ \t]*(.*?)[ \t]*$", fm, re.M)
    if not m:
        return None
    value = m.group(1)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        quote, value = value[0], value[1:-1]
        if quote == '"':
            value = re.sub(r"\\(.)", r"\1", value)
        else:
            value = value.replace("''", "'")
    return value


def abstract(body):
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    m = re.search(r"^#{1,6}[ \t]*Abstract[ \t]*\n(.*?)(?=^#{1,6}[ \t]|\Z)", body, re.S | re.M | re.I)
    return plain(m.group(1)) if m else ""


def sentences(text):
    return [s for s in re.split(r"(?<=[.?!])\s+(?=[A-Z0-9(\"“])", text) if norm(s)]


def check(cv_pdf, papers_dir):
    """Return (status, report, log lines)."""
    if not cv_pdf.is_file():
        return "skip", "", [f"{cv_pdf} not found; nothing to compare with."]
    cv = norm("\n".join(page.extract_text() or "" for page in PdfReader(cv_pdf).pages))
    if not cv:
        raise SystemExit(f"No text could be extracted from {cv_pdf}.")

    log, problems = [], []
    for index in sorted(papers_dir.glob("*/index.md")):
        rel = index.relative_to(ROOT) if index.is_relative_to(ROOT) else index
        fm, body = front_matter(index.read_text(encoding="utf-8"))
        title = field(fm, "title") or ""
        if (field(fm, "draft") or "").lower() == "true":
            log.append(f"skip  {rel} (draft)")
            continue
        if (field(fm, "cv_check") or "").lower() == "false":
            log.append(f"skip  {rel} (cv_check: false)")
            continue

        notes = []
        if norm(title) not in cv:
            notes.append("- 标题在 CV 里找不到。")
        text = abstract(body)
        if not text:
            log.append(f"note  {rel}: no Abstract section; only the title is checked")
        elif norm(text) not in cv:
            missing = [s for s in sentences(text) if norm(s) not in cv]
            if missing:
                notes.append("- 摘要和 CV 不一致。网站上的这几句在 CV 里找不到：")
                notes += [f"  - {s}" for s in missing]
            else:
                notes.append("- 摘要和 CV 不一致。网站上的每一句 CV 里都有，但连起来对不上，"
                             "可能是有一边加了或删了句子，或者调整了顺序。")

        if notes:
            problems.append(f"**{title or rel}**（`{rel}`）\n\n" + "\n".join(notes))
            log.append(f"DIFF  {rel}")
        else:
            log.append(f"ok    {rel}")

    if not problems:
        return "ok", "", log
    cv_rel = cv_pdf.relative_to(ROOT) if cv_pdf.is_relative_to(ROOT) else cv_pdf
    report = "\n\n".join(
        [f"网站上下面这些论文的文字和英文 CV（`{cv_rel}`）对不上：", *problems,
         "比较时不区分大小写，也不看标点、空格和换行。",
         "改的时候，同一个文件里的 `summary`（Research 页卡片上的简介）和 `description` 也要跟着改；"
         "JMP 还有首页 `config.yml` 里 `jobMarket` 的简介。改好推上去后，网站重新发布时会再检查一次，"
         "一致了这个 issue 就会自动关闭。",
         "如果某篇论文有意和 CV 不一样（比如网站上放的是论文里的完整摘要），"
         "在它的 front matter 里写 `cv_check: false`，就不再检查这一篇。"]
    ) + "\n"
    return "mismatch", report, log


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cv", type=Path, default=ROOT / "static" / "Li_Yuchao_CV.pdf")
    parser.add_argument("--papers", type=Path, default=ROOT / "content" / "papers")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    status, report, log = check(args.cv.resolve(), args.papers.resolve())
    print("\n".join(log))
    print(f"\nstatus: {status}")
    if report:
        print("\n" + report)
    if args.report:
        args.report.write_text(report, encoding="utf-8")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
            out.write(f"status={status}\n")


if __name__ == "__main__":
    sys.exit(main())
