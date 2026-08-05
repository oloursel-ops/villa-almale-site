#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup

DATE = "2026-08-05"
EXPIRY = "2026-11-01T00:00:00+01:00"
WHATSAPP_NUMBER = "33687174067"
STYLE_ID = "villa-almale-v7-4-global-actions"
SCRIPT_ID = "villa-almale-v7-4-global-actions-script"

PAGES = {
    "index.html": "fr",
    "villa-nuevo-portil/index.html": "fr",
    "off-season/fr/index.html": "fr",
    "en/index.html": "en",
    "en/holiday-villa-nuevo-portil/index.html": "en",
    "off-season/index.html": "en",
    "es/index.html": "es",
    "es/alquiler-vacacional-nuevo-portil/index.html": "es",
    "off-season/es/index.html": "es",
}

COPY = {
    "fr": {
        "offer": "Disponibilités limitées cet automne — tarifs directs spéciaux sur certaines dates de septembre et octobre 2026.",
        "offer_cta": "Voir les dates et tarifs",
        "offer_label": "Offre directe automne 2026",
        "close": "Fermer l’offre spéciale",
        "book": "Réserver",
        "book_label": "Voir les disponibilités et réserver Villa Almale",
        "whatsapp_label": "Contacter Villa Almale sur WhatsApp",
        "whatsapp_message": "Bonjour, je souhaite connaître les disponibilités et le tarif direct de la Villa Almale.",
    },
    "en": {
        "offer": "Limited autumn availability — special direct rates for selected September & October 2026 stays.",
        "offer_cta": "Check dates & prices",
        "offer_label": "Autumn 2026 direct offer",
        "close": "Dismiss special offer",
        "book": "Book",
        "book_label": "Check availability and book Villa Almale",
        "whatsapp_label": "Contact Villa Almale on WhatsApp",
        "whatsapp_message": "Hello, I would like to check availability and the direct rate for Villa Almale.",
    },
    "es": {
        "offer": "Disponibilidad limitada este otoño — tarifas directas especiales para determinadas estancias de septiembre y octubre de 2026.",
        "offer_cta": "Ver fechas y precios",
        "offer_label": "Oferta directa otoño 2026",
        "close": "Cerrar la oferta especial",
        "book": "Reservar",
        "book_label": "Consultar disponibilidad y reservar Villa Almale",
        "whatsapp_label": "Contactar con Villa Almale por WhatsApp",
        "whatsapp_message": "Hola, me gustaría consultar la disponibilidad y la tarifa directa de Villa Almale.",
    },
}

BOOKING = {
    "fr": "/reservation.html",
    "en": "/en/reservation.html",
    "es": "/es/reservation.html",
}

CSS = r'''
/* Villa Almale V7.4 — global offer banner and floating actions */
.site-autumn-offer[hidden]{display:none!important}
.site-autumn-offer{position:relative;z-index:65;background:#123f44;color:#fff;border-bottom:1px solid rgba(255,255,255,.2);box-shadow:0 5px 18px rgba(7,34,35,.1)}
.site-autumn-offer__inner{max-width:1220px;margin:0 auto;padding:.72rem 3.35rem .72rem 1.25rem;display:flex;align-items:center;justify-content:center;gap:.85rem;text-align:center;font-size:.94rem;line-height:1.4}
.site-autumn-offer__text{font-weight:650;letter-spacing:.003em}
.site-autumn-offer__cta{display:inline-flex;align-items:center;white-space:nowrap;color:#fff;text-decoration:underline;text-decoration-thickness:1.5px;text-underline-offset:3px;font-weight:800}
.site-autumn-offer__cta:hover,.site-autumn-offer__cta:focus-visible{color:#f7dfb2}
.site-autumn-offer__close{position:absolute;right:.65rem;top:50%;transform:translateY(-50%);width:2.2rem;height:2.2rem;border:0;border-radius:999px;background:transparent;color:#fff;font-size:1.4rem;line-height:1;cursor:pointer}
.site-autumn-offer__close:hover,.site-autumn-offer__close:focus-visible{background:rgba(255,255,255,.14);outline:2px solid rgba(255,255,255,.72);outline-offset:1px}
.site-floating-actions{position:fixed;right:1rem;bottom:1rem;z-index:70;display:flex;align-items:center;gap:.65rem;filter:drop-shadow(0 12px 24px rgba(0,0,0,.2))}
.site-floating-action{display:inline-flex;align-items:center;justify-content:center;gap:.52rem;min-height:3.15rem;padding:.78rem 1rem;border:1px solid rgba(255,255,255,.32);border-radius:999px;color:#fff!important;text-decoration:none!important;font-weight:800;font-size:.94rem;line-height:1;transition:transform .18s ease,box-shadow .18s ease,filter .18s ease}
.site-floating-action:hover,.site-floating-action:focus-visible{transform:translateY(-2px);box-shadow:0 12px 25px rgba(0,0,0,.2);filter:brightness(1.04);outline:2px solid rgba(255,255,255,.75);outline-offset:2px}
.site-floating-action svg{display:block;width:1.22rem;height:1.22rem;flex:0 0 1.22rem;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.site-floating-action--whatsapp{background:#1b875b}
.site-floating-action--booking{background:#123f44}
@media(max-width:720px){
  body.has-site-floating-actions{padding-bottom:5.25rem}
  .site-autumn-offer__inner{display:block;padding:.72rem 3rem .72rem .8rem;font-size:.84rem;text-align:left}
  .site-autumn-offer__cta{margin-top:.18rem}
  .site-floating-actions{left:.65rem;right:.65rem;bottom:calc(.65rem + env(safe-area-inset-bottom));gap:.5rem}
  .site-floating-action{flex:1;min-width:0;min-height:3.35rem;padding:.78rem .7rem;font-size:.9rem}
}
@media(max-width:370px){
  .site-floating-action{font-size:.82rem;gap:.38rem;padding:.72rem .52rem}
  .site-floating-action svg{width:1.1rem;height:1.1rem;flex-basis:1.1rem}
}
'''

SCRIPT = r'''
(function(){
  var offer=document.querySelector('[data-site-global-offer]');
  if(!offer)return;
  var key='villa-almale-autumn-offer-dismissed-v2';
  var expiry=new Date(offer.getAttribute('data-expiry'));
  var dismissed=false;
  try{dismissed=localStorage.getItem(key)==='1';}catch(e){}
  if(dismissed || (Number.isFinite(expiry.getTime()) && new Date()>=expiry)){
    offer.hidden=true;
    return;
  }
  var close=offer.querySelector('[data-site-offer-close]');
  if(close){
    close.addEventListener('click',function(){
      offer.hidden=true;
      try{localStorage.setItem(key,'1');}catch(e){}
    });
  }
})();
'''

WHATSAPP_ICON = '''<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M20.5 11.6a8.5 8.5 0 0 1-12.6 7.5L3.5 20.5l1.4-4.2A8.5 8.5 0 1 1 20.5 11.6Z"></path><path d="M8.2 7.8c.3-.3.7-.3 1 0l1.1 1.5c.2.3.2.6 0 .9l-.6.8c.8 1.6 2 2.8 3.7 3.5l.7-.8c.2-.3.6-.4.9-.2l1.7 1c.3.2.4.6.2.9-.5 1-1.4 1.5-2.5 1.5-3.7-.1-7.4-3.6-7.6-7.2 0-.8.4-1.4 1.4-1.9Z"></path></svg>'''
BOOK_ICON = '''<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M5 4.5h14v15H5z"></path><path d="M8 2.5v4M16 2.5v4M5 9h14M9 13h2M13 13h2M9 16h2"></path></svg>'''


def offer_html(lang: str) -> str:
    c = COPY[lang]
    return f'''<div class="site-autumn-offer" data-site-global-offer data-expiry="{EXPIRY}" data-offer-version="autumn-2026" role="region" aria-label="{c['offer_label']}">
<div class="site-autumn-offer__inner"><span class="site-autumn-offer__text">{c['offer']}</span><a class="site-autumn-offer__cta" data-analytics-event="special_offer_click" href="{BOOKING[lang]}">{c['offer_cta']} →</a></div>
<button class="site-autumn-offer__close" data-site-offer-close type="button" aria-label="{c['close']}">×</button>
</div>'''


def actions_html(lang: str) -> str:
    c = COPY[lang]
    wa_text = quote(c["whatsapp_message"], safe="")
    wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={wa_text}"
    return f'''<nav class="site-floating-actions" aria-label="Villa Almale — contact and booking">
<a class="site-floating-action site-floating-action--whatsapp" data-analytics-event="whatsapp_click" href="{wa_url}" target="_blank" rel="noopener noreferrer" aria-label="{c['whatsapp_label']}">{WHATSAPP_ICON}<span>WhatsApp</span></a>
<a class="site-floating-action site-floating-action--booking" data-analytics-event="booking_click" href="{BOOKING[lang]}" aria-label="{c['book_label']}">{BOOK_ICON}<span>{c['book']}</span></a>
</nav>'''


def first_tag(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.contents:
        if getattr(node, "name", None):
            return node
    raise RuntimeError("HTML fragment contains no tag")


def update_json_ld(node) -> None:
    if isinstance(node, dict):
        typ = node.get("@type")
        types = {typ} if isinstance(typ, str) else set(typ or [])
        if "WebPage" in types:
            node["dateModified"] = DATE
        for value in node.values():
            update_json_ld(value)
    elif isinstance(node, list):
        for value in node:
            update_json_ld(value)


def remove_existing_ui(soup: BeautifulSoup) -> None:
    selectors = [
        "[data-site-global-offer]",
        ".site-floating-actions",
        ".mobile-booking-cta",
        "[data-autumn-offer]",
    ]
    for selector in selectors:
        for node in soup.select(selector):
            node.decompose()
    for element_id in (STYLE_ID, SCRIPT_ID, "villa-almale-v7-3-conversion-script"):
        node = soup.find(id=element_id)
        if node:
            node.decompose()


def patch_page(path: Path, lang: str) -> None:
    text = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(text, "html.parser")
    if soup.head is None or soup.body is None:
        raise RuntimeError(f"{path}: missing head/body")
    if len(soup.find_all("h1")) != 1:
        raise RuntimeError(f"{path}: expected exactly one H1")
    canonical = soup.find("link", rel="canonical")
    canonical_before = canonical.get("href") if canonical else None

    remove_existing_ui(soup)

    style = soup.new_tag("style", id=STYLE_ID)
    style.string = CSS
    soup.head.append(style)

    banner = first_tag(offer_html(lang))
    header = soup.find("header")
    if header is not None:
        header.insert_before(banner)
    else:
        soup.body.insert(0, banner)

    actions = first_tag(actions_html(lang))
    soup.body.append(actions)
    classes = list(soup.body.get("class", []))
    if "has-site-floating-actions" not in classes:
        classes.append("has-site-floating-actions")
    soup.body["class"] = classes

    script = soup.new_tag("script", id=SCRIPT_ID)
    script.string = SCRIPT
    soup.body.append(script)

    for block in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = block.string or block.get_text()
        payload = json.loads(raw)
        update_json_ld(payload)
        block.string = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    output = str(soup)
    if not output.lstrip().lower().startswith("<!doctype"):
        output = "<!DOCTYPE html>\n" + output
    path.write_text(output, encoding="utf-8")

    check = BeautifulSoup(output, "html.parser")
    if len(check.select("[data-site-global-offer]")) != 1:
        raise RuntimeError(f"{path}: offer banner count is not one")
    if len(check.select(".site-floating-actions")) != 1:
        raise RuntimeError(f"{path}: floating actions count is not one")
    if len(check.select(".site-floating-actions a")) != 2:
        raise RuntimeError(f"{path}: expected two floating action links")
    if check.select_one(".mobile-booking-cta") or check.select_one("[data-autumn-offer]"):
        raise RuntimeError(f"{path}: obsolete floating UI remains")
    if len(check.find_all("h1")) != 1:
        raise RuntimeError(f"{path}: H1 changed")
    if any(not h.get_text(" ", strip=True) for h in check.find_all(["h2", "h3"])):
        raise RuntimeError(f"{path}: empty H2/H3")
    new_canonical = check.find("link", rel="canonical")
    canonical_after = new_canonical.get("href") if new_canonical else None
    if canonical_before != canonical_after:
        raise RuntimeError(f"{path}: canonical changed")
    offer = check.select_one("[data-site-global-offer]")
    if COPY[lang]["offer"] not in offer.get_text(" ", strip=True):
        raise RuntimeError(f"{path}: wrong language offer")
    booking_links = check.select('[data-analytics-event="booking_click"]')
    if not any(a.get("href") == BOOKING[lang] for a in booking_links):
        raise RuntimeError(f"{path}: booking route missing")
    whatsapp = check.select_one('[data-analytics-event="whatsapp_click"]')
    if whatsapp is None or not whatsapp.get("href", "").startswith(f"https://wa.me/{WHATSAPP_NUMBER}?"):
        raise RuntimeError(f"{path}: WhatsApp route missing or incorrect")
    for block in check.find_all("script", attrs={"type": "application/ld+json"}):
        json.loads(block.string or block.get_text())


def patch_sitemap(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<lastmod>\d{4}-\d{2}-\d{2}</lastmod>", f"<lastmod>{DATE}</lastmod>", text)
    path.write_text(text, encoding="utf-8")
    if text.count("<loc>") != 9 or text.count(f"<lastmod>{DATE}</lastmod>") != 9:
        raise RuntimeError("sitemap validation failed")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: v74-global-banner-floating-actions.py /path/to/site-root")
    root = Path(sys.argv[1])
    for relative, lang in PAGES.items():
        path = root / relative
        if not path.is_file():
            raise RuntimeError(f"Missing page: {path}")
        patch_page(path, lang)
    patch_sitemap(root / "sitemap.xml")

    english_offseason = (root / "off-season/index.html").read_text(encoding="utf-8")
    required_preserved = [
        "Play golf. Live Andalusia.",
        "See the house before you check the price.",
        "conversion-photo-grid",
        "hero-proof",
        "brand-official",
        "villa-almale-location-golf-v7-2.webp",
    ]
    for marker in required_preserved:
        if marker not in english_offseason:
            raise RuntimeError(f"English off-season page lost marker: {marker}")

    print("Villa Almale V7.4 multilingual banners and floating actions validated successfully.")


if __name__ == "__main__":
    main()
