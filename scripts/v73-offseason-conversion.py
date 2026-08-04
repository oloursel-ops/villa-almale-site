#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from bs4 import BeautifulSoup

DATE = "2026-08-04"
EXPIRY = "2026-11-01T00:00:00+01:00"
BOOKING = "/en/reservation.html"
MARKER = "villa-almale-v7-3-conversion"

CSS = r'''
/* villa-almale-v7-3-conversion */
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
.hero-proof{display:flex;flex-wrap:wrap;gap:.55rem;margin-top:1rem}
.hero-proof span{display:inline-flex;align-items:center;min-height:2rem;padding:.42rem .72rem;border:1px solid rgba(255,255,255,.38);border-radius:999px;background:rgba(8,31,28,.42);color:#fff;font-size:.84rem;line-height:1.2;backdrop-filter:blur(4px)}
.conversion-gallery{padding:1.1rem 0 2.6rem;background:#f4f1e9}
.conversion-gallery .gallery-intro{display:flex;align-items:end;justify-content:space-between;gap:1.5rem;margin-bottom:1rem}
.conversion-gallery .gallery-intro h2{margin:.2rem 0 0;font-size:clamp(1.55rem,3vw,2.35rem)}
.conversion-gallery .gallery-intro p{max-width:42rem;margin:0;color:#4d5b57}
.conversion-photo-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:.7rem}
.conversion-photo-grid figure{margin:0;overflow:hidden;border-radius:14px;background:#d9ddd8;box-shadow:0 8px 24px rgba(17,49,44,.09)}
.conversion-photo-grid figure:nth-child(1),.conversion-photo-grid figure:nth-child(2){grid-column:span 2}
.conversion-photo-grid figure:nth-child(n+3){grid-column:span 1}
.conversion-photo-grid img{display:block;width:100%;height:190px;object-fit:cover;transition:transform .25s ease}
.conversion-photo-grid figure:hover img{transform:scale(1.025)}
.direct-trust{display:flex;flex-wrap:wrap;gap:.55rem;margin-top:.9rem;font-size:.88rem}
.direct-trust span{display:inline-flex;padding:.42rem .68rem;border-radius:999px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.28)}
.mobile-booking-cta{display:none}
@media (max-width:900px){
  .conversion-gallery .gallery-intro{display:block}.conversion-gallery .gallery-intro p{margin-top:.6rem}
  .conversion-photo-grid{grid-template-columns:repeat(2,1fr)}
  .conversion-photo-grid figure,.conversion-photo-grid figure:nth-child(1),.conversion-photo-grid figure:nth-child(2),.conversion-photo-grid figure:nth-child(n+3){grid-column:span 1}
  .conversion-photo-grid figure:first-child{grid-column:1/-1}
  .conversion-photo-grid img{height:175px}
}
@media (max-width:720px){
  body{padding-bottom:4.6rem}
  .autumn-offer-inner{display:block;padding:.72rem 3rem .72rem .85rem;font-size:.86rem}
  .autumn-offer-link{margin-top:.2rem}
  .brand-official .brand-icon{width:38px;height:38px;flex-basis:38px}
  .hero-proof{gap:.4rem}.hero-proof span{font-size:.78rem;padding:.38rem .58rem}
  .conversion-photo-grid{gap:.55rem}.conversion-photo-grid img{height:145px}
  .mobile-booking-cta{position:fixed;left:.7rem;right:.7rem;bottom:calc(.7rem + env(safe-area-inset-bottom));z-index:80;display:flex;align-items:center;justify-content:center;min-height:3.25rem;padding:.8rem 1rem;border-radius:999px;background:#103b35;color:#fff;text-decoration:none;font-weight:800;box-shadow:0 12px 32px rgba(0,0,0,.28)}
}
@media (max-width:430px){.conversion-photo-grid{grid-template-columns:1fr}.conversion-photo-grid figure:first-child{grid-column:auto}.conversion-photo-grid img{height:210px}}
'''

SCRIPT = r'''
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

OFFER_HTML = f'''
<div class="autumn-offer-bar" data-autumn-offer data-expiry="{EXPIRY}" role="region" aria-label="Autumn special offer">
  <div class="autumn-offer-inner"><span><strong>Limited autumn availability</strong> — special direct rates for selected September &amp; October 2026 stays.</span><a class="autumn-offer-link" data-analytics-event="special_offer_click" href="{BOOKING}">Check dates &amp; prices →</a></div>
  <button class="autumn-offer-close" data-offer-close type="button" aria-label="Dismiss special offer">×</button>
</div>
'''

BRAND_HTML = '''
<a aria-label="Villa ALMALE" class="brand brand-official" href="/en/">
  <svg aria-hidden="true" class="brand-icon" viewBox="0 0 64 64"><path d="M15 45 31.9 12 49 45" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="5"></path><path d="M10 48c7-5 14-5 21 0s14 5 23 0" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="4"></path></svg>
  <span class="brand-wordmark">Villa<br><strong>ALMALE</strong></span>
</a>
'''

PROOF_HTML = '''
<div class="hero-proof" aria-label="Booking reassurance">
  <span>Vrbo 9.0/10 · 13 reviews</span>
  <span>Licensed villa · VFT/HU/02471</span>
  <span>Secure direct booking · OwnerRez + Stripe</span>
</div>
'''

GALLERY_HTML = '''
<section class="conversion-gallery" aria-labelledby="real-villa-heading">
  <div class="shell">
    <div class="gallery-intro"><div><span class="eyebrow">The real Villa Almale</span><h2 id="real-villa-heading">See the house before you check the price.</h2></div><p>A private five-bedroom base with pool, garden, shared living spaces and room for the group to settle in after golf.</p></div>
    <div class="conversion-photo-grid">
      <figure><img src="/assets/images/current/hero-villa-piscine-jardin.webp" alt="Villa Almale, private pool and secluded garden" width="1920" height="1440" loading="lazy" decoding="async"></figure>
      <figure><img src="/assets/images/current/piscine-privee.webp" alt="Private fenced saltwater pool at Villa Almale" width="1440" height="1080" loading="lazy" decoding="async"></figure>
      <figure><img src="/assets/images/current/patio-andalou-table-dressee.webp" alt="Andalusian patio prepared for a shared meal" width="1440" height="1080" loading="lazy" decoding="async"></figure>
      <figure><img src="/assets/images/current/salon-salle-a-manger.webp" alt="Villa Almale living and dining room" width="1440" height="1080" loading="lazy" decoding="async"></figure>
      <figure><img src="/assets/images/current/suite-principale.webp" alt="Main suite at Villa Almale" width="1440" height="1080" loading="lazy" decoding="async"></figure>
      <figure><img src="/assets/images/current/chambre-double-bleue.webp" alt="Blue double bedroom at Villa Almale" width="1440" height="1080" loading="lazy" decoding="async"></figure>
    </div>
  </div>
</section>
'''

TRUST_HTML = '''
<div class="direct-trust" aria-label="Direct booking information"><span>Live availability</span><span>Secure Stripe payment</span><span>Licensed VFT/HU/02471</span><span>Vrbo 9.0/10 · 13 reviews</span></div>
'''

MOBILE_CTA_HTML = f'''<a class="mobile-booking-cta" data-analytics-event="booking_click" href="{BOOKING}">Check dates &amp; direct price →</a>'''


def frag(html: str):
    return BeautifulSoup(html, "html.parser").find()


def update_date_modified(payload):
    if isinstance(payload, dict):
        typ = payload.get("@type")
        types = {typ} if isinstance(typ, str) else set(typ or [])
        if "WebPage" in types:
            payload["dateModified"] = DATE
        for value in payload.values():
            update_date_modified(value)
    elif isinstance(payload, list):
        for value in payload:
            update_date_modified(value)


def main(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print("V7.3 conversion patch already present; no change required.")
        return
    soup = BeautifulSoup(text, "html.parser")
    if not soup.head or not soup.body:
        raise RuntimeError("Missing head/body")
    if len(soup.find_all("h1")) != 1:
        raise RuntimeError("Expected exactly one H1")
    h1 = soup.find("h1").get_text(" ", strip=True)
    if h1 != "Play golf. Live Andalusia.":
        raise RuntimeError(f"Unexpected landing page H1: {h1!r}")

    style = soup.new_tag("style", id=MARKER)
    style.string = CSS
    soup.head.append(style)

    header = soup.select_one("header.site-header")
    if header is None:
        raise RuntimeError("Site header missing")
    old_brand = header.select_one("a.brand")
    if old_brand is None:
        raise RuntimeError("Header brand missing")
    old_brand.replace_with(frag(BRAND_HTML))

    soup.body.insert(0, frag(OFFER_HTML))

    hero_actions = soup.select_one(".hero-season .hero-actions")
    if hero_actions is None:
        raise RuntimeError("Hero actions missing")
    hero_actions.insert_after(frag(PROOF_HTML))

    stat_strip = soup.select_one("section.stat-strip")
    if stat_strip is None:
        raise RuntimeError("Stat strip missing")
    stat_strip.insert_after(frag(GALLERY_HTML))

    golf_notice = soup.select_one("#golf .notice-box.golf-access")
    if golf_notice is None:
        raise RuntimeError("Golf access notice missing")
    replacement = BeautifulSoup('<div class="notice-box golf-access" style="margin-bottom:22px"><strong>Golf at the doorstep.</strong> The official pedestrian entrance to Golf Nuevo Portil is beside the residential entrance and reached in under one minute on foot.</div>', "html.parser").div
    golf_notice.replace_with(replacement)

    final_banner = soup.select_one("section.section-sm .banner")
    if final_banner is None:
        raise RuntimeError("Final booking banner missing")
    copy_block = final_banner.find("div", recursive=False)
    if copy_block is None:
        raise RuntimeError("Final banner copy block missing")
    copy_block.append(frag(TRUST_HTML))

    soup.body.append(frag(MOBILE_CTA_HTML))
    script = soup.new_tag("script", id=f"{MARKER}-script")
    script.string = SCRIPT
    soup.body.append(script)

    for block in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = block.string or block.get_text()
        payload = json.loads(raw)
        update_date_modified(payload)
        block.string = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    out = "<!DOCTYPE html>\n" + str(soup).split("<!DOCTYPE html>", 1)[-1].lstrip()
    path.write_text(out, encoding="utf-8")

    check = BeautifulSoup(out, "html.parser")
    assert check.find("style", id=MARKER)
    assert check.select_one("[data-autumn-offer]")
    assert check.select_one(".brand-official .brand-icon")
    assert len(check.select(".conversion-photo-grid img")) == 6
    assert len(check.select(".hero-proof span")) == 3
    assert check.select_one(".mobile-booking-cta")
    assert "small private gate on the property boundary" not in check.select_one("#golf .golf-access").get_text(" ", strip=True)
    assert len(check.find_all("h1")) == 1
    assert all(h.get_text(" ", strip=True) for h in check.find_all(["h2", "h3"]))
    print("Villa Almale English landing page V7.3 conversion patch validated.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: v73-offseason-conversion.py /path/to/off-season/index.html")
    main(Path(sys.argv[1]))
