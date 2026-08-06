#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from bs4 import BeautifulSoup

MARKER = "villa-almale-offseason-shared-v1"
EXPIRY = "2026-11-01T00:00:00+01:00"

CONFIG = {
    "en": {
        "home": "/en/",
        "booking": "/en/reservation.html",
        "offer_label": "Autumn special offer",
        "offer_text": "Limited autumn availability — special direct rates for selected September & October 2026 stays.",
        "offer_link": "Check dates & prices →",
        "dismiss": "Dismiss special offer",
    },
    "fr": {
        "home": "/fr/",
        "booking": "/fr/reservation.html",
        "offer_label": "Offre spéciale d’automne",
        "offer_text": "Disponibilités limitées cet automne — tarifs directs spéciaux pour certains séjours en septembre et octobre 2026.",
        "offer_link": "Voir les dates et tarifs →",
        "dismiss": "Fermer l’offre spéciale",
    },
    "es": {
        "home": "/es/",
        "booking": "/es/reservation.html",
        "offer_label": "Oferta especial de otoño",
        "offer_text": "Disponibilidad limitada este otoño — tarifas directas especiales para determinadas estancias en septiembre y octubre de 2026.",
        "offer_link": "Consultar fechas y precios →",
        "dismiss": "Cerrar la oferta especial",
    },
}

CSS = r'''
/* villa-almale-offseason-shared-v1 */
.autumn-offer-bar{background:#103b35;color:#fff;border-bottom:1px solid rgba(255,255,255,.18);position:relative;z-index:50}
.autumn-offer-inner{max-width:1180px;margin:0 auto;padding:.7rem 3.25rem .7rem 1.25rem;display:flex;align-items:center;justify-content:center;gap:.9rem;text-align:center;font-size:.94rem;line-height:1.35}
.autumn-offer-inner strong{font-weight:750;letter-spacing:.01em}
.autumn-offer-link{display:inline-flex;align-items:center;white-space:nowrap;color:#fff;text-decoration:underline;text-underline-offset:3px;font-weight:750}
.autumn-offer-close{position:absolute;right:.65rem;top:50%;transform:translateY(-50%);width:2.15rem;height:2.15rem;border:0;border-radius:999px;background:transparent;color:#fff;font-size:1.35rem;line-height:1;cursor:pointer}
.autumn-offer-close:hover,.autumn-offer-close:focus-visible{background:rgba(255,255,255,.12);outline:2px solid rgba(255,255,255,.6);outline-offset:1px}
.brand.brand-official{display:inline-flex;align-items:center;gap:.62rem;text-decoration:none}
.brand-official .brand-icon{width:44px;height:44px;flex:0 0 44px;color:currentColor}
.brand-official .brand-wordmark{display:block;font-family:Georgia,"Times New Roman",serif;font-size:1.16rem;line-height:.88;letter-spacing:.02em;text-transform:none}
.brand-official .brand-wordmark strong{font-size:.9em;letter-spacing:.12em}
@media(max-width:720px){
  .autumn-offer-inner{display:block;padding:.72rem 3rem .72rem .85rem;font-size:.86rem}
  .autumn-offer-link{margin-top:.2rem}
  .brand-official .brand-icon{width:38px;height:38px;flex-basis:38px}
}
'''

OFFER_SCRIPT = r'''
(function(){
  var bar=document.querySelector('[data-autumn-offer]');
  if(!bar)return;
  var key='villa-almale-autumn-offer-dismissed-v1';
  var expiry=new Date(bar.getAttribute('data-expiry'));
  var hidden=false;
  try{hidden=localStorage.getItem(key)==='1';}catch(e){}
  if(hidden || (Number.isFinite(expiry.getTime()) && new Date()>=expiry)){bar.hidden=true;return;}
  var close=bar.querySelector('[data-offer-close]');
  if(close)close.addEventListener('click',function(){bar.hidden=true;try{localStorage.setItem(key,'1');}catch(e){}});
})();
'''


def fragment(html: str):
    return BeautifulSoup(html, "html.parser").find()


def brand_html(lang: str) -> str:
    cfg = CONFIG[lang]
    return f'''
<a aria-label="Villa ALMALE" class="brand brand-official" href="{cfg['home']}">
  <svg aria-hidden="true" class="brand-icon" viewBox="0 0 64 64"><path d="M15 45 31.9 12 49 45" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="5"></path><path d="M10 48c7-5 14-5 21 0s14 5 23 0" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="4"></path></svg>
  <span class="brand-wordmark">Villa<br><strong>ALMALE</strong></span>
</a>
'''


def offer_html(lang: str) -> str:
    cfg = CONFIG[lang]
    return f'''
<div class="autumn-offer-bar" data-autumn-offer data-expiry="{EXPIRY}" role="region" aria-label="{cfg['offer_label']}">
  <div class="autumn-offer-inner"><span><strong>{cfg['offer_text'].split(' — ', 1)[0]}</strong> — {cfg['offer_text'].split(' — ', 1)[1]}</span><a class="autumn-offer-link" data-analytics-event="special_offer_click" href="{cfg['booking']}">{cfg['offer_link']}</a></div>
  <button class="autumn-offer-close" data-offer-close type="button" aria-label="{cfg['dismiss']}">×</button>
</div>
'''


def patch(lang: str, path: Path) -> None:
    if lang not in CONFIG:
        raise SystemExit(f"Unsupported language: {lang}")

    text = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(text, "html.parser")
    if not soup.head or not soup.body:
        raise RuntimeError(f"Missing head/body in {path}")

    style = soup.find("style", id=MARKER)
    if style is None:
        style = soup.new_tag("style", id=MARKER)
        soup.head.append(style)
    style.string = CSS

    old_brand = soup.select_one("header.site-header a.brand") or soup.select_one("a.brand")
    if old_brand is None:
        raise RuntimeError(f"Header brand missing in {path}")
    old_brand.replace_with(fragment(brand_html(lang)))

    if soup.select_one("[data-autumn-offer]") is None:
        soup.body.insert(0, fragment(offer_html(lang)))
        script = soup.new_tag("script", id=f"{MARKER}-offer-script")
        script.string = OFFER_SCRIPT
        soup.body.append(script)

    # V7.4 already provides the single canonical WhatsApp + booking action bar.
    # Remove the older standalone WhatsApp control so the two floating systems
    # cannot coexist after this or any later shared off-season update.
    for legacy_whatsapp in soup.select(
        '[data-whatsapp-contact="villa-almale-offseason"], .villa-almale-whatsapp-offseason'
    ):
        legacy_whatsapp.decompose()

    out = str(soup)
    if not out.lstrip().lower().startswith("<!doctype"):
        out = "<!DOCTYPE html>\n" + out
    path.write_text(out, encoding="utf-8")

    check = BeautifulSoup(out, "html.parser")
    cfg = CONFIG[lang]
    brand = check.select_one("header.site-header a.brand-official") or check.select_one("a.brand-official")
    assert brand is not None
    assert brand.get("href") == cfg["home"]
    assert brand.select_one('svg.brand-icon[viewBox="0 0 64 64"]') is not None
    assert brand.select_one("img") is None
    assert len(check.select("[data-autumn-offer]")) == 1
    assert check.select_one("[data-autumn-offer] .autumn-offer-link").get("href") == cfg["booking"]
    assert cfg["offer_text"].split(" — ", 1)[0] in check.select_one("[data-autumn-offer]").get_text(" ", strip=True)
    assert not check.select('[data-whatsapp-contact="villa-almale-offseason"]')
    assert not check.select('.villa-almale-whatsapp-offseason')
    canonical_whatsapp = check.select('.site-floating-action--whatsapp')
    assert len(canonical_whatsapp) == 1
    assert canonical_whatsapp[0].get("href", "").startswith("https://wa.me/33687174067?")
    assert check.find("style", id=MARKER) is not None
    print(f"Validated shared off-season elements for {lang}: logo, autumn banner and one WhatsApp action.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: update-offseason-shared.py LANG PATH_TO_INDEX_HTML")
    patch(sys.argv[1].lower(), Path(sys.argv[2]))
