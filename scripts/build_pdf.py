#!/usr/bin/env python3
"""Build the public PDF strictly from this repository's Markdown source.

No fabricated testimonials or performance data. The PDF is a separate edition
of the open chapters, reference notes, and reusable templates.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote

from markdown import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pdf" / "github-income-handbook.pdf"
REPO = "https://github.com/AIPMAndy/github-income-handbook"
PAGES = "https://aipmandy.github.io/github-income-handbook/"
WECHAT = "AIPMAndy"


def source_html(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    body = markdown(content, extensions=["extra", "sane_lists", "toc"])
    # Relative Markdown links are unusable in PDFs unless converted to
    # their verifiable repository source URLs. Leave in-page anchors alone.
    def fix_link(match):
        href = html.unescape(match.group(1))
        if href.startswith(("#", "https://", "http://", "mailto:")):
            return match.group(0)
        resolved = (path.parent / href.split("#", 1)[0]).resolve()
        if not resolved.is_relative_to(ROOT):
            return 'href="' + REPO + '"'
        relative = resolved.relative_to(ROOT).as_posix()
        suffix = ("#" + href.split("#", 1)[1]) if "#" in href else ""
        return 'href="' + REPO + "/blob/main/" + quote(relative, safe="/") + suffix + '"'
    return re.sub(r'href="([^"]+)"', fix_link, body)


def markdown_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ")


def section(path: Path, identifier: str, kind: str) -> str:
    source_link = REPO + "/blob/main/" + quote(path.relative_to(ROOT).as_posix(), safe="/")
    tag = "作者教程" if kind == "CHAPTER" else ("研究与来源" if kind == "SOURCE" else "开放模板")
    hint = ""
    if path.name.startswith("15-") and kind == "CHAPTER":
        hint = ('<p class="scope">案例说明：本章公开项目仅用于方法分析；'
                '不能据此证明客户、订单、收入或转化率。未经公开许可的客户案例不收录。</p>')
    return (
        '<article class="chapter" id="' + identifier + '">'
        '<div class="chapter-kicker">' + kind + ' / ' + html.escape(tag) + '</div>'
        + hint + '<div class="markdown">' + source_html(path) + '</div>'
        '<p class="origin">原始可编辑材料：<a href="' + source_link + '">'
        + html.escape(path.relative_to(ROOT).as_posix()) + '</a></p>'
        '</article>'
    )


def build() -> None:
    chapters = sorted((ROOT / "chapters").glob("*.md"))
    assert len(chapters) == 20, f"Expected 20 canonical chapters, got {len(chapters)}"
    sources = [ROOT / "research" / n for n in
               ("sources.md", "legal-and-platform.md", "red-team.md")]
    assert all(p.is_file() for p in sources)
    templates = sorted((ROOT / "templates").glob("*.md"))
    assert len(templates) >= 10, "Expected reusable Markdown templates"
    build_date = os.environ.get("EDITION_DATE", date.today().isoformat())

    navigation = [
        '<a href="#ch' + f"{n:02d}" + '"><span>' + f"{n:02d}"
        + '</span><strong>' + html.escape(markdown_title(path)) + '</strong></a>'
        for n, path in enumerate(chapters)
    ]
    origin = ('<a href="' + REPO + '">GitHub 代码与原文</a> · '
              '<a href="' + PAGES + '">在线互动工具</a> · '
              '<a href="https://metaver.vip/services">咨询与陪跑</a>')
    sections = [
        section(path, f"ch{n:02d}", "CHAPTER")
        for n, path in enumerate(chapters)
    ]
    sections += [section(p, f"ref{i}", "SOURCE") for i, p in enumerate(sources)]
    sections += [section(p, f"template{i}", "TEMPLATE") for i, p in enumerate(templates)]

    css = """
    @page { size: A4; margin: 20mm 18mm 19mm;
      @bottom-left { content: "AI 酋长 Andy · 开源知识"; color: #6c7580;
         font: 8pt "Noto Sans CJK SC", sans-serif; }
      @bottom-right { content: counter(page); color: #6c7580;
         font: 9pt sans-serif; }
    }
    @page:first { @bottom-left {content:none} @bottom-right {content:none} }
    :root { color:#172434; }
    * { box-sizing:border-box; }
    body { font-family:"Noto Sans CJK SC","Noto Sans SC",sans-serif;
      font-size:10pt; line-height:1.76; color:#223042; }
    a { color:#245488; text-decoration:none; }
    p, li { orphans:3; widows:3; }
    .cover { page-break-after:always; min-height:248mm; padding-top:30mm; }
    .brand { font-size:9pt; color:#45607e; letter-spacing:2px;
      font-weight:700; padding-bottom:9mm; border-bottom:1px solid #cad4de; }
    .edition { margin-top:36mm; font-size:10pt; color:#4b6682;
      letter-spacing:2px; }
    .cover h1 { font-size:38pt; color:#172434; line-height:1.19;
      letter-spacing:-1.5px; margin:8mm 0 7mm; }
    .tagline { font-size:15pt; line-height:1.45; color:#394d62; margin-bottom:12mm; }
    .cover-rule { display:block; width:24mm; height:2.4mm; background:#295c90; }
    .cover-note { margin-top:14mm; max-width:145mm;
      font-size:11pt; line-height:1.9; color:#5c6976; }
    .cover-footer { margin-top:40mm; padding-top:7mm;
      border-top:1px solid #d6dfe7; font-size:9pt; color:#4d5865; }
    .toc { page-break-after:always; }
    .toc h2,.appendix-intro h2 { font-size:24pt; color:#172434; margin:10mm 0 2mm; }
    .toc p { margin:0 0 10mm; color:#697783; }
    .toc-grid { display:grid; grid-template-columns:1fr 1fr; gap:3mm 8mm; }
    .toc-grid a { display:flex; gap:3mm; padding:2mm 0;
      border-bottom:1px solid #e2e7ed; font-size:10pt; }
    .toc-grid span { color:#6482a2; font-weight:700; }
    .toc-grid strong { font-weight:500; color:#243b52; }
    .toc-after { margin-top:12mm; color:#58697a; font-size:9pt; }
    .chapter { page-break-before:always; }
    .chapter-kicker { text-transform:uppercase; font:700 9pt sans-serif;
      letter-spacing:1.8px; color:#6684a5; padding:0 0 5mm;
      border-bottom:1px solid #d4dce4; }
    .markdown h1 { font-size:22pt; line-height:1.33;
      margin:8mm 0 7mm; color:#14283d; page-break-after:avoid; }
    .markdown h2 { font-size:15pt; margin:9mm 0 4mm; color:#1d3d5e;
      page-break-after:avoid; }
    .markdown h3 { font-size:11.5pt; margin:6mm 0 2mm;
      color:#2a4359; page-break-after:avoid; }
    .markdown p { margin:3mm 0; }
    .markdown li { margin:1.3mm 0; padding-left:1mm; }
    .markdown ul,.markdown ol { padding-left:7mm; }
    .markdown blockquote { margin:4mm 0; padding:2mm 4mm;
      border-left:2px solid #4b759f; background:#f1f5f9; color:#41566b; }
    .markdown code { font:9pt monospace; background:#edf2f6;
      padding:0.2mm 1mm; overflow-wrap:anywhere; }
    .markdown pre { border:1px solid #e2e7ed; background:#f6f8fa;
      padding:4mm; font:8.2pt monospace; white-space:pre-wrap; overflow-wrap:anywhere; }
    .markdown table { border-collapse:collapse; width:100%; font-size:8.5pt; }
    .markdown th,.markdown td { padding:2mm; border:1px solid #dbe3eb; }
    .markdown th { background:#edf3f9; }
    .scope { background:#edf3f9; border-left:2px solid #245488;
      padding:3mm; color:#34516e; }
    .origin { font-size:8.5pt; margin-top:10mm; padding-top:4mm;
      border-top:1px solid #e2e7ed; color:#657585; overflow-wrap:anywhere; }
    .appendix-intro { page-break-before:always; padding-top:42mm; }
    .appendix-intro p { color:#627282; }
    .contact { margin-top:10mm; padding:5mm 6mm; border:1px solid #cfd9e3;
      background:#f7f9fb; }
    .contact b { color:#1b3f64; }
    """
    h = (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>'
        + css + '</style></head><body>'
        '<section class="cover"><div class="brand">XINGJUE · KNOWLEDGE SERIES</div>'
        '<p class="edition">OPEN SOURCE HANDBOOK / ' + html.escape(build_date) + '</p>'
        '<h1>GitHub 赚钱<br>实战指南</h1>'
        '<div class="tagline">把公开作品，变成可以核验的商业机会。</div>'
        '<span class="cover-rule"></span>'
        '<p class="cover-note">20 章可编辑实操教程 + 来源核对 + 开放模板。'
        '从问题验证、开源交付、流量到询盘、报价和复盘。'
        '不承诺收入，不用 Star 或浏览量代替真实交易。</p>'
        '<div class="cover-footer">作者：AI 酋长 Andy · 星觉科技<br>'
        '个人微信：AIPMAndy · <a href="https://metaver.vip/">个人官网</a> · '
        '<a href="https://www.a6no1.cn/">公司官网</a><br>'
        + origin + '</div></section>'
        '<section class="toc"><h2>阅读地图</h2>'
        '<p>建议先完成 00—04，再选择一条业务路线，最后使用模板完成验证。</p>'
        '<div class="toc-grid">' + ''.join(navigation) + '</div>'
        '<p class="toc-after">附录含公开来源、平台边界、对抗式审核和可复用模板。'
        '政策、付款资格与平台规则会变化，请以链接的官方原文为准。</p>'
        '<div class="contact"><b>免费的完整项目：</b>' + origin + '</div></section>'
        + ''.join(sections)
        + '<section class="chapter"><div class="chapter-kicker">CONTACT / 作者信息</div>'
        '<div class="markdown"><h1>需要更具体的实施支持？</h1>'
        '<p>教程永久免费公开；如果需要针对真实业务的 AI 产品化、获客或实施咨询，'
        '请先通过公开服务页面了解适用范围与交付边界。</p>'
        '<p><b>个人微信：</b>AIPMAndy</p>'
        '<p><b>个人官网：</b><a href="https://metaver.vip/">https://metaver.vip/</a></p>'
        '<p><b>公司官网：</b><a href="https://www.a6no1.cn/">https://www.a6no1.cn/</a></p>'
        '<p><b>服务入口：</b><a href="https://metaver.vip/services">https://metaver.vip/services</a></p>'
        '<p>本资料不构成财务、法律或税务专业意见，不保证就业、营收、排名或利润。</p>'
        '</div></section></body></html>'
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=h, base_url=str(ROOT)).write_pdf(str(OUT), metadata={
        "title": "GitHub 赚钱实战指南",
        "author": "AI 酋长 Andy",
        "subject": "开源产品验证与商业交付的实践指南",
    })
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    print(json.dumps({
        "pdf": str(OUT.relative_to(ROOT)), "bytes": OUT.stat().st_size,
        "sha256": digest, "chapters": len(chapters),
        "sources": len(sources), "templates": len(templates),
        "build_date": build_date
    }, ensure_ascii=False))


if __name__ == "__main__":
    build()
