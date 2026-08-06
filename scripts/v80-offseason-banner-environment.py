#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup


DATE = "2026-08-06"
STYLE_ID = "villa-almale-v80-offseason-banner-environment"
SECTION_ID = "atlantic-setting"
AERIAL_IMAGE = "/assets/images/current/ria-piedras-plage-vue-aerienne.webp"
SUNSET_IMAGE = "/assets/images/current/plage-atlantique-coucher-soleil.webp"

PAGES = {
    "off-season/index.html": "en",
    "off-season/fr/index.html": "fr",
    "off-season/es/index.html": "es",
}

COPY = {
    "en": {
        "main": "Availability in September & October",
        "detail": "From €2,226 / 7 nights · entire villa · flexible arrivals from 12 September",
        "cta": "Check prices",
        "booking": "/en/reservation.html",
        "offer_label": "September and October availability from 2,226 euros",
        "eyebrow": "Between the estuary and the Atlantic",
        "title": "The landscape is part of the stay.",
        "intro": (
            "Nuevo Portil lies between the Ría del Río Piedras, pine woods and long Atlantic beaches—"
            "a natural setting for walks, golf days and unhurried evenings outdoors."
        ),
        "aerial_alt": "Aerial view of the Ría del Río Piedras and the Atlantic beach near Nuevo Portil",
        "aerial_caption": "The Ría del Río Piedras meets the Atlantic",
        "sunset_alt": "Sunset over an Atlantic beach on the Costa de la Luz",
        "sunset_caption": "Evening light on the Costa de la Luz",
    },
    "fr": {
        "main": "Disponibilités en septembre et octobre",
        "detail": "À partir de 2 226 € / 7 nuits · villa entière · arrivées flexibles dès le 12 septembre",
        "cta": "Voir les tarifs",
        "booking": "/reservation.html",
        "offer_label": "Disponibilités en septembre et octobre à partir de 2 226 euros",
        "eyebrow": "Entre la ría et l’Atlantique",
        "title": "Le paysage fait partie du séjour.",
        "intro": (
            "Nuevo Portil s’inscrit entre la Ría del Río Piedras, les pinèdes et les longues plages "
            "atlantiques : un cadre naturel pour marcher, jouer au golf et profiter des soirées dehors."
        ),
        "aerial_alt": "Vue aérienne de la Ría del Río Piedras et de la plage atlantique près de Nuevo Portil",
        "aerial_caption": "La Ría del Río Piedras rejoint l’Atlantique",
        "sunset_alt": "Coucher de soleil sur une plage atlantique de la Costa de la Luz",
        "sunset_caption": "La lumière du soir sur la Costa de la Luz",
    },
    "es": {
        "main": "Disponibilidad en septiembre y octubre",
        "detail": "Desde 2.226 € / 7 noches · villa completa · llegadas flexibles desde el 12 de septiembre",
        "cta": "Ver precios",
        "booking": "/es/reservation.html",
        "offer_label": "Disponibilidad en septiembre y octubre desde 2.226 euros",
        "eyebrow": "Entre la ría y el Atlántico",
        "title": "El paisaje también forma parte de la estancia.",
        "intro": (
            "Nuevo Portil se abre entre la Ría del Río Piedras, los pinares y las largas playas del "
            "Atlántico: un entorno natural para pasear, jugar al golf y alargar las tardes al aire libre."
        ),
        "aerial_alt": "Vista aérea de la Ría del Río Piedras y la playa atlántica cerca de Nuevo Portil",
        "aerial_caption": "La Ría del Río Piedras se encuentra con el Atlántico",
        "sunset_alt": "Atardecer en una playa atlántica de la Costa de la Luz",
        "sunset_caption": "La luz del atardecer en la Costa de la Luz",
    },
}

CSS = r'''
/* Villa Almale V8.0 — one price banner and Atlantic setting */
.site-autumn-offer__inner{display:block;padding:.62rem 3.35rem .68rem;text-align:center}
.offseason-promo-copy{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.08rem;text-align:center}
.offseason-promo-main{display:block;font-family:Georgia,"Times New Roman",serif;font-size:clamp(1.05rem,1.75vw,1.22rem);font-weight:700;letter-spacing:.025em;line-height:1.18}
.offseason-promo-detail{display:block;font-family:Arial,Helvetica,sans-serif;font-size:.82rem;font-weight:600;letter-spacing:.012em;line-height:1.35}
.offseason-promo-detail .site-autumn-offer__cta{display:inline;margin-left:.42rem;font-family:Arial,Helvetica,sans-serif;font-size:inherit;font-weight:800}
.offseason-setting{padding:clamp(3.2rem,6vw,5rem) 0;background:#f4f1e9;color:#153f39}
.offseason-setting__intro{display:grid;grid-template-columns:minmax(0,.75fr) minmax(0,1.25fr);gap:clamp(1rem,4vw,3.8rem);align-items:end;margin-bottom:1.35rem}
.offseason-setting__intro h2{margin:.28rem 0 0;font-size:clamp(1.9rem,3.8vw,3.25rem);line-height:1.06;color:#103b35}
.offseason-setting__intro p{max-width:48rem;margin:0;color:#4d5b57;font-size:1.02rem;line-height:1.7}
.offseason-setting__grid{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(260px,.65fr);gap:.85rem}
.offseason-setting figure{position:relative;min-width:0;margin:0;overflow:hidden;border-radius:20px;background:#d7ded8;box-shadow:0 16px 38px rgba(17,49,44,.12)}
.offseason-setting figure:first-child{aspect-ratio:16/9}
.offseason-setting figure:last-child{aspect-ratio:3/4}
.offseason-setting img{display:block;width:100%;height:100%;object-fit:cover}
.offseason-setting figcaption{position:absolute;right:.75rem;bottom:.75rem;left:.75rem;padding:.68rem .82rem;border:1px solid rgba(255,255,255,.5);border-radius:12px;background:rgba(9,47,42,.78);color:#fff;font-size:.83rem;font-weight:700;line-height:1.35;backdrop-filter:blur(6px)}
@media(max-width:800px){
  .offseason-setting__intro{grid-template-columns:1fr;gap:.65rem}
  .offseason-setting__grid{grid-template-columns:1fr 1fr}
  .offseason-setting figure:first-child{grid-column:1/-1}
  .offseason-setting figure:last-child{aspect-ratio:4/3}
}
@media(max-width:720px){
  .site-autumn-offer__inner{padding:.62rem 2.8rem .68rem .7rem;text-align:center}
  .offseason-promo-main{font-size:1rem}
  .offseason-promo-detail{font-size:.75rem;line-height:1.4}
  .offseason-promo-detail .site-autumn-offer__cta{margin-left:.3rem}
}
@media(max-width:520px){
  .offseason-setting{padding:2.65rem 0}
  .offseason-setting__grid{grid-template-columns:1fr}
  .offseason-setting figure:first-child{grid-column:auto;aspect-ratio:4/3}
  .offseason-setting figure:last-child{aspect-ratio:4/3}
}
'''


def fragment(html: str):
    parsed = BeautifulSoup(html, "html.parser")
    for node in parsed.contents:
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


def surroundings_html(lang: str) -> str:
    c = COPY[lang]
    return f'''
<section class="offseason-setting" id="{SECTION_ID}" aria-labelledby="atlantic-setting-heading-{lang}">
  <div class="shell">
    <div class="offseason-setting__intro">
      <div><span class="eyebrow">{c['eyebrow']}</span><h2 id="atlantic-setting-heading-{lang}">{c['title']}</h2></div>
      <p>{c['intro']}</p>
    </div>
    <div class="offseason-setting__grid">
      <figure><img src="{AERIAL_IMAGE}" width="1600" height="901" loading="lazy" decoding="async" alt="{c['aerial_alt']}"><figcaption>{c['aerial_caption']}</figcaption></figure>
      <figure><img src="{SUNSET_IMAGE}" width="900" height="1200" loading="lazy" decoding="async" alt="{c['sunset_alt']}"><figcaption>{c['sunset_caption']}</figcaption></figure>
    </div>
  </div>
</section>
'''


def patch_page(path: Path, lang: str) -> None:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    if soup.head is None or soup.body is None:
        raise RuntimeError(f"{path}: missing head/body")
    if len(soup.find_all("h1")) != 1:
        raise RuntimeError(f"{path}: expected exactly one H1")

    canonical = soup.find("link", rel="canonical")
    canonical_before = canonical.get("href") if canonical else None

    # The older page-specific banner duplicated the newer global banner.
    for node in soup.select("[data-autumn-offer]"):
        node.decompose()
    # Keep the V7.4 floating WhatsApp action and remove the earlier stand-alone one.
    for node in soup.select('[data-whatsapp-contact="villa-almale-offseason"]'):
        node.decompose()

    for node in soup.select(f"#{STYLE_ID}, #{SECTION_ID}"):
        node.decompose()

    offer = soup.select_one("[data-site-global-offer]")
    if offer is None:
        raise RuntimeError(f"{path}: global offer banner missing")
    c = COPY[lang]
    offer["data-offer-version"] = "september-october-2026-v3"
    offer["aria-label"] = c["offer_label"]
    inner = offer.select_one(".site-autumn-offer__inner")
    if inner is None:
        raise RuntimeError(f"{path}: global offer inner container missing")
    inner.clear()
    promo = fragment(
        f'''<span class="site-autumn-offer__text offseason-promo-copy" data-offseason-promo="september-october-2026"><span class="offseason-promo-main">{c['main']}</span><span class="offseason-promo-detail">{c['detail']} <a class="site-autumn-offer__cta" data-analytics-event="special_offer_click" data-offer-id="september-october-2026" href="{c['booking']}">{c['cta']} →</a></span></span>'''
    )
    inner.append(promo)

    global_script = soup.find(id="villa-almale-v7-4-global-actions-script")
    if global_script and global_script.string:
        for old_key in (
            "villa-almale-autumn-offer-dismissed-v2",
            "villa-almale-spanish-september-offer-v1",
            "villa-almale-spanish-september-offer-v2",
        ):
            global_script.string = global_script.string.replace(
                old_key, "villa-almale-offseason-price-offer-v3"
            )

    style = soup.new_tag("style", id=STYLE_ID)
    style.string = CSS
    soup.head.append(style)

    setting = fragment(surroundings_html(lang))
    anchor = (
        soup.select_one("#location-at-a-glance")
        or soup.select_one("#clima-septiembre-octubre")
        or soup.select_one(".stat-strip")
    )
    if anchor is None:
        raise RuntimeError(f"{path}: no stable insertion anchor for surroundings section")
    anchor.insert_after(setting)

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
    assert len(check.select("[data-autumn-offer]")) == 0
    assert len(check.select('[data-whatsapp-contact="villa-almale-offseason"]')) == 0
    assert len(check.select("[data-site-global-offer]")) == 1
    assert len(check.select(".site-floating-actions .site-floating-action--whatsapp")) == 1
    assert len(check.select("[data-offseason-promo='september-october-2026']")) == 1
    assert len(check.select(f"#{SECTION_ID}")) == 1
    assert len(check.select(f"#{SECTION_ID} img")) == 2
    assert len(check.select(f"img[src='{AERIAL_IMAGE}']")) == 1
    assert len(check.select(f"img[src='{SUNSET_IMAGE}']")) == 1
    assert c["main"] in check.select_one("[data-site-global-offer]").get_text(" ", strip=True)
    assert c["detail"] in check.select_one("[data-site-global-offer]").get_text(" ", strip=True)
    assert check.select_one(f"[data-site-global-offer] a[href='{c['booking']}']") is not None
    assert len(check.find_all("h1")) == 1
    assert all(h.get_text(" ", strip=True) for h in check.find_all(["h2", "h3"]))
    canonical_after = check.find("link", rel="canonical")
    assert (canonical_after.get("href") if canonical_after else None) == canonical_before
    for block in check.find_all("script", attrs={"type": "application/ld+json"}):
        json.loads(block.string or block.get_text())

    print(f"Validated V8.0 price banner deduplication and environment photos: {lang}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: v80-offseason-banner-environment.py /path/to/site-root")
    root = Path(sys.argv[1])
    for relative, lang in PAGES.items():
        path = root / relative
        if not path.is_file():
            raise RuntimeError(f"Missing page: {path}")
        patch_page(path, lang)


if __name__ == "__main__":
    main()
