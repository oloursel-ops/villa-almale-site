#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("live")
PAGE = ROOT / "off-season/index.html"
IMAGE_PATH = "/assets/images/current/villa-almale-location-golf-v7-2.webp"
DATE = "2026-08-02"

STYLE = """
.location-at-a-glance{padding-top:68px;padding-bottom:68px;background:#f6f3ec}
.location-at-a-glance .section-heading{align-items:end}
.location-figure{max-width:900px;margin:30px auto 0}
.location-figure img{display:block;width:100%;height:auto;border-radius:24px;box-shadow:0 20px 50px rgba(10,35,57,.16);background:#fff}
.location-figure figcaption{max-width:780px;margin:14px auto 0;color:#66706d;font-size:.86rem;line-height:1.55;text-align:center}
@media (max-width:720px){.location-at-a-glance{padding-top:52px;padding-bottom:52px}.location-figure{margin-top:22px}.location-figure img{border-radius:16px}.location-figure figcaption{font-size:.78rem;text-align:left}}
""".strip()

SECTION = f"""
<section class="section location-at-a-glance" id="location-at-a-glance">
  <div class="shell">
    <div class="section-heading">
      <div>
        <span class="eyebrow">Between Seville and the Algarve</span>
        <h2>Location at a glance</h2>
      </div>
      <p>A simple overview of Villa Almale’s Atlantic setting and the main golf options around Nuevo Portil.</p>
    </div>
    <figure class="location-figure">
      <img src="{IMAGE_PATH}" width="900" height="507" loading="lazy" decoding="async" alt="Schematic showing Villa Almale in Nuevo Portil between Seville and the Algarve, with nearby golf courses"/>
      <figcaption>Schematic overview. Driving times are indicative and may vary with traffic, route and the exact golf entrance used.</figcaption>
    </figure>
  </div>
</section>
""".strip()


def update_json_ld(soup: BeautifulSoup) -> None:
    for block in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = block.string or block.get_text()
        payload = json.loads(raw)

        def walk(node):
            if isinstance(node, dict):
                node_type = node.get("@type")
                types = {node_type} if isinstance(node_type, str) else set(node_type or [])
                if "WebPage" in types:
                    node["dateModified"] = DATE
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        walk(payload)
        block.string = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def patch() -> None:
    if not PAGE.is_file():
        raise RuntimeError(f"Missing production page: {PAGE}")

    text = PAGE.read_text(encoding="utf-8")
    soup = BeautifulSoup(text, "html.parser")

    if soup.find(id="location-at-a-glance") is None:
        stat_strip = soup.select_one("section.stat-strip")
        if stat_strip is None:
            raise RuntimeError("The stat-strip insertion anchor is missing")
        fragment = BeautifulSoup(SECTION, "html.parser").find("section")
        stat_strip.insert_after(fragment)

    if soup.find("style", id="v72-location-visual-style") is None:
        if soup.head is None:
            raise RuntimeError("HTML head is missing")
        style = soup.new_tag("style", id="v72-location-visual-style")
        style.string = STYLE
        soup.head.append(style)

    update_json_ld(soup)

    output = str(soup)
    if not output.lstrip().lower().startswith("<!doctype"):
        output = "<!DOCTYPE html>\n" + output
    PAGE.write_text(output, encoding="utf-8")


def validate() -> None:
    text = PAGE.read_text(encoding="utf-8")
    soup = BeautifulSoup(text, "html.parser")

    sections = soup.select("#location-at-a-glance")
    if len(sections) != 1:
        raise RuntimeError(f"Expected exactly one location section, found {len(sections)}")
    image = sections[0].find("img", src=IMAGE_PATH)
    if image is None:
        raise RuntimeError("Location visual image is missing")
    if image.get("width") != "900" or image.get("height") != "507":
        raise RuntimeError("Location visual dimensions are incorrect")
    if image.get("loading") != "lazy" or image.get("decoding") != "async":
        raise RuntimeError("Location visual loading attributes are missing")
    if soup.find("style", id="v72-location-visual-style") is None:
        raise RuntimeError("Location visual CSS is missing")
    if len(soup.find_all("h1")) != 1:
        raise RuntimeError("The page must keep exactly one H1")
    if any(not heading.get_text(" ", strip=True) for heading in soup.find_all(["h2", "h3"])):
        raise RuntimeError("An empty heading was introduced")
    for anchor in soup.find_all("a", href=True):
        if anchor.get("target") != "_blank":
            raise RuntimeError(f"Link does not open in a new tab: {anchor.get('href')}")
        rel = set(anchor.get("rel", []))
        if not {"noopener", "noreferrer"}.issubset(rel):
            raise RuntimeError(f"Link security attributes missing: {anchor.get('href')}")
    for block in soup.find_all("script", attrs={"type": "application/ld+json"}):
        json.loads(block.string or block.get_text())
    if "latitude" in text.lower() or "longitude" in text.lower():
        raise RuntimeError("Exact coordinates must not be exposed")


if __name__ == "__main__":
    patch()
    validate()
    print("Villa Almale V7.2 location visual update validated successfully.")
