#!/usr/bin/env python3
"""Automated structural, text and every-page render gate for the PDF edition.

Contact sheet is review evidence, not a substitute for final human/device QA.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "pdf" / "github-income-handbook.pdf"
OUT = ROOT / "artifacts" / "pdf-qa"
OUT.mkdir(parents=True, exist_ok=True)

errors = []
with fitz.open(PDF) as doc:
    count = doc.page_count
    if count < 24:
        errors.append(f"Too few pages for the 20-chapter edition: {count}")
    if len(doc.get_toc()) < 20:
        errors.append("Missing PDF chapter bookmarks")
    text = "\n".join(page.get_text() for page in doc)
    for phrase in ["GitHub", "AIPMAndy", "metaver.vip", "a6no1.cn", "不承诺"]:
        if phrase not in text:
            errors.append("Missing important searchable text: " + phrase)
    if "\ufffd" in text:
        errors.append("Unicode replacement glyph found in extracted PDF text")
    links = sum(len(page.get_links()) for page in doc)
    if links < 35:
        errors.append(f"Expected actionable sources, table of contents and contacts: {links} links")
    thumbs = []
    for i, page in enumerate(doc):
        blocks = page.get_text("blocks")
        content_blocks = [b for b in blocks if len(b) >= 5 and isinstance(b[4], str) and b[4].strip()]
        if not content_blocks:
            errors.append(f"Blank text page {i+1}")
        for b in content_blocks:
            if b[0] < -2 or b[1] < -2 or b[2] > page.rect.width + 2 or b[3] > page.rect.height + 2:
                errors.append(f"Page {i+1} text beyond bounds: {tuple(round(v,1) for v in b[:4])}")
        pix = page.get_pixmap(matrix=fitz.Matrix(0.50, 0.50), alpha=False)
        im = Image.frombytes("RGB", [pix.width,pix.height], pix.samples)
        thumbs.append(im)
        if i in (0, 1, count//2, count-1):
            high = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            high.save(str(OUT / f"sample-{i+1:03d}.png"))
    columns = 5
    tile_w, tile_h = 325, 485
    sheet = Image.new("RGB", (columns*tile_w, math.ceil(count/columns)*tile_h), "white")
    draw = ImageDraw.Draw(sheet)
    for i, im in enumerate(thumbs):
        im.thumbnail((tile_w-18, tile_h-36))
        x=(i%columns)*tile_w + (tile_w-im.width)//2
        y=(i//columns)*tile_h + 8
        sheet.paste(im,(x,y))
        draw.text(((i%columns)*tile_w+12, y+im.height+6), f"Page {i+1}", fill="#25354a")
    sheet.save(OUT / "all-pages.jpg", quality=85)
    digest=hashlib.sha256(PDF.read_bytes()).hexdigest()
    report={
        "pdf":"pdf/github-income-handbook.pdf","sha256":digest,"pages":count,
        "bookmarks":len(doc.get_toc()),"annotations_and_links":links,
        "searchable_characters":len(text),"every_page_rendered":len(thumbs),
        "errors":errors,
        "review_limits":"Automated render/text/bounds only. Manual zoom and real devices remain pending."
    }
(OUT / "report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(report,indent=2,ensure_ascii=False))
if errors:
    raise SystemExit(1)
