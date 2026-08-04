#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup

MARKER = "villa-almale-offseason-shared-v1"
PHONE = "33687174067"
EXPIRY = "2026-11-01T00:00:00+01:00"

CONFIG = {
    "en": {
        "home": "/en/",
        "booking": "/en/reservation.html",
        "offer_label": "Autumn special offer",
        "offer_text": "Limited autumn availability — special direct rates for selected September & October 2026 stays.",
        "offer_link": "Check dates & prices →",
        "dismiss": "Dismiss special offer",
        "whatsapp": "Hello, I would like information about Villa Almale availability.",
        "whatsapp_label": "Contact Villa Almale on WhatsApp",
    },
    "fr": {
        "home": "/fr/",
        "booking": "/fr/reservation.html",
        "offer_label": "Offre spéciale d’automne",
        "offer_text": "Disponibilités limitées cet automne — tarifs directs spéciaux pour certains séjours en septembre et octobre 2026.",
        "offer_link": "Voir les dates et tarifs →",
        "dismiss": "Fermer l’offre spéciale",
        "whatsapp": "Bonjour, je souhaite obtenir des informations sur les disponibilités de Villa Almale.",
        "whatsapp_label": "Contacter Villa Almale sur WhatsApp",
    },
    "es": {
        "home": "/es/",
        "booking": "/es/reservation.html",
        "offer_label": "Oferta especial de otoño",
        "offer_text": "Disponibilidad limitada este otoño — tarifas directas especiales para determinadas estancias en septiembre y octubre de 2026.",
        "offer_link": "Consultar fechas y precios →",
        "dismiss": "Cerrar la oferta especial",
        "whatsapp": "Hola, me gustaría recibir información sobre la disponibilidad de Villa Almale.",
        "whatsapp_label": "Contactar con Villa Almale por WhatsApp",
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
.villa-almale-whatsapp-offseason{position:fixed;right:max(22px,env(safe-area-inset-right));bottom:max(24px,env(safe-area-inset-bottom));z-index:86;display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:54px;padding:0 19px 0 15px;border:1px solid rgba(224,179,104,.72);border-radius:999px;background:rgba(13,70,72,.96);color:#fff;box-shadow:0 12px 34px rgba(0,31,34,.30);font:700 15px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;letter-spacing:.01em;text-decoration:none;-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);-webkit-tap-highlight-color:transparent;transition:transform .18s ease,box-shadow .18s ease,background .18s ease}
.villa-almale-whatsapp-offseason:hover,.villa-almale-whatsapp-offseason:focus-visible{transform:translateY(-2px);background:#0a3d40;box-shadow:0 16px 40px rgba(0,31,34,.36);outline:2px solid rgba(255,255,255,.85);outline-offset:3px}
.villa-almale-whatsapp-offseason svg{width:28px;height:28px;display:block;fill:currentColor;flex:0 0 28px}
.villa-almale-whatsapp-offseason span{white-space:nowrap}
@media(max-width:720px){
  .autumn-offer-inner{display:block;padding:.72rem 3rem .72rem .85rem;font-size:.86rem}
  .autumn-offer-link{margin-top:.2rem}
  .brand-official .brand-icon{width:38px;height:38px;flex-basis:38px}
  .villa-almale-whatsapp-offseason{right:max(15px,env(safe-area-inset-right));bottom:calc(5.5rem + env(safe-area-inset-bottom));width:56px;height:56px;min-height:56px;padding:0;border-radius:50%}
  .villa-almale-whatsapp-offseason span{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
}
@media print{.villa-almale-whatsapp-offseason{display:none!important}}
@media(prefers-reduced-motion:reduce){.villa-almale-whatsapp-offseason{transition:none}}
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


def whatsapp_html(lang: str) -> str:
    cfg = CONFIG[lang]
    url = f"https://wa.me/{PHONE}?text={quote(cfg['whatsapp'], safe='')}"
    return f'''
<a class="villa-almale-whatsapp-offseason" data-whatsapp-contact="villa-almale-offseason" href="{url}" target="_blank" rel="noopener noreferrer" aria-label="{cfg['whatsapp_label']}" title="WhatsApp">
  <svg viewBox="0 0 32 32" aria-hidden="true" focusable="false"><path d="M19.11 17.2c-.26-.13-1.54-.76-1.78-.85-.24-.09-.41-.13-.59.13-.17.26-.67.85-.82 1.02-.15.17-.3.2-.56.07-.26-.13-1.09-.4-2.08-1.29-.77-.68-1.29-1.53-1.44-1.79-.15-.26-.02-.4.11-.53.12-.12.26-.3.39-.46.13-.15.17-.26.26-.43.09-.17.04-.33-.02-.46-.07-.13-.59-1.42-.8-1.94-.21-.51-.43-.44-.59-.45h-.5c-.17 0-.46.07-.69.33-.24.26-.91.89-.91 2.18 0 1.28.94 2.52 1.07 2.69.13.17 1.84 2.81 4.46 3.94.62.27 1.11.43 1.49.55.63.2 1.2.17 1.65.1.5-.07 1.54-.63 1.76-1.24.22-.61.22-1.13.15-1.24-.06-.11-.24-.17-.5-.3z"></path><path d="M16.04 3.2A12.55 12.55 0 0 0 5.18 22.03L3.2 28.8l6.94-1.82a12.56 12.56 0 1 0 5.9-23.78zm0 22.83c-2.05 0-4.05-.55-5.79-1.59l-.41-.24-4.12 1.08 1.1-4.01-.27-.42a10.27 10.27 0 1 1 9.49 5.18z"></path></svg>
  <span>WhatsApp</span>
</a>
'''


def patch(lang: str, path: Path) -> None:
    if lang not in CONFIG:
        raise SystemExit(f"Unsupported language: {lang}")

    text = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(text, "html.parser")
    if not soup.head or not soup.body:
        raise RuntimeError(f"Missing head/body in {path}")

    if soup.find("style", id=MARKER) is None:
        style = soup.new_tag("style", id=MARKER)
        style.string = CSS
        soup.head.append(style)

    old_brand = soup.select_one("header.site-header a.brand") or soup.select_one("a.brand")
    if old_brand is None:
        raise RuntimeError(f"Header brand missing in {path}")
    old_brand.replace_with(fragment(brand_html(lang)))

    if soup.select_one("[data-autumn-offer]") is None:
        soup.body.insert(0, fragment(offer_html(lang)))
        script = soup.new_tag("script", id=f"{MARKER}-offer-script")
        script.string = OFFER_SCRIPT
        soup.body.append(script)

    if soup.select_one('[data-whatsapp-contact="villa-almale-offseason"]') is None:
        soup.body.append(fragment(whatsapp_html(lang)))

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
    whatsapp = check.select_one('[data-whatsapp-contact="villa-almale-offseason"]')
    assert whatsapp is not None
    assert f"wa.me/{PHONE}" in whatsapp.get("href", "")
    assert len(check.select('[data-whatsapp-contact="villa-almale-offseason"]')) == 1
    assert check.find("style", id=MARKER) is not None
    print(f"Validated shared off-season elements for {lang}: logo, autumn banner and WhatsApp button.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: update-offseason-shared.py LANG PATH_TO_INDEX_HTML")
    patch(sys.argv[1].lower(), Path(sys.argv[2]))
