#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup


DATE = "2026-08-05"
STYLE_ID = "villa-almale-v76-spanish-climate"
SECTION_ID = "clima-septiembre-octubre"
NAUTICAL_PHOTO_ID = "el-rompido-nautica"
LEGACY_WHATSAPP_SELECTOR = '[data-whatsapp-contact="villa-almale-offseason"]'
RIA_IMAGE = "/assets/images/current/plage-ria-rio-piedras.webp"
MARINA_IMAGE = "/assets/images/current/el-rompido-marina.webp"
AEMET_URL = (
    "https://www.aemet.es/es/serviciosclimaticos/datosclimatologicos/"
    "valoresclimatologicos?l=4642E"
)

CSS = r'''
/* Villa Almale V7.6 — Spanish climate block */
.es-climate-section{padding:clamp(3.4rem,7vw,5.6rem) 0;background:#edf4ef;color:#153f39}
.es-climate-layout{display:grid;grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);gap:clamp(2rem,5vw,4.5rem);align-items:center}
.es-climate-copy h2{margin:.35rem 0 1rem;font-size:clamp(2rem,4.2vw,3.65rem);line-height:1.05;color:#103b35}
.es-climate-copy>p{max-width:42rem;margin:0;color:#4d5b57;font-size:1.03rem}
.es-climate-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.8rem}
.es-climate-card{min-height:9.4rem;padding:1.25rem;border:1px solid rgba(16,59,53,.14);border-radius:18px;background:#fff;box-shadow:0 10px 30px rgba(17,49,44,.08)}
.es-climate-card .month{display:block;margin-bottom:.55rem;color:#9a6b2f;font-size:.73rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase}
.es-climate-card strong{display:block;margin-bottom:.45rem;font-family:Georgia,"Times New Roman",serif;font-size:clamp(1.8rem,3.4vw,2.65rem);font-weight:400;line-height:1;color:#103b35}
.es-climate-card span:last-child{display:block;color:#5a6864;font-size:.9rem;line-height:1.4}
.es-climate-source{grid-column:1/-1;margin:.35rem 0 0;color:#66736f;font-size:.78rem;line-height:1.5}
.es-climate-source a{color:#153f39;font-weight:750;text-underline-offset:3px}
.es-nautical-photo{position:relative;max-width:760px;aspect-ratio:4/3;margin:1.8rem auto 2rem;overflow:hidden;border-radius:22px;background:#d8e2df;box-shadow:0 18px 46px rgba(12,43,39,.15)}
.es-nautical-photo img{display:block;width:100%;height:100%;object-fit:cover;object-position:center}
.es-nautical-photo .photo-copy{position:absolute;right:1rem;bottom:1rem;left:1rem;padding:1rem 1.1rem;border:1px solid rgba(255,255,255,.55);border-radius:15px;background:rgba(9,47,42,.84);color:#fff;backdrop-filter:blur(7px)}
.es-nautical-photo .photo-copy h3{margin:0 0 .2rem;color:#fff;font-size:1.12rem}
.es-nautical-photo .photo-copy p{margin:0;color:rgba(255,255,255,.82);font-size:.87rem}
@media(max-width:860px){.es-climate-layout{grid-template-columns:1fr}.es-climate-copy>p{max-width:none}}
@media(max-width:520px){.es-climate-grid{grid-template-columns:1fr}.es-climate-card{min-height:0}.es-climate-source{grid-column:auto}.es-nautical-photo{aspect-ratio:1/1;border-radius:18px}}
'''


CLIMATE_HTML = f'''
<section class="es-climate-section" id="{SECTION_ID}" aria-labelledby="climate-heading">
  <div class="shell es-climate-layout">
    <div class="es-climate-copy">
      <span class="eyebrow">El clima en septiembre y octubre</span>
      <h2 id="climate-heading">Mucho tiempo al aire libre, incluso al final del verano.</h2>
      <p>Como referencia cercana, las normales de Huelva–Ronda Este describen días todavía luminosos y temperaturas suaves para alternar playa, paseos, golf y terrazas.</p>
    </div>
    <div class="es-climate-grid" aria-label="Temperaturas y horas de sol medias">
      <article class="es-climate-card"><span class="month">Septiembre</span><strong>29,4 / 17,3 °C</strong><span>máxima / mínima media diaria</span></article>
      <article class="es-climate-card"><span class="month">Septiembre</span><strong>268 h de sol</strong><span>media mensual · unas 8,9 h al día</span></article>
      <article class="es-climate-card"><span class="month">Octubre</span><strong>24,9 / 14,1 °C</strong><span>máxima / mínima media diaria</span></article>
      <article class="es-climate-card"><span class="month">Octubre</span><strong>211 h de sol</strong><span>media mensual · unas 6,8 h al día</span></article>
      <p class="es-climate-source">Fuente: <a href="{AEMET_URL}" target="_blank" rel="noopener noreferrer">normales climatológicas AEMET · Huelva, Ronda Este (estación 4642E)</a>. Son valores medios de referencia, no una previsión diaria; junto al mar, las condiciones de Nuevo Portil pueden variar.</p>
    </div>
  </div>
</section>
'''


NAUTICAL_PHOTO_HTML = f'''
<figure class="photo-card theme-photo es-nautical-photo" id="{NAUTICAL_PHOTO_ID}">
  <img src="{MARINA_IMAGE}" width="900" height="900" loading="lazy" decoding="async" alt="Puerto y terrazas de El Rompido junto a la Ría del Río Piedras">
  <figcaption class="photo-copy"><h3>El Rompido junto al agua</h3><p>Puerto, terrazas y salidas hacia la Flecha del Rompido</p></figcaption>
</figure>
'''


def fragment(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.contents:
        if getattr(node, "name", None):
            return node
    raise RuntimeError("HTML fragment contains no tag")


def update_date_modified(node) -> None:
    if isinstance(node, dict):
        typ = node.get("@type")
        types = {typ} if isinstance(typ, str) else set(typ or [])
        if "WebPage" in types:
            node["dateModified"] = DATE
        for value in node.values():
            update_date_modified(value)
    elif isinstance(node, list):
        for value in node:
            update_date_modified(value)


def patch(path: Path) -> None:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    if soup.head is None or soup.body is None:
        raise RuntimeError("Spanish landing page is missing head/body")
    if len(soup.find_all("h1")) != 1:
        raise RuntimeError("Spanish landing page must contain exactly one H1")

    canonical = soup.find("link", rel="canonical")
    canonical_before = canonical.get("href") if canonical else None

    # The V7.4 floating action bar supersedes this earlier stand-alone button.
    for node in soup.select(LEGACY_WHATSAPP_SELECTOR):
        node.decompose()

    for node in soup.select(f"#{STYLE_ID}, #{SECTION_ID}, #{NAUTICAL_PHOTO_ID}"):
        node.decompose()

    hero_lead = soup.select_one("section.hero-season .hero-content p.lead")
    if hero_lead is None:
        raise RuntimeError("Spanish hero introduction is missing")
    hero_lead.string = (
        "Cinco dormitorios para grupos de 4 a 6 adultos, piscina privada, jardín y playa a pie, "
        "entre la ría del Río Piedras, los pinares y el Atlántico."
    )

    style = soup.new_tag("style", id=STYLE_ID)
    style.string = CSS
    soup.head.append(style)

    beach = soup.select_one("section#beach")
    if beach is None:
        raise RuntimeError("Spanish beach section is missing")
    ria_image = beach.find("img", src=RIA_IMAGE)
    if ria_image is None:
        raise RuntimeError("Approved Ría beach image is missing from the beach section")
    ria_image["width"] = "900"
    ria_image["height"] = "900"
    ria_image["loading"] = "lazy"
    ria_image["decoding"] = "async"
    beach.insert_after(fragment(CLIMATE_HTML))

    nautical = soup.select_one("section#nautical")
    if nautical is None:
        raise RuntimeError("Spanish nautical section is missing")
    nautical_heading = nautical.select_one(".section-heading")
    if nautical_heading is None:
        raise RuntimeError("Spanish nautical section heading is missing")
    nautical_heading.insert_after(fragment(NAUTICAL_PHOTO_HTML))

    for block in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = block.string or block.get_text()
        payload = json.loads(raw)
        update_date_modified(payload)
        block.string = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    output = str(soup)
    if not output.lstrip().lower().startswith("<!doctype"):
        output = "<!DOCTYPE html>\n" + output
    path.write_text(output, encoding="utf-8")

    check = BeautifulSoup(output, "html.parser")
    assert len(check.find_all("h1")) == 1
    assert check.select_one(LEGACY_WHATSAPP_SELECTOR) is None
    assert len(check.select(".site-floating-actions")) == 1
    assert len(check.select(".site-floating-actions .site-floating-action--whatsapp")) == 1
    assert len(check.select(".site-floating-actions .site-floating-action--booking")) == 1
    assert len(check.select(f"#{SECTION_ID}")) == 1
    assert len(check.select(f"#{SECTION_ID} .es-climate-card")) == 4
    assert len(check.select(f"section#beach img[src='{RIA_IMAGE}']")) == 1
    checked_ria = check.select_one(f"section#beach img[src='{RIA_IMAGE}']")
    assert checked_ria is not None and checked_ria.get("width") == "900" and checked_ria.get("height") == "900"
    assert len(check.select(f"section#nautical #{NAUTICAL_PHOTO_ID}")) == 1
    checked_marina = check.select_one(f"section#nautical #{NAUTICAL_PHOTO_ID} img[src='{MARINA_IMAGE}']")
    assert checked_marina is not None and checked_marina.get("width") == "900" and checked_marina.get("height") == "900"
    assert "29,4 / 17,3 °C" in check.get_text(" ", strip=True)
    assert "24,9 / 14,1 °C" in check.get_text(" ", strip=True)
    assert "268 h de sol" in check.get_text(" ", strip=True)
    assert "211 h de sol" in check.get_text(" ", strip=True)
    assert "entre la ría del Río Piedras, los pinares y el Atlántico" in check.get_text(" ", strip=True)
    assert check.select_one(f'#{SECTION_ID} a[href="{AEMET_URL}"]') is not None
    climate = check.select_one(f"#{SECTION_ID}")
    assert climate is not None and climate.find_previous("section", id="beach") is not None
    canonical_after = check.find("link", rel="canonical")
    assert (canonical_after.get("href") if canonical_after else None) == canonical_before

    print("Villa Almale V7.6 Spanish climate block and WhatsApp deduplication validated.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: v76-spanish-climate-whatsapp-fix.py /path/to/off-season/es/index.html")
    patch(Path(sys.argv[1]))
