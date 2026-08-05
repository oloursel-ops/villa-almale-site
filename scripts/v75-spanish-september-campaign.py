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

TITLE = "Villa, playa y experiencias en la Costa de la Luz | Villa Almale"
DESCRIPTION = (
    "Villa de 5 dormitorios para 4–6 adultos, con piscina privada, playa a pie y actividades "
    "organizadas por temas. Disponibilidad en septiembre y octubre desde 2.226 € por 7 noches."
)
WEBPAGE_NAME = "Villa, Atlántico y cinco formas de disfrutar la Costa de la Luz | Villa Almale"
WEBPAGE_DESCRIPTION = (
    "Una villa privada de cinco dormitorios para 4–6 adultos, con piscina, playa a pie, "
    "actividades náuticas, golf y excursiones por el oeste de Andalucía."
)

CSS = r'''
/* Villa Almale V7.6 — Spanish themed campaign landing page */
.site-autumn-offer__inner{display:block;padding:.62rem 3.35rem .66rem;text-align:center}
.site-autumn-offer__text.es-promo-copy{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.08rem;text-align:center}
.es-promo-main{display:block;font-family:Georgia,"Times New Roman",serif;font-size:clamp(1.05rem,1.75vw,1.22rem);font-weight:700;letter-spacing:.025em;line-height:1.18}
.es-promo-detail{display:block;font-family:Arial,Helvetica,sans-serif;font-size:.82rem;font-weight:600;letter-spacing:.012em;line-height:1.35}
.es-promo-detail .site-autumn-offer__cta{display:inline;margin-left:.42rem;font-family:Arial,Helvetica,sans-serif;font-size:inherit;font-weight:800}
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
.es-theme-section{scroll-margin-top:6.5rem}
.es-theme-section .section-heading{margin-bottom:1.6rem}
.es-theme-section .eyebrow{display:inline-flex;align-items:center;gap:.45rem}
.es-theme-section .eyebrow::before{content:attr(data-theme-number);display:inline-grid;place-items:center;width:2rem;height:2rem;border-radius:999px;background:#123f44;color:#fff;font-family:Arial,Helvetica,sans-serif;font-size:.72rem;font-weight:800;letter-spacing:.04em}
.es-theme-villa{background:#fff}
.es-theme-beach{background:#f5efe4}
.es-theme-golf{background:#edf3ed}
.es-theme-nautical{background:#eaf4f5}
.es-theme-tourism{background:#123f44;color:#fff}
.es-theme-tourism .section-heading p{color:rgba(255,255,255,.78)}
.es-theme-tourism .eyebrow::before{background:#f7dfb2;color:#123f44}
.es-theme-tourism .timeline article{border-color:rgba(255,255,255,.2)}
.es-theme-section .theme-links{display:flex;flex-wrap:wrap;gap:.65rem;margin-top:1rem}
.es-theme-section .theme-links a{font-weight:750}
.es-theme-section .theme-photo img{width:100%;height:100%;min-height:360px;object-fit:cover}
.es-theme-nautical .notice-box{background:rgba(255,255,255,.72)}
@media(max-width:900px){
  .es-gallery-intro{display:block}.es-gallery-intro p{margin-top:.6rem}
  .es-photo-grid{grid-template-columns:repeat(2,1fr)}
  .es-photo-grid figure,.es-photo-grid figure:nth-child(1),.es-photo-grid figure:nth-child(2),.es-photo-grid figure:nth-child(n+3){grid-column:span 1}
  .es-photo-grid figure:first-child{grid-column:1/-1}
  .es-photo-grid img{height:175px}
}
@media(max-width:720px){
  .site-autumn-offer__inner{padding:.62rem 2.8rem .68rem .7rem;text-align:center}
  .es-promo-main{font-size:1rem}
  .es-promo-detail{font-size:.75rem;line-height:1.4}
  .es-promo-detail .site-autumn-offer__cta{margin-left:.3rem}
  .es-campaign-hero-proof{gap:.4rem}.es-campaign-hero-proof span{font-size:.78rem;padding:.38rem .58rem}
  .es-campaign-gallery{padding:2.35rem 0}
  .es-photo-grid{gap:.55rem}.es-photo-grid img{height:145px}
  .es-theme-section .theme-photo img{min-height:250px}
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


def villa_theme_html() -> str:
    return '''
<section class="section es-theme-section es-theme-villa" id="villa" aria-labelledby="villa-heading">
  <div class="shell two-col">
    <div class="house-photo theme-photo"><img src="/assets/images/current/hero-villa-piscine-jardin.webp" alt="Villa Almale con piscina privada y jardín" width="1920" height="1440" loading="lazy" decoding="async"></div>
    <div class="copy">
      <span class="eyebrow" data-theme-number="01">Villa y piscina</span>
      <h2 id="villa-heading">Una casa privada para vivir dentro y fuera.</h2>
      <p>Cinco dormitorios, varios espacios de vida y un jardín íntimo permiten reunirse sin renunciar al descanso. La casa admite hasta 10 huéspedes, con un máximo de seis adultos.</p>
      <ul class="check-list">
        <li>3 dormitorios dobles + 2 dormitorios con camas individuales</li>
        <li>Piscina privada vallada de agua salada</li>
        <li>Jardín de unos 800 m², terrazas y patio andaluz</li>
        <li>Grandes mesas interiores y exteriores para 10</li>
        <li>Cocina equipada, barbacoa de gas y fibra</li>
        <li>Garaje para bicicletas y material de exterior</li>
      </ul>
      <div class="button-row"><a class="button secondary" href="/es/alquiler-vacacional-nuevo-portil/">Descubrir toda la villa →</a></div>
    </div>
  </div>
</section>
'''


def beach_theme_html() -> str:
    return '''
<section class="section es-theme-section es-theme-beach" id="beach" aria-labelledby="beach-heading">
  <div class="shell two-col reverse">
    <div class="copy">
      <span class="eyebrow" data-theme-number="02">Playa y paseos</span>
      <h2 id="beach-heading">La Ría y el Atlántico se disfrutan a pie.</h2>
      <p>La playa de la Ría del Río Piedras está a unos 10–15 minutos andando. El entorno combina orilla, pinares, marismas y caminos tranquilos para pasear sin organizar una excursión.</p>
      <ul class="check-list">
        <li>Baño y paseo por la playa de la Ría</li>
        <li>Puestas de sol junto al Río Piedras</li>
        <li>Recorridos bajo los pinos de Nuevo Portil</li>
        <li>Puerto, terrazas y paseo marítimo de El Rompido</li>
      </ul>
    </div>
    <div class="photo-card theme-photo"><img src="/assets/images/current/plage-ria-rio-piedras.webp" alt="Playa de la Ría del Río Piedras cerca de Villa Almale" width="1440" height="1080" loading="lazy" decoding="async"><div class="photo-copy"><h3>Playa a pie</h3><p>Ría del Río Piedras · Nuevo Portil</p></div></div>
  </div>
</section>
'''


def golf_theme_html() -> str:
    return '''
<section class="section es-theme-section es-theme-golf" id="golf" aria-labelledby="golf-heading">
  <div class="shell">
    <div class="section-heading">
      <div><span class="eyebrow" data-theme-number="03">Golf</span><h2 id="golf-heading">Acceso, campos, reservas y traslados en un solo bloque.</h2></div>
      <p>Villa Almale ofrece únicamente alojamiento. Las salidas, green fees, material y traslados se consultan y pagan directamente a cada proveedor independiente.</p>
    </div>
    <div class="notice-box golf-access" style="margin-bottom:22px"><strong>Golf Nuevo Portil a pie.</strong> El acceso peatonal oficial se alcanza en menos de un minuto desde la entrada residencial.</div>
    <div class="course-grid">
      <article class="course-card"><span class="kicker">Golf Nuevo Portil</span><h3>18 hoyos entre pinares</h3><p>El campo local, par 71, es la opción más cercana y se alcanza andando.</p><p><a data-analytics-event="golf_club_click" href="https://open.teeone.golf/en/golfnuevoportil/disponibilidad" rel="nofollow noopener noreferrer" target="_blank">Reservar una salida →</a><br><a data-analytics-event="golf_club_click" href="https://www.golfnuevoportil.com/rates/" rel="nofollow noopener noreferrer" target="_blank">Ver green fees oficiales →</a></p></article>
      <article class="course-card"><span class="kicker">Golf El Rompido</span><h3>Campos Norte y Sur</h3><p>Dos recorridos diferentes ofrecen 36 hoyos en el paisaje de las marismas del Río Piedras.</p><p><a data-analytics-event="golf_club_click" href="https://www.teetimesbooking.com/club/golf-el-rompido" rel="nofollow noopener noreferrer" target="_blank">Reservar una salida →</a><br><a data-analytics-event="golf_club_click" href="https://www.golfelrompido.es/en/golf-rates/" rel="nofollow noopener noreferrer" target="_blank">Ver green fees oficiales →</a></p></article>
      <article class="course-card"><span class="kicker">Islantilla Golf Resort</span><h3>Tres vueltas de nueve hoyos</h3><p>Una opción de 27 hoyos con varias combinaciones de 18 y academia.</p><p><a data-analytics-event="golf_club_click" href="https://open.teeone.golf/en/islantilla/disponibilidad" rel="nofollow noopener noreferrer" target="_blank">Reservar una salida →</a><br><a data-analytics-event="golf_club_click" href="https://www.islantillagolfresort.com/en/golf" rel="nofollow noopener noreferrer" target="_blank">Campo y tarifas oficiales →</a></p></article>
      <article class="course-card"><span class="kicker">Isla Canela Golf</span><h3>Old Course y Links</h3><p>Dos campos complementarios de 18 hoyos cerca del Guadiana y de Portugal.</p><p><a data-analytics-event="golf_club_click" href="https://www.islacanela.es/en/golf" rel="nofollow noopener noreferrer" target="_blank">Web oficial y reservas →</a></p></article>
    </div>
    <div class="notice-box" style="margin-top:22px"><strong>Traslados de golf independientes.</strong> Un operador local puede presupuestar recorridos a los campos de la zona. <a data-analytics-event="transfer_click" href="https://taximarrompido.com/" rel="nofollow noopener noreferrer" target="_blank">Solicitar presupuesto →</a></div>
  </div>
</section>
'''


def nautical_theme_html() -> str:
    return '''
<section class="section es-theme-section es-theme-nautical" id="nautical" aria-labelledby="nautical-heading">
  <div class="shell">
    <div class="section-heading">
      <div><span class="eyebrow" data-theme-number="04">Náutica</span><h2 id="nautical-heading">Ría, mar y actividades según las condiciones.</h2></div>
      <p>El entorno de Nuevo Portil y El Rompido permite alternar días tranquilos junto al agua con actividades organizadas por operadores locales.</p>
    </div>
    <div class="cards">
      <article class="card"><span class="number">01</span><h3>Paddle y kayak</h3><p>La Ría ofrece un entorno protegido para salir sobre el agua cuando la marea y la meteorología lo permiten.</p></article>
      <article class="card"><span class="number">02</span><h3>Barco y Flecha del Rompido</h3><p>Desde El Rompido se pueden consultar travesías, excursiones y accesos en barco con los prestadores de la zona.</p></article>
      <article class="card"><span class="number">03</span><h3>Condiciones antes de salir</h3><p>Las horas de marea y el estado del mar cambian cada día; consultar la información oficial forma parte de la salida.</p></article>
    </div>
    <div class="notice-box" style="margin-top:22px"><strong>Consulta las condiciones oficiales.</strong><div class="theme-links"><a href="https://www.aemet.es/es/eltiempo/prediccion/municipios/cartaya-id21021" rel="nofollow noopener noreferrer" target="_blank">Previsión AEMET →</a><a href="https://www.puertos.es/servicios/oceanografia" rel="nofollow noopener noreferrer" target="_blank">Mareas y estado del mar →</a></div></div>
  </div>
</section>
'''


def tourism_theme_html() -> str:
    return '''
<section class="section dark es-theme-section es-theme-tourism" id="tourism" aria-labelledby="tourism-heading">
  <div class="shell">
    <div class="section-heading">
      <div><span class="eyebrow" data-theme-number="05">Turismo</span><h2 id="tourism-heading">Pueblos marineros, Andalucía y Portugal.</h2></div>
      <p>Villa Almale es una base única para alternar descubrimientos locales y excursiones de un día sin cambiar de alojamiento.</p>
    </div>
    <div class="timeline">
      <article><time>Muy cerca</time><h3>El Rompido</h3><p>Puerto, terrazas, restaurantes de pescado y paseo frente a la Flecha.</p></article>
      <article><time>Provincia de Huelva</time><h3>Paisajes y patrimonio</h3><p>Marismas, pinares, litoral y lugares relacionados con la historia marítima de la región.</p></article>
      <article><time>Escapada andaluza</time><h3>Sevilla</h3><p>Un día urbano para descubrir monumentos, barrios históricos y gastronomía.</p></article>
      <article><time>Escapada portuguesa</time><h3>Faro y el Algarve</h3><p>Portugal es accesible en coche para variar los paisajes y los ambientes.</p></article>
    </div>
  </div>
</section>
'''


def practical_html() -> str:
    return '''
<section class="section alt" id="practical">
  <div class="shell">
    <div class="section-heading"><div><span class="eyebrow">Preparar la estancia</span><h2>Reserva, llegadas y confort — claramente separados de las actividades.</h2></div></div>
    <div class="rich-grid">
      <article class="info-panel span-6"><span class="kicker">01</span><h3>Solo alojamiento</h3><p>La tarifa cubre la villa según las condiciones del motor de reserva. El transporte y las actividades se reservan por separado.</p></article>
      <article class="info-panel span-6"><span class="kicker">02</span><h3>Llegadas flexibles desde el 12 de septiembre</h3><p>A partir del 12 de septiembre, los días de llegada son flexibles según disponibilidad, para una estancia mínima de siete noches.</p></article>
      <article class="info-panel span-6"><span class="kicker">03</span><h3>Traslados desde el aeropuerto</h3><p>Un operador local independiente puede proponer traslados privados desde Faro o Sevilla.</p><p><a data-analytics-event="transfer_click" href="https://taximarrompido.com/" rel="nofollow noopener noreferrer" target="_blank">Solicitar presupuesto independiente →</a></p></article>
      <article class="info-panel span-6"><span class="kicker">04</span><h3>Confort de temporada</h3><p>El insert de leña calienta el salón. La casa no dispone de calefacción central ni climatización integral; tres aparatos portátiles y ventiladores complementan algunas estancias.</p></article>
    </div>
    <div class="notice-box" style="margin-top:22px"><strong>Proveedores independientes.</strong> Cada operador fija sus precios, disponibilidad, condiciones y formas de pago. La información de esta página no constituye un paquete.</div>
  </div>
</section>
'''


FAQ_ENTRIES = [
    ("¿La piscina es privada?", "Sí. Está reservada a los ocupantes de la villa, vallada y tratada por electrólisis salina. Los niños permanecen bajo la supervisión permanente de un adulto."),
    ("¿A qué distancia está la playa?", "La playa y la Ría del Río Piedras están a unos 10–15 minutos a pie, según el ritmo y el recorrido."),
    ("¿Qué tamaño de grupo funciona mejor?", "La casa puede alojar hasta 10 huéspedes, con un máximo de seis adultos. Esta página está pensada especialmente para estancias de 4 a 6 adultos."),
    ("¿Qué flexibilidad hay a partir del 12 de septiembre?", "A partir del 12 de septiembre, las llegadas son flexibles según disponibilidad, con una estancia mínima de siete noches. El motor de reserva muestra las fechas aplicables."),
    ("¿Se puede utilizar la chimenea?", "Sí. El salón dispone de un insert de leña funcional y la leña se guarda en el garaje. Es un complemento de confort, no una calefacción integral."),
    ("¿Se recomienda coche?", "Sigue siendo la opción más flexible para explorar la costa y organizar excursiones. También se puede reservar por separado un traslado privado desde Faro o Sevilla."),
]


def faq_html() -> str:
    details = "".join(
        f"<details><summary>{question}</summary><p>{answer}</p></details>"
        for question, answer in FAQ_ENTRIES
    )
    return f'''
<section class="section es-theme-faq" id="faq">
  <div class="shell two-col reverse">
    <div class="copy"><span class="eyebrow">Preguntas frecuentes</span><h2>Lo esencial antes de reservar.</h2><div class="faq" style="margin-top:28px">{details}</div></div>
    <div class="photo-card"><img src="/assets/images/current/patio-andalou-table-dressee.webp" alt="Mesa preparada en el patio andaluz de Villa Almale" width="1440" height="1080" loading="lazy" decoding="async"><div class="photo-copy"><h3>Una casa, varias formas de vivir la costa.</h3><p>Villa Almale · Nuevo Portil · VFT/HU/02471</p></div></div>
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
            elif "BreadcrumbList" in types:
                for item in node.get("itemListElement", []):
                    if item.get("position") == 2:
                        item["name"] = "Villa y experiencias en la Costa de la Luz"
            elif "FAQPage" in types:
                node["mainEntity"] = [
                    {
                        "@type": "Question",
                        "name": question,
                        "acceptedAnswer": {"@type": "Answer", "text": answer},
                    }
                    for question, answer in FAQ_ENTRIES
                ]
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
        f'''<a href="#villa">Villa y piscina</a><a href="#beach">Playa</a><a href="#golf">Golf</a><a href="#nautical">Náutica</a><a href="#tourism">Turismo</a><a class="nav-cta" data-analytics-event="booking_click" href="{BOOKING}">Ver fechas</a>''',
        "html.parser",
    )
    for child in list(nav_fragment.contents):
        nav.append(child)

    footer = soup.select_one("footer.footer")
    footer_intro = footer.select_one(".footer-grid > div > p") if footer else None
    footer_links = footer.select_one(".footer-links") if footer else None
    if footer_intro:
        footer_intro.string = (
            "Una villa privada de cinco dormitorios en Nuevo Portil, entre piscina, playa y experiencias atlánticas."
        )
    if footer_links:
        footer_links.clear()
        footer_nav = BeautifulSoup(
            '''<a href="#villa">Villa y piscina</a><a href="#beach">Playa y paseos</a><a href="#golf">Golf</a><a href="#nautical">Náutica</a><a href="#tourism">Turismo</a>''',
            "html.parser",
        )
        for child in list(footer_nav.contents):
            footer_links.append(child)

    hero = soup.select_one("section.hero-season")
    hero_content = hero.select_one(".hero-content") if hero else None
    if hero is None or hero_content is None:
        raise RuntimeError("Spanish campaign hero missing")
    hero_content.select_one(".eyebrow").string = "Septiembre y octubre en la Costa de la Luz"
    hero_content.select_one("h1").string = "Una villa privada para disfrutar la Costa de la Luz a tu ritmo."
    hero_content.select_one("p.lead").string = (
        "Cinco dormitorios para grupos de 4 a 6 adultos, piscina privada, jardín y playa a pie, "
        "con cada experiencia reunida en un bloque claro."
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
<div class="hero-fact"><strong>10–15 min</strong><span>playa de la Ría a pie</span></div>
<div class="hero-fact"><strong>Privada</strong><span>piscina · jardín</span></div>
''',
        "html.parser",
    )
    for child in list(facts.contents):
        hero_facts.append(child)

    stat_strip = soup.select_one("section.stat-strip")
    if stat_strip:
        stat_strip.decompose()
    hero.insert_after(fragment(gallery_html()))

    final_cta_section = soup.select_one("section.section-sm")
    if final_cta_section is None:
        raise RuntimeError("Spanish direct-booking section missing")

    legacy_faq = soup.select_one(".faq")
    legacy_faq_section = legacy_faq.find_parent("section") if legacy_faq else None
    if legacy_faq_section and legacy_faq_section is not final_cta_section:
        legacy_faq_section.decompose()

    for selector in (
        "section#why",
        "section#house",
        "section#villa",
        "section#beach",
        "section#golf",
        "section#nautical",
        "section#tourism",
        "section#practical",
        "section#faq",
    ):
        for node in soup.select(selector):
            node.decompose()
    for node in soup.select("section.dark"):
        if node is not final_cta_section:
            node.decompose()

    for section_html in (
        villa_theme_html(),
        beach_theme_html(),
        golf_theme_html(),
        nautical_theme_html(),
        tourism_theme_html(),
        practical_html(),
        faq_html(),
    ):
        final_cta_section.insert_before(fragment(section_html))

    banner = soup.select_one("section.section-sm .banner")
    if banner:
        banner.select_one(".eyebrow").string = "Reserva directa"
        banner.select_one("h2").string = "Una casa, cinco formas de vivir la Costa de la Luz."
        banner.select_one("p").string = (
            "Elige tus fechas y prepara cada experiencia desde una misma base privada. "
            "Consulta disponibilidad y precio completo mediante OwnerRez."
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
        global_offer["data-offer-version"] = "september-october-2026-es-v2"
        global_offer["aria-label"] = "Disponibilidad en septiembre y octubre desde 2.226 euros"
        inner = global_offer.select_one(".site-autumn-offer__inner")
        if inner is None:
            raise RuntimeError("Global promotional banner inner container missing")
        inner.clear()
        promo = fragment(
            f'''<span class="site-autumn-offer__text es-promo-copy"><span class="es-promo-main">Disponibilidad en septiembre y octubre</span><span class="es-promo-detail">Desde 2.226 € / 7 noches · villa completa · llegadas flexibles desde el 12/09 <a class="site-autumn-offer__cta" data-analytics-event="special_offer_click" data-offer-id="september-october-2026-es" href="{BOOKING}">Ver precios →</a></span></span>'''
        )
        inner.append(promo)
        global_cta = global_offer.select_one(".site-autumn-offer__cta")
        global_cta.string = "Ver precios →"
        global_cta["href"] = BOOKING
        global_cta["data-analytics-event"] = "special_offer_click"
        global_cta["data-offer-id"] = "september-october-2026-es"
        global_script = soup.find(id="villa-almale-v7-4-global-actions-script")
        if global_script and global_script.string:
            for old_key in (
                "villa-almale-autumn-offer-dismissed-v2",
                "villa-almale-spanish-september-offer-v1",
            ):
                global_script.string = global_script.string.replace(
                    old_key,
                    "villa-almale-spanish-september-offer-v2",
                )

    update_json_ld(soup)

    output = str(soup)
    if not output.lstrip().lower().startswith("<!doctype"):
        output = "<!DOCTYPE html>\n" + output
    path.write_text(output, encoding="utf-8")

    check = BeautifulSoup(output, "html.parser")
    assert len(check.find_all("h1")) == 1
    assert check.find("h1").get_text(" ", strip=True) == "Una villa privada para disfrutar la Costa de la Luz a tu ritmo."
    assert len(check.select(".es-september-offer")) == 0
    assert len(check.select(".es-photo-grid img")) == 6
    assert len(check.select(".es-campaign-hero-proof span")) == 3
    assert len(check.select(".es-direct-trust")) == 1
    assert len(check.select(".hero-facts .hero-fact")) == 4
    assert len(check.select(".es-theme-section")) == 5
    for theme_id in ("villa", "beach", "golf", "nautical", "tourism"):
        assert check.select_one(f"section#{theme_id}.es-theme-section")
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
    promo = check.select_one("[data-site-global-offer] .es-promo-copy")
    assert promo
    assert promo.select_one(".es-promo-main").get_text(" ", strip=True) == "Disponibilidad en septiembre y octubre"
    assert promo.select_one(".es-promo-detail")
    assert promo.select_one(".site-autumn-offer__cta").get("href") == BOOKING
    assert 'font-family:Georgia,"Times New Roman",serif' in CSS
    assert "font-family:Arial,Helvetica,sans-serif" in CSS
    section_order = [output.index(f'id="{theme_id}"') for theme_id in ("villa", "beach", "golf", "nautical", "tourism")]
    assert section_order == sorted(section_order)
    thematic_copy = BeautifulSoup(str(check.body), "html.parser")
    for selector in ("header", "footer", "section#golf", "script", "style"):
        for node in thematic_copy.select(selector):
            node.decompose()
    assert "golf" not in thematic_copy.get_text(" ", strip=True).lower()
    for block in check.find_all("script", attrs={"type": "application/ld+json"}):
        payload = json.loads(block.string or block.get_text())
        assert all(
            not isinstance(node, dict) or node.get("@id") != OFFER_ID
            for node in payload.get("@graph", [])
        )
        for node in payload.get("@graph", []):
            if isinstance(node, dict) and node.get("@type") == "FAQPage":
                assert [item["name"] for item in node["mainEntity"]] == [question for question, _ in FAQ_ENTRIES]


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

    print("Villa Almale V7.6 Spanish themed landing page, two-line banner and multilingual logo routes validated.")


if __name__ == "__main__":
    main()
