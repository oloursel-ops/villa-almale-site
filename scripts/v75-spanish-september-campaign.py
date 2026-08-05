#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup


DATE = "2026-08-05"
STYLE_ID = "villa-almale-v75-spanish-campaign"
OFFER_ID = "https://villanuevoportil.com/off-season/es/#offer-2026-09-26"
BOOKING = "/es/reservation.html"
WHATSAPP_NUMBER = "33687174067"
WHATSAPP_MESSAGE = (
    "Hola, me interesa una estancia en septiembre u octubre de 2026. "
    "¿Qué fechas y tarifas están disponibles?"
)

HOME_ROUTES = {
    "off-season/index.html": "/en/",
    "off-season/fr/index.html": "/",
    "off-season/es/index.html": "/es/",
}

TITLE = "Septiembre en la Costa de la Luz | Villa Almale"
DESCRIPTION = (
    "Villa de 5 dormitorios para 4–6 adultos: golf a menos de 1 minuto, piscina y playa a pie. "
    "Disponibilidad en septiembre y octubre desde 2.226 € por 7 noches."
)
WEBPAGE_NAME = "Golf, Atlántico y una casa privada para disfrutar juntos | Villa Almale"
WEBPAGE_DESCRIPTION = (
    "Una villa privada de cinco dormitorios para 4–6 adultos en septiembre, con piscina, "
    "playa a pie y acceso oficial al Golf Nuevo Portil a menos de un minuto."
)

CSS = r'''
/* Villa Almale V7.5 — Spanish September campaign landing page */
.es-campaign-hero-proof{display:flex;flex-wrap:wrap;gap:.55rem;margin-top:1rem}
.es-campaign-hero-proof span{display:inline-flex;align-items:center;min-height:2rem;padding:.42rem .72rem;border:1px solid rgba(255,255,255,.38);border-radius:999px;background:rgba(8,31,28,.44);color:#fff;font-size:.84rem;line-height:1.2;backdrop-filter:blur(4px)}
.es-campaign-gallery{padding:3.2rem 0;background:#fff}
.es-gallery-intro{display:flex;align-items:end;justify-content:space-between;gap:1.5rem;margin-bottom:1.15rem}
.es-gallery-intro h2{margin:.25rem 0 0;font-size:clamp(1.6rem,3vw,2.4rem)}
.es-gallery-intro p{max-width:42rem;margin:0;color:#4d5b57}
.es-photo-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:.7rem}
.es-photo-grid figure{margin:0;overflow:hidden;border-radius:14px;background:#d9ddd8;box-shadow:0 8px 24px rgba(17,49,44,.09)}
.es-photo-grid figure:nth-child(1),.es-photo-grid figure:nth-child(2){grid-column:span 2}
.es-photo-grid figure:nth-child(n+3){grid-column:span 1}
.es-photo-grid img{display:block;width:100%;height:190px;object-fit:cover;transition:transform .25s ease}
.es-photo-grid figure:hover img{transform:scale(1.025)}
.es-direct-trust{display:flex;flex-wrap:wrap;gap:.55rem;margin-top:.9rem;font-size:.88rem}
.es-direct-trust span{display:inline-flex;padding:.42rem .68rem;border-radius:999px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.28)}
@media(max-width:900px){
  .es-gallery-intro{display:block}.es-gallery-intro p{margin-top:.6rem}
  .es-photo-grid{grid-template-columns:repeat(2,1fr)}
  .es-photo-grid figure,.es-photo-grid figure:nth-child(1),.es-photo-grid figure:nth-child(2),.es-photo-grid figure:nth-child(n+3){grid-column:span 1}
  .es-photo-grid figure:first-child{grid-column:1/-1}
  .es-photo-grid img{height:175px}
}
@media(max-width:720px){
  .es-campaign-hero-proof{gap:.4rem}.es-campaign-hero-proof span{font-size:.78rem;padding:.38rem .58rem}
  .es-campaign-gallery{padding:2.35rem 0}
  .es-photo-grid{gap:.55rem}.es-photo-grid img{height:145px}
}
@media(max-width:430px){
  .es-photo-grid{grid-template-columns:1fr}.es-photo-grid figure:first-child{grid-column:auto}.es-photo-grid img{height:210px}
}
'''


def fragment(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.contents:
        if getattr(node, "name", None):
            return node
    raise RuntimeError("HTML fragment contains no tag")


def set_meta(soup: BeautifulSoup, *, name: str | None = None, prop: str | None = None, value: str) -> None:
    selector = {"name": name} if name else {"property": prop}
    node = soup.find("meta", attrs=selector)
    if node is None:
        node = soup.new_tag("meta")
        for key, item in selector.items():
            node[key] = item
        soup.head.append(node)
    node["content"] = value


def patch_brand_links(root: Path) -> None:
    for relative, home in HOME_ROUTES.items():
        path = root / relative
        if not path.is_file():
            raise RuntimeError(f"Missing page: {path}")
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        brand = soup.select_one("header.site-header a.brand")
        if brand is None:
            raise RuntimeError(f"Brand link missing: {path}")
        brand["href"] = home
        brand.attrs.pop("target", None)
        brand.attrs.pop("rel", None)
        output = str(soup)
        if not output.lstrip().lower().startswith("<!doctype"):
            output = "<!DOCTYPE html>\n" + output
        path.write_text(output, encoding="utf-8")


def hero_actions_html() -> str:
    whatsapp = f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(WHATSAPP_MESSAGE, safe='')}"
    return f'''
<div class="hero-actions">
  <a class="button primary" data-analytics-event="booking_click" href="{BOOKING}">Ver fechas y precio directo →</a>
  <a class="button outline-light" data-analytics-event="whatsapp_click" href="{whatsapp}" target="_blank" rel="noopener noreferrer">Consultar por WhatsApp</a>
</div>
'''


def hero_proof_html() -> str:
    return '''
<div class="es-campaign-hero-proof" aria-label="Garantías de reserva">
  <span>Vrbo 9,0/10 · 13 reseñas</span>
  <span>Vivienda turística · VFT/HU/02471</span>
  <span>Reserva directa segura · OwnerRez + Stripe</span>
</div>
'''


def gallery_html() -> str:
    return '''
<section class="es-campaign-gallery" aria-labelledby="villa-real-heading">
  <div class="shell">
    <div class="es-gallery-intro">
      <div><span class="eyebrow">La Villa Almale real</span><h2 id="villa-real-heading">Una casa para compartir, no varias habitaciones de hotel.</h2></div>
      <p>Espacios privados y comunes para que 4–6 adultos puedan jugar, descansar, cocinar y disfrutar juntos de la Costa de la Luz.</p>
    </div>
    <div class="es-photo-grid">
      <figure><img src="/assets/images/current/hero-villa-piscine-jardin.webp" alt="Villa Almale, piscina privada y jardín sin miradas" width="1920" height="1440" loading="lazy" decoding="async"></figure>
      <figure><img src="/assets/images/current/piscine-privee.webp" alt="Piscina privada vallada de Villa Almale" width="1440" height="1080" loading="lazy" decoding="async"></figure>
      <figure><img src="/assets/images/current/patio-andalou-table-dressee.webp" alt="Patio andaluz preparado para comer juntos" width="1440" height="1080" loading="lazy" decoding="async"></figure>
      <figure><img src="/assets/images/current/salon-salle-a-manger.webp" alt="Salón y comedor de Villa Almale" width="1440" height="1080" loading="lazy" decoding="async"></figure>
      <figure><img src="/assets/images/current/suite-principale.webp" alt="Suite principal de Villa Almale" width="1440" height="1080" loading="lazy" decoding="async"></figure>
      <figure><img src="/assets/images/current/chambre-double-bleue.webp" alt="Dormitorio doble azul de Villa Almale" width="1440" height="1080" loading="lazy" decoding="async"></figure>
    </div>
  </div>
</section>
'''


def update_json_ld(soup: BeautifulSoup) -> None:
    for block in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = block.string or block.get_text()
        payload = json.loads(raw)
        graph = payload.get("@graph") if isinstance(payload, dict) else None
        if not isinstance(graph, list):
            continue
        graph[:] = [
            node
            for node in graph
            if not (isinstance(node, dict) and node.get("@id") == OFFER_ID)
        ]
        for node in graph:
            if not isinstance(node, dict):
                continue
            typ = node.get("@type")
            types = {typ} if isinstance(typ, str) else set(typ or [])
            if "Accommodation" in types:
                node["description"] = WEBPAGE_DESCRIPTION
                if node.get("offers") == {"@id": OFFER_ID}:
                    node.pop("offers", None)
            elif "WebPage" in types:
                node["name"] = WEBPAGE_NAME
                node["description"] = WEBPAGE_DESCRIPTION
                node["dateModified"] = DATE
            elif "FAQPage" in types:
                questions = node.get("mainEntity", [])
                for question in questions:
                    if "estancia corta" in question.get("name", "").lower():
                        question["name"] = "¿Qué flexibilidad hay a partir del 12 de septiembre?"
                        question["acceptedAnswer"] = {
                            "@type": "Answer",
                            "text": "A partir del 12 de septiembre se aceptan llegadas flexibles según disponibilidad, con una estancia mínima de siete noches. La página de reserva muestra las fechas aplicables.",
                        }
        block.string = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def patch_spanish_landing(path: Path) -> None:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    if soup.head is None or soup.body is None:
        raise RuntimeError("Spanish landing page is missing head/body")
    if len(soup.find_all("h1")) != 1:
        raise RuntimeError("Spanish landing page must contain exactly one H1")

    for node in soup.select(
        f"#{STYLE_ID}, .es-september-offer, .es-campaign-gallery, .es-campaign-hero-proof, .es-direct-trust"
    ):
        node.decompose()

    soup.title.string = TITLE
    set_meta(soup, name="description", value=DESCRIPTION)
    set_meta(soup, name="twitter:title", value=TITLE)
    set_meta(soup, name="twitter:description", value=DESCRIPTION)
    set_meta(soup, prop="og:title", value=TITLE)
    set_meta(soup, prop="og:description", value=DESCRIPTION)

    style = soup.new_tag("style", id=STYLE_ID)
    style.string = CSS
    soup.head.append(style)

    nav = soup.select_one("header.site-header nav.nav-links")
    if nav is None:
        raise RuntimeError("Spanish navigation missing")
    nav.clear()
    nav_fragment = BeautifulSoup(
        f'''<a href="#why">La experiencia</a><a href="#house">La casa</a><a href="#golf">Golf</a><a href="#practical">Información práctica</a><a class="nav-cta" data-analytics-event="booking_click" href="{BOOKING}">Ver fechas</a>''',
        "html.parser",
    )
    for child in list(nav_fragment.contents):
        nav.append(child)

    hero = soup.select_one("section.hero-season")
    hero_content = hero.select_one(".hero-content") if hero else None
    if hero is None or hero_content is None:
        raise RuntimeError("Spanish campaign hero missing")
    hero_content.select_one(".eyebrow").string = "Septiembre en la Costa de la Luz"
    hero_content.select_one("h1").string = "Golf, Atlántico y una casa privada para disfrutar juntos."
    hero_content.select_one("p.lead").string = (
        "Villa de cinco dormitorios para grupos de 4 a 6 adultos, con piscina privada, jardín, "
        "playa a pie y acceso oficial al Golf Nuevo Portil a menos de un minuto."
    )
    old_actions = hero_content.select_one(".hero-actions")
    if old_actions is None:
        raise RuntimeError("Spanish hero actions missing")
    new_actions = fragment(hero_actions_html())
    old_actions.replace_with(new_actions)
    new_actions.insert_after(fragment(hero_proof_html()))

    hero_facts = hero.select_one(".hero-facts")
    if hero_facts is None:
        raise RuntimeError("Spanish hero facts missing")
    hero_facts.clear()
    facts = BeautifulSoup(
        '''
<div class="hero-fact"><strong>5</strong><span>dormitorios</span></div>
<div class="hero-fact"><strong>4–6</strong><span>adultos · grupo ideal</span></div>
<div class="hero-fact"><strong>&lt; 1 min</strong><span>Golf Nuevo Portil a pie</span></div>
<div class="hero-fact"><strong>Privada</strong><span>piscina · playa a pie</span></div>
''',
        "html.parser",
    )
    for child in list(facts.contents):
        hero_facts.append(child)

    stat_strip = soup.select_one("section.stat-strip")
    if stat_strip:
        stat_strip.decompose()
    hero.insert_after(fragment(gallery_html()))

    why = soup.select_one("section#why")
    house = soup.select_one("section#house")
    golf = soup.select_one("section#golf")
    if why is None or house is None or golf is None:
        raise RuntimeError("Spanish landing content sections missing")
    house.extract()
    golf.extract()
    why.insert_after(house)
    house.insert_after(golf)

    golf_notice = golf.select_one(".notice-box.golf-access")
    if golf_notice:
        golf_notice.clear()
        strong = soup.new_tag("strong")
        strong.string = "Golf a la puerta de casa."
        golf_notice.append(strong)
        golf_notice.append(" El acceso peatonal oficial al Golf Nuevo Portil se alcanza en menos de un minuto desde la entrada residencial.")

    practical = soup.select_one("section#practical")
    short_panel = None
    if practical:
        for panel in practical.select("article.info-panel"):
            heading = panel.find("h3")
            if heading and "Estancias cortas" in heading.get_text(" ", strip=True):
                short_panel = panel
                break
    if short_panel:
        short_panel.find("h3").string = "Llegadas flexibles desde el 12 de septiembre"
        short_panel.find("p").string = (
            "A partir del 12 de septiembre aceptamos llegadas flexibles según disponibilidad, "
            "con una estancia mínima de siete noches."
        )

    for details in soup.select(".faq details"):
        summary = details.find("summary")
        if summary and "estancia corta" in summary.get_text(" ", strip=True).lower():
            summary.string = "¿Qué flexibilidad hay a partir del 12 de septiembre?"
            paragraph = details.find("p")
            paragraph.string = (
                "A partir del 12 de septiembre se aceptan llegadas flexibles según disponibilidad, "
                "con una estancia mínima de siete noches. La página de reserva muestra las fechas aplicables."
            )

    banner = soup.select_one("section.section-sm .banner")
    if banner:
        banner.select_one(".eyebrow").string = "Reserva directa"
        banner.select_one("h2").string = "Una semana de golf sin la rutina de un hotel."
        banner.select_one("p").string = (
            "Cinco dormitorios, espacios compartidos y varios campos desde una misma casa. "
            "Consulta fechas y precio completo mediante OwnerRez."
        )
        trust = fragment(
            '''<div class="es-direct-trust" aria-label="Información de reserva directa"><span>Disponibilidad en tiempo real</span><span>Pago seguro con Stripe</span><span>VFT/HU/02471</span><span>Vrbo 9,0/10 · 13 reseñas</span></div>'''
        )
        banner.find("div", recursive=False).append(trust)
        cta = banner.select_one("a.button")
        cta.string = "Ver fechas y precio directo →"
        cta["href"] = BOOKING
        cta["data-analytics-event"] = "booking_click"

    global_offer = soup.select_one("[data-site-global-offer]")
    if global_offer:
        global_offer["data-offer-version"] = "september-2026-es"
        global_offer["aria-label"] = "Disponibilidad en septiembre y octubre"
        global_offer.select_one(".site-autumn-offer__text").string = (
            "Disponibilidad en septiembre y octubre — desde 2.226 € por 7 noches para la villa completa · llegadas flexibles desde el 12 de septiembre."
        )
        global_cta = global_offer.select_one(".site-autumn-offer__cta")
        global_cta.string = "Ver disponibilidad y precios →"
        global_cta["href"] = BOOKING
        global_cta["data-analytics-event"] = "special_offer_click"
        global_cta["data-offer-id"] = "september-october-2026-es"
        global_script = soup.find(id="villa-almale-v7-4-global-actions-script")
        if global_script and global_script.string:
            global_script.string = global_script.string.replace(
                "villa-almale-autumn-offer-dismissed-v2",
                "villa-almale-spanish-september-offer-v1",
            )

    update_json_ld(soup)

    output = str(soup)
    if not output.lstrip().lower().startswith("<!doctype"):
        output = "<!DOCTYPE html>\n" + output
    path.write_text(output, encoding="utf-8")

    check = BeautifulSoup(output, "html.parser")
    assert len(check.find_all("h1")) == 1
    assert check.find("h1").get_text(" ", strip=True) == "Golf, Atlántico y una casa privada para disfrutar juntos."
    assert len(check.select(".es-september-offer")) == 0
    assert len(check.select(".es-photo-grid img")) == 6
    assert len(check.select(".es-campaign-hero-proof span")) == 3
    assert len(check.select(".es-direct-trust")) == 1
    assert len(check.select(".hero-facts .hero-fact")) == 4
    assert check.select_one('[data-analytics-event="special_offer_click"]')
    assert check.select_one('[data-analytics-event="booking_click"]')
    assert check.select_one('[data-analytics-event="whatsapp_click"]')
    assert "2.226 €" in check.get_text(" ", strip=True)
    assert "371 € por adulto" not in check.get_text(" ", strip=True)
    assert "26 de septiembre – 3 de octubre" not in check.get_text(" ", strip=True)
    assert "Llegadas flexibles desde el 12 de septiembre" in check.get_text(" ", strip=True)
    assert len(check.select(".hero-actions a")) == 2
    assert not any(
        "a class=" in str(node)
        for node in check.select_one(".hero-actions").find_all(string=True, recursive=False)
    )
    assert output.index('id="house"') < output.index('id="golf"')
    for block in check.find_all("script", attrs={"type": "application/ld+json"}):
        payload = json.loads(block.string or block.get_text())
        assert all(
            not isinstance(node, dict) or node.get("@id") != OFFER_ID
            for node in payload.get("@graph", [])
        )


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: v75-spanish-september-campaign.py /path/to/site-root")
    root = Path(sys.argv[1])
    patch_brand_links(root)
    patch_spanish_landing(root / "off-season/es/index.html")

    for relative, home in HOME_ROUTES.items():
        soup = BeautifulSoup((root / relative).read_text(encoding="utf-8"), "html.parser")
        brand = soup.select_one("header.site-header a.brand")
        if brand is None or brand.get("href") != home:
            raise RuntimeError(f"Incorrect brand destination in {relative}")

    print("Villa Almale V7.5 Spanish September landing page and multilingual logo routes validated.")


if __name__ == "__main__":
    main()
