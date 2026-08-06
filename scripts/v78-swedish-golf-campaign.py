#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup


DATE = "2026-08-06"
SITE = "https://villanuevoportil.com"
SV_URL = f"{SITE}/off-season/sv/"
BOOKING = "/en/reservation.html"
WHATSAPP_NUMBER = "33687174067"
WHATSAPP_MESSAGE = (
    "Hej, jag är intresserad av Villa Almale i september eller oktober 2026. "
    "Vilka datum och priser finns tillgängliga för 4–6 vuxna?"
)
WHATSAPP_URL = f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(WHATSAPP_MESSAGE, safe='')}"

TITLE = "Golfvilla vid Atlanten i september och oktober | Villa Almale"
DESCRIPTION = (
    "Hyr hela Villa Almale i Nuevo Portil för en golfvecka med 4–6 vuxna. "
    "Fem sovrum, privat pool, strand och Golf Nuevo Portil på gångavstånd. "
    "Från 2 226 € för 7 nätter."
)

LANGUAGE_PAGES = {
    "off-season/index.html": ("en", "English"),
    "off-season/fr/index.html": ("fr", "Français"),
    "off-season/es/index.html": ("es", "Español"),
}

ALTERNATES = (
    ("en", f"{SITE}/off-season/"),
    ("fr", f"{SITE}/off-season/fr/"),
    ("es", f"{SITE}/off-season/es/"),
    ("sv", SV_URL),
    ("x-default", f"{SITE}/off-season/"),
)

STYLE_ID = "villa-almale-v78-swedish-golf"
CSS = r'''
/* Villa Almale V7.8 — Swedish golf campaign landing page */
html[lang="sv"] .hero-content h1{max-width:19ch}
html[lang="sv"] .hero-content .lead{max-width:58rem}
html[lang="sv"] .site-autumn-offer__text{max-width:64rem}
html[lang="sv"] .es-gallery-intro h2{max-width:24ch}
html[lang="sv"] .course-card h3{min-height:2.25em}
@media(max-width:720px){
  html[lang="sv"] .hero-content h1{max-width:16ch}
  html[lang="sv"] .course-card h3{min-height:0}
}
'''


def parse(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def fragment(html: str):
    soup = parse(html)
    nodes = [node for node in soup.contents if getattr(node, "name", None)]
    if len(nodes) != 1:
        raise RuntimeError("Expected one HTML fragment root")
    return nodes[0]


def write_html(path: Path, soup: BeautifulSoup) -> None:
    output = str(soup)
    if not output.lstrip().lower().startswith("<!doctype"):
        output = "<!DOCTYPE html>\n" + output
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding="utf-8")


def set_meta(
    soup: BeautifulSoup,
    *,
    value: str,
    name: str | None = None,
    prop: str | None = None,
) -> None:
    attrs = {"name": name} if name else {"property": prop}
    node = soup.find("meta", attrs=attrs)
    if node is None:
        node = soup.new_tag("meta", attrs=attrs)
        soup.head.append(node)
    node["content"] = value


def set_alternates(soup: BeautifulSoup) -> None:
    for node in soup.find_all("link", rel="alternate"):
        node.decompose()
    canonical = soup.find("link", rel="canonical")
    anchor = canonical if canonical is not None else soup.head.find("meta", attrs={"name": "description"})
    for lang, href in reversed(ALTERNATES):
        node = soup.new_tag("link", rel="alternate", hreflang=lang, href=href)
        if anchor is not None:
            anchor.insert_after(node)
        else:
            soup.head.append(node)


def ensure_swedish_language_link(soup: BeautifulSoup) -> None:
    panel = soup.select_one(".lang-menu .lang-panel")
    if panel is None:
        raise RuntimeError("Language menu is missing")
    for node in panel.select('a[hreflang="sv"], a[href="/off-season/sv/"]'):
        node.decompose()
    link = soup.new_tag("a", href="/off-season/sv/", hreflang="sv", lang="sv")
    link.string = "Svenska"
    panel.append(link)


def add_swedish_discovery(path: Path) -> None:
    soup = parse(path.read_text(encoding="utf-8"))
    if soup.head is None:
        raise RuntimeError(f"Missing head in {path}")
    set_alternates(soup)
    ensure_swedish_language_link(soup)
    write_html(path, soup)


def build_main() -> str:
    return f'''
<main>
  <section class="hero hero-season">
    <div class="shell"><div class="hero-content">
      <span class="eyebrow">Golf vid Atlanten · september och oktober 2026</span>
      <h1>En hel villa för golfveckan på Costa de la Luz.</h1>
      <p class="lead">Samla 4–6 vuxna i en privat villa med fem sovrum, pool och strand i närheten – och Golf Nuevo Portil på gångavstånd.</p>
      <div class="hero-actions">
        <a class="button primary" data-analytics-event="booking_click" href="{BOOKING}">Se lediga datum och pris →</a>
        <a class="button outline-light" data-analytics-event="whatsapp_click" href="{WHATSAPP_URL}" rel="noopener noreferrer" target="_blank">Fråga oss på WhatsApp</a>
      </div>
      <div class="es-campaign-hero-proof" aria-label="Trygg direktbokning">
        <span>Vrbo 9,0/10 · 13 omdömen</span>
        <span>Registrerad semesterbostad · VFT/HU/02471</span>
        <span>Säker direktbokning · OwnerRez + Stripe</span>
      </div>
    </div></div>
    <div class="hero-facts">
      <div class="hero-fact"><strong>5</strong><span>sovrum</span></div>
      <div class="hero-fact"><strong>4–6</strong><span>vuxna · idealisk grupp</span></div>
      <div class="hero-fact"><strong>&lt; 1 min</strong><span>Golf Nuevo Portil till fots</span></div>
      <div class="hero-fact"><strong>Privat</strong><span>pool · trädgård</span></div>
    </div>
  </section>

  <section class="es-campaign-gallery" aria-labelledby="villa-real-heading">
    <div class="shell">
      <div class="es-gallery-intro">
        <div><span class="eyebrow">Det här är Villa Almale</span><h2 id="villa-real-heading">Ett eget hus för gruppen – inte flera hotellrum.</h2></div>
        <p>Gemensamma ytor och fem sovrum för 4–6 vuxna som vill spela golf, laga mat, koppla av och uppleva Costa de la Luz tillsammans.</p>
      </div>
      <div class="es-photo-grid">
        <figure><img src="/assets/images/current/hero-villa-piscine-jardin.webp" alt="Villa Almale med privat pool och trädgård" width="1920" height="1440" loading="lazy" decoding="async"></figure>
        <figure><img src="/assets/images/current/piscine-privee.webp" alt="Villa Almales inhägnade privata pool" width="1440" height="1080" loading="lazy" decoding="async"></figure>
        <figure><img src="/assets/images/current/patio-andalou-table-dressee.webp" alt="Dukat bord på den andalusiska uteplatsen" width="1440" height="1080" loading="lazy" decoding="async"></figure>
        <figure><img src="/assets/images/current/salon-salle-a-manger.webp" alt="Vardagsrum och matsal i Villa Almale" width="1440" height="1080" loading="lazy" decoding="async"></figure>
        <figure><img src="/assets/images/current/suite-principale.webp" alt="Villa Almales största sovrum" width="1440" height="1080" loading="lazy" decoding="async"></figure>
        <figure><img src="/assets/images/current/chambre-double-bleue.webp" alt="Blått dubbelrum i Villa Almale" width="1440" height="1080" loading="lazy" decoding="async"></figure>
      </div>
    </div>
  </section>

  <section class="section es-theme-section es-theme-villa" id="villa" aria-labelledby="villa-heading">
    <div class="shell two-col">
      <div class="house-photo theme-photo"><img src="/assets/images/current/hero-villa-piscine-jardin.webp" alt="Villa Almale med privat pool och trädgård" width="1920" height="1440" loading="lazy" decoding="async"></div>
      <div class="copy">
        <span class="eyebrow" data-theme-number="01">Villa och pool</span>
        <h2 id="villa-heading">Ett privat hus för dagarna mellan rundorna.</h2>
        <p>Fem sovrum, generösa sällskapsytor och en skyddad trädgård ger plats för både gemenskap och vila. Huset tar upp till 10 gäster, med högst sex vuxna.</p>
        <ul class="check-list">
          <li>3 dubbelrum + 2 sovrum med enkelsängar</li>
          <li>Inhägnad privat saltvattenpool</li>
          <li>Cirka 800 m² trädgård, terrasser och andalusisk patio</li>
          <li>Stora matbord inne och ute för 10</li>
          <li>Utrustat kök, gasolgrill och fiberinternet</li>
          <li>Garage för golfbagar, vagnar och cyklar</li>
        </ul>
        <div class="button-row"><a class="button secondary" href="/en/holiday-villa-nuevo-portil/">Se hela villan →</a></div>
      </div>
    </div>
  </section>

  <section class="section es-theme-section es-theme-beach" id="beach" aria-labelledby="beach-heading">
    <div class="shell two-col reverse">
      <div class="copy">
        <span class="eyebrow" data-theme-number="02">Strand och promenader</span>
        <h2 id="beach-heading">Ría del Río Piedras och Atlanten inom promenadavstånd.</h2>
        <p>Stranden vid Ría del Río Piedras ligger omkring 10–15 minuter till fots. Här möts vatten, pinjeskog, våtmarker och lugna stigar – enkelt att njuta av utan planering.</p>
        <ul class="check-list">
          <li>Bad och promenader längs Ría-stranden</li>
          <li>Solnedgångar vid Río Piedras</li>
          <li>Stigar bland pinjeträden i Nuevo Portil</li>
          <li>Hamn, restauranger och strandpromenad i El Rompido</li>
        </ul>
      </div>
      <div class="photo-card theme-photo"><img src="/assets/images/current/plage-ria-rio-piedras.webp" alt="Stranden vid Ría del Río Piedras nära Villa Almale" width="900" height="900" loading="lazy" decoding="async"><div class="photo-copy"><h3>Stranden på gångavstånd</h3><p>Ría del Río Piedras · Nuevo Portil</p></div></div>
    </div>
  </section>

  <section class="es-climate-section" id="klimat-september-oktober" aria-labelledby="climate-heading">
    <div class="shell es-climate-layout">
      <div class="es-climate-copy">
        <span class="eyebrow">Klimatet i september och oktober</span>
        <h2 id="climate-heading">Långa, ljusa dagar för golf och livet utomhus.</h2>
        <p>Klimatnormalerna för närliggande Huelva–Ronda Este visar fortfarande varma dagar och milda kvällar – fint för golf, strand, promenader och middagar på terrassen.</p>
      </div>
      <div class="es-climate-grid" aria-label="Genomsnittliga temperaturer och soltimmar">
        <article class="es-climate-card"><span class="month">September</span><strong>29,4 / 17,3 °C</strong><span>genomsnittlig daglig max/min</span></article>
        <article class="es-climate-card"><span class="month">September</span><strong>268 soltimmar</strong><span>per månad · cirka 8,9 timmar per dag</span></article>
        <article class="es-climate-card"><span class="month">Oktober</span><strong>24,9 / 14,1 °C</strong><span>genomsnittlig daglig max/min</span></article>
        <article class="es-climate-card"><span class="month">Oktober</span><strong>211 soltimmar</strong><span>per månad · cirka 6,8 timmar per dag</span></article>
        <p class="es-climate-source">Källa: <a href="https://www.aemet.es/es/serviciosclimaticos/datosclimatologicos/valoresclimatologicos?l=4642E" target="_blank" rel="noopener noreferrer">AEMETs klimatnormaler · Huelva, Ronda Este (station 4642E)</a>. Genomsnittliga referensvärden; dagsvädret i Nuevo Portil kan variera.</p>
      </div>
    </div>
  </section>

  <section class="section es-theme-section es-theme-golf" id="golf" aria-labelledby="golf-heading">
    <div class="shell">
      <div class="section-heading">
        <div><span class="eyebrow" data-theme-number="03">Golf</span><h2 id="golf-heading">En bana till fots och fler rundor längs kusten.</h2></div>
        <p>Golf Nuevo Portil ligger på gångavstånd från Villa Almale. Med bil når gruppen flera andra banor för att variera spel och landskap under veckan.</p>
      </div>
      <div class="notice-box golf-access" style="margin-bottom:22px"><strong>Golf Nuevo Portil till fots.</strong> Den officiella gångvägen nås på mindre än en minut från bostadsområdets entré.</div>
      <div class="course-grid">
        <article class="course-card"><span class="kicker">Golf Nuevo Portil</span><h3>18 hål bland pinjeträd</h3><p>Den lokala par 71-banan är närmast och nås till fots.</p><p><a data-analytics-event="golf_club_click" href="https://open.teeone.golf/en/golfnuevoportil/disponibilidad" rel="nofollow noopener noreferrer" target="_blank">Boka starttid →</a><br><a data-analytics-event="golf_club_click" href="https://www.golfnuevoportil.com/rates/" rel="nofollow noopener noreferrer" target="_blank">Se officiella greenfeepriser →</a></p></article>
        <article class="course-card"><span class="kicker">Golf El Rompido</span><h3>Norra och södra banan</h3><p>Två olika 18-hålsbanor ger 36 hål i landskapet runt Río Piedras våtmarker.</p><p><a data-analytics-event="golf_club_click" href="https://www.teetimesbooking.com/club/golf-el-rompido" rel="nofollow noopener noreferrer" target="_blank">Boka starttid →</a><br><a data-analytics-event="golf_club_click" href="https://www.golfelrompido.es/en/golf-rates/" rel="nofollow noopener noreferrer" target="_blank">Se officiella greenfeepriser →</a></p></article>
        <article class="course-card"><span class="kicker">Islantilla Golf Resort</span><h3>Tre 9-hålsslingor</h3><p>En 27-hålsanläggning med flera kombinationer av 18 hål och golfakademi.</p><p><a data-analytics-event="golf_club_click" href="https://open.teeone.golf/en/islantilla/disponibilidad" rel="nofollow noopener noreferrer" target="_blank">Boka starttid →</a><br><a data-analytics-event="golf_club_click" href="https://www.islantillagolfresort.com/en/golf" rel="nofollow noopener noreferrer" target="_blank">Bana och officiella priser →</a></p></article>
        <article class="course-card"><span class="kicker">Isla Canela Golf</span><h3>Old Course och Links</h3><p>Två kompletterande 18-hålsbanor nära floden Guadiana och Portugal.</p><p><a data-analytics-event="golf_club_click" href="https://www.islacanela.es/en/golf" rel="nofollow noopener noreferrer" target="_blank">Officiell webbplats och bokning →</a></p></article>
      </div>
      <div class="notice-box" style="margin-top:22px"><strong>Transport till banorna.</strong> En lokal operatör kan ordna körningar som passar gruppens starttider. <a data-analytics-event="transfer_click" href="https://taximarrompido.com/" rel="nofollow noopener noreferrer" target="_blank">Be om offert →</a></div>
    </div>
  </section>

  <section class="section es-theme-section es-theme-nautical" id="nautical" aria-labelledby="nautical-heading">
    <div class="shell">
      <div class="section-heading">
        <div><span class="eyebrow" data-theme-number="04">På vattnet</span><h2 id="nautical-heading">Ría, Atlanten och Flecha del Rompido från vattnet.</h2></div>
        <p>Runt Nuevo Portil och El Rompido kan lugna dagar vid vattnet varvas med aktiviteter hos lokala arrangörer.</p>
      </div>
      <figure class="photo-card theme-photo es-nautical-photo" id="el-rompido-nautica"><img src="/assets/images/current/el-rompido-marina.webp" alt="Hamnen och restaurangerna i El Rompido vid Ría del Río Piedras" width="900" height="900" loading="lazy" decoding="async"><figcaption class="photo-copy"><h3>El Rompido vid vattnet</h3><p>Hamn, restauranger och båtturer mot Flecha del Rompido</p></figcaption></figure>
      <div class="cards">
        <article class="card"><span class="number">01</span><h3>SUP och kajak</h3><p>Ría erbjuder skyddat vatten och öppna vyer för den som vill upptäcka kusten med SUP eller kajak.</p></article>
        <article class="card"><span class="number">02</span><h3>Båt och Flecha del Rompido</h3><p>Från El Rompido går båtturer och utflykter mot Flecha, med flera sätt att nå dess stränder.</p></article>
        <article class="card"><span class="number">03</span><h3>Välj rätt tid på dagen</h3><p>Tidvattnet förändrar landskapet i Ría. Kontrollera tiderna för att välja dagens bästa stund på vattnet.</p></article>
      </div>
      <div class="notice-box" style="margin-top:22px"><strong>Planera efter väder och tidvatten.</strong><div class="theme-links"><a href="https://www.aemet.es/es/eltiempo/prediccion/municipios/cartaya-id21021" rel="nofollow noopener noreferrer" target="_blank">Väderprognos från AEMET →</a><a href="https://www.puertos.es/servicios/oceanografia" rel="nofollow noopener noreferrer" target="_blank">Tidvatten och havsläge →</a></div></div>
    </div>
  </section>

  <section class="section dark es-theme-section es-theme-tourism" id="tourism" aria-labelledby="tourism-heading">
    <div class="shell">
      <div class="section-heading">
        <div><span class="eyebrow" data-theme-number="05">Utflykter</span><h2 id="tourism-heading">Fiskelägen, Andalusien och Portugal.</h2></div>
        <p>Villa Almale är en bekväm bas för lokala upptäckter och dagsutflykter utan att byta boende.</p>
      </div>
      <div class="timeline">
        <article><time>Mycket nära</time><h3>El Rompido</h3><p>Hamn, terrasser, fiskrestauranger och promenadstråk med utsikt mot Flecha.</p></article>
        <article><time>Huelvaprovinsen</time><h3>Landskap och kulturarv</h3><p>Våtmarker, pinjeskogar, kust och platser som berättar om regionens sjöfartshistoria.</p></article>
        <article><time>En dag i Andalusien</time><h3>Sevilla</h3><p>Monument, historiska kvarter och gastronomi under en omväxlande stadsdag.</p></article>
        <article><time>En dag i Portugal</time><h3>Faro och Algarve</h3><p>Portugal nås med bil när gruppen vill byta landskap och atmosfär.</p></article>
      </div>
    </div>
  </section>

  <section class="section alt" id="practical">
    <div class="shell">
      <div class="section-heading"><div><span class="eyebrow">Inför resan</span><h2>En golfvecka som är enkel att organisera.</h2></div></div>
      <div class="rich-grid">
        <article class="info-panel span-6"><span class="kicker">01</span><h3>Villan, i ert tempo</h3><p>Bokningen omfattar hela villan. Gruppen väljer själv transfer, golf, aktiviteter och utflykter efter sitt program.</p></article>
        <article class="info-panel span-6"><span class="kicker">02</span><h3>Flexibel ankomst från 12 september</h3><p>Från 12 september är ankomstdagarna flexibla beroende på tillgänglighet. Minsta vistelse är från fyra nätter, beroende på vecka.</p></article>
        <article class="info-panel span-6"><span class="kicker">03</span><h3>Transfer från flygplatsen</h3><p>Privat transfer från Faro eller Sevilla kan bokas för en smidig resa direkt till villan.</p><p><a data-analytics-event="transfer_click" href="https://taximarrompido.com/" rel="nofollow noopener noreferrer" target="_blank">Be om offert →</a></p></article>
        <article class="info-panel span-6"><span class="kicker">04</span><h3>Komfort under hösten</h3><p>Under svalare kvällar ger vedspisen värme i vardagsrummet. Huset har också tre portabla enheter och fläktar i flera rum.</p></article>
      </div>
      <div class="notice-box" style="margin-top:22px"><strong>Välj till efter gruppens plan.</strong> Golf, transfer och upplevelser bokas direkt hos respektive operatör, så att gruppen kan sätta ihop sin egen vecka.</div>
    </div>
  </section>

  <section class="section es-theme-faq" id="faq">
    <div class="shell two-col reverse">
      <div class="copy"><span class="eyebrow">Vanliga frågor</span><h2>Det viktigaste före bokning.</h2><div class="faq" style="margin-top:28px">
        <details><summary>Är poolen privat?</summary><p>Ja. Den är endast för villans gäster, inhägnad och renas med saltelektrolys. Barn ska alltid stå under en vuxens uppsikt.</p></details>
        <details><summary>Hur långt är det till stranden?</summary><p>Stranden och Ría del Río Piedras ligger omkring 10–15 minuter till fots, beroende på tempo och vägval.</p></details>
        <details><summary>Vilken gruppstorlek passar bäst?</summary><p>Huset tar upp till 10 gäster, med högst sex vuxna. Den här vistelsen är särskilt utformad för grupper på 4–6 vuxna.</p></details>
        <details><summary>Hur flexibel är ankomsten från 12 september?</summary><p>Från 12 september är ankomsten flexibel beroende på tillgänglighet. Minsta vistelse är från fyra nätter, beroende på vecka. Bokningsmotorn visar vilka datum som gäller.</p></details>
        <details><summary>Hur värms huset under svalare kvällar?</summary><p>Vardagsrummet har en fungerande vedspis och ved förvaras i garaget. Tre portabla enheter ger extra komfort i vissa rum; huset saknar centralvärme.</p></details>
        <details><summary>Rekommenderas hyrbil?</summary><p>Bil ger störst frihet för golfbanor och utflykter. Privat transfer från Faro eller Sevilla kan också bokas separat.</p></details>
      </div></div>
      <div class="photo-card"><img src="/assets/images/current/patio-andalou-table-dressee.webp" alt="Dukat bord på Villa Almales andalusiska uteplats" width="1440" height="1080" loading="lazy" decoding="async"><div class="photo-copy"><h3>Ett hus, många sätt att uppleva kusten.</h3><p>Villa Almale · Nuevo Portil · VFT/HU/02471</p></div></div>
    </div>
  </section>

  <section class="section-sm"><div class="shell"><div class="banner"><div>
    <span class="eyebrow">Boka direkt</span>
    <h2>Samla gruppen för en golfvecka vid Atlanten.</h2>
    <p>Se lediga datum och totalpris i OwnerRez. Välj sedan banor och utflykter i den takt som passar er.</p>
    <div class="es-direct-trust" aria-label="Information om direktbokning"><span>Tillgänglighet i realtid</span><span>Säker betalning med Stripe</span><span>VFT/HU/02471</span><span>Vrbo 9,0/10 · 13 omdömen</span></div>
  </div><a class="button light" data-analytics-event="booking_click" href="{BOOKING}">Se lediga datum och pris →</a></div></div></section>
</main>
'''


def build_footer() -> str:
    return f'''
<footer class="footer"><div class="shell">
  <div class="footer-grid">
    <div><h3>Villa Almale</h3><p>En privat villa med fem sovrum i Nuevo Portil, nära golf, pool, strand och Atlantens landskap.</p><p>contact@villanuevoportil.com · VFT/HU/02471</p></div>
    <div><strong>Upptäck</strong><div class="footer-links"><a href="#villa">Villa och pool</a><a href="#beach">Strand och promenader</a><a href="#golf">Golf</a><a href="#nautical">På vattnet</a><a href="#tourism">Utflykter</a></div></div>
    <div><strong>Planera</strong><div class="footer-links"><a data-analytics-event="booking_click" href="{BOOKING}">Se lediga datum</a><a href="/legal.html">Juridisk information</a><a href="/privacy.html">Integritet</a><a href="/cookies.html">Cookies</a><a href="/booking-terms.html">Bokningsvillkor</a></div></div>
  </div>
  <div class="footer-bottom"><span>© <span data-current-year></span> Villa Almale</span><span>Nuevo Portil · Costa de la Luz · Spanien</span></div>
</div></footer>
'''


def update_json_ld(soup: BeautifulSoup) -> None:
    faq = [
        ("Är poolen privat?", "Ja. Den är endast för villans gäster, inhägnad och renas med saltelektrolys. Barn ska alltid stå under en vuxens uppsikt."),
        ("Hur långt är det till stranden?", "Stranden och Ría del Río Piedras ligger omkring 10–15 minuter till fots, beroende på tempo och vägval."),
        ("Vilken gruppstorlek passar bäst?", "Huset tar upp till 10 gäster, med högst sex vuxna. Den här vistelsen är särskilt utformad för grupper på 4–6 vuxna."),
        ("Hur flexibel är ankomsten från 12 september?", "Från 12 september är ankomsten flexibel beroende på tillgänglighet. Minsta vistelse är från fyra nätter, beroende på vecka. Bokningsmotorn visar vilka datum som gäller."),
        ("Hur värms huset under svalare kvällar?", "Vardagsrummet har en fungerande vedspis och ved förvaras i garaget. Tre portabla enheter ger extra komfort i vissa rum; huset saknar centralvärme."),
        ("Rekommenderas hyrbil?", "Bil ger störst frihet för golfbanor och utflykter. Privat transfer från Faro eller Sevilla kan också bokas separat."),
    ]
    for block in soup.find_all("script", attrs={"type": "application/ld+json"}):
        payload = json.loads(block.string or block.get_text())
        graph = payload.get("@graph") if isinstance(payload, dict) else None
        if not isinstance(graph, list):
            continue
        for node in graph:
            if not isinstance(node, dict):
                continue
            typ = node.get("@type")
            types = {typ} if isinstance(typ, str) else set(typ or [])
            if "WebSite" in types:
                node["inLanguage"] = ["fr-FR", "en-GB", "es-ES", "sv-SE"]
            elif "Accommodation" in types:
                node["description"] = DESCRIPTION
            elif "ImageObject" in types:
                node["@id"] = f"{SV_URL}#primaryimage"
                node["caption"] = "Villa Almale med privat pool och trädgård i Nuevo Portil"
            elif "WebPage" in types:
                node.update({
                    "@id": f"{SV_URL}#webpage",
                    "url": SV_URL,
                    "name": TITLE,
                    "description": DESCRIPTION,
                    "inLanguage": "sv-SE",
                    "primaryImageOfPage": {"@id": f"{SV_URL}#primaryimage"},
                    "dateModified": DATE,
                    "breadcrumb": {"@id": f"{SV_URL}#breadcrumb"},
                })
            elif "BreadcrumbList" in types:
                node["@id"] = f"{SV_URL}#breadcrumb"
                node["itemListElement"] = [
                    {"@type": "ListItem", "position": 1, "name": "Villa Almale", "item": f"{SITE}/en/"},
                    {"@type": "ListItem", "position": 2, "name": "Golfvilla vid Atlanten", "item": SV_URL},
                ]
            elif "FAQPage" in types:
                node["@id"] = f"{SV_URL}#faq"
                node["mainEntity"] = [
                    {"@type": "Question", "name": question, "acceptedAnswer": {"@type": "Answer", "text": answer}}
                    for question, answer in faq
                ]
        block.string = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def transform_spanish_to_swedish(source: Path, destination: Path) -> None:
    soup = parse(source.read_text(encoding="utf-8"))
    if soup.head is None or soup.body is None or soup.main is None or soup.footer is None:
        raise RuntimeError("Source landing page is incomplete")

    soup.html["lang"] = "sv"
    soup.title.string = TITLE
    set_meta(soup, name="description", value=DESCRIPTION)
    set_meta(soup, name="twitter:title", value=TITLE)
    set_meta(soup, name="twitter:description", value=DESCRIPTION)
    set_meta(soup, name="twitter:image:alt", value="Villa Almale med privat pool och trädgård i Nuevo Portil")
    set_meta(soup, prop="og:locale", value="sv_SE")
    set_meta(soup, prop="og:title", value=TITLE)
    set_meta(soup, prop="og:description", value=DESCRIPTION)
    set_meta(soup, prop="og:url", value=SV_URL)
    set_meta(soup, prop="og:image:alt", value="Villa Almale med privat pool och trädgård i Nuevo Portil")

    for node in soup.find_all("meta", attrs={"property": "og:locale:alternate"}):
        node.decompose()
    for locale in reversed(("en_GB", "fr_FR", "es_ES")):
        node = soup.new_tag("meta", attrs={"property": "og:locale:alternate", "content": locale})
        soup.head.append(node)

    canonical = soup.find("link", rel="canonical")
    if canonical is None:
        canonical = soup.new_tag("link", rel="canonical")
        soup.head.append(canonical)
    canonical["href"] = SV_URL
    set_alternates(soup)

    old_style = soup.find(id=STYLE_ID)
    if old_style:
        old_style.decompose()
    style = soup.new_tag("style", id=STYLE_ID)
    style.string = CSS
    soup.head.append(style)

    brand = soup.select_one("header.site-header a.brand")
    nav = soup.select_one("header.site-header nav.nav-links")
    lang_button = soup.select_one(".lang-menu .lang-button")
    menu_button = soup.select_one("header.site-header .menu-button")
    if None in (brand, nav, lang_button, menu_button):
        raise RuntimeError("Source header is incomplete")
    brand["href"] = "/en/"
    brand.attrs.pop("target", None)
    brand.attrs.pop("rel", None)
    menu_button.string = "Meny"
    menu_button["aria-label"] = "Meny"
    nav["aria-label"] = "Huvudnavigering"
    nav.clear()
    nav_fragment = parse(
        f'<a href="#villa">Villan</a><a href="#beach">Stranden</a><a href="#golf">Golf</a>'
        f'<a href="#nautical">På vattnet</a><a href="#tourism">Utflykter</a>'
        f'<a class="nav-cta" data-analytics-event="booking_click" href="{BOOKING}">Se lediga datum</a>'
    )
    for child in list(nav_fragment.contents):
        nav.append(child)
    lang_button.string = "SV ▾"
    ensure_swedish_language_link(soup)
    for link in soup.select(".lang-menu .lang-panel a"):
        link.attrs.pop("target", None)
        link.attrs.pop("rel", None)

    offer = soup.select_one("[data-site-global-offer]")
    if offer is None:
        raise RuntimeError("Global offer banner is missing")
    offer["aria-label"] = "Lediga veckor i september och oktober från 2 226 euro"
    offer["data-offer-version"] = "september-october-2026-sv-v1"
    offer["data-expiry"] = "2026-11-01T00:00:00+01:00"
    offer_inner = offer.select_one(".site-autumn-offer__inner")
    offer_inner.clear()
    offer_inner.append(fragment(
        f'<span class="site-autumn-offer__text es-promo-copy"><span class="es-promo-main">Lediga veckor i september och oktober</span><span class="es-promo-detail">Hela villan från 2 226 € / 7 nätter · flexibel ankomst från 12 september <a class="site-autumn-offer__cta" data-analytics-event="special_offer_click" data-offer-id="september-october-2026-sv" href="{BOOKING}">Se priser →</a></span></span>'
    ))
    close = offer.select_one("[data-site-offer-close]")
    if close:
        close["aria-label"] = "Stäng erbjudandet"

    soup.main.replace_with(fragment(build_main()))
    soup.footer.replace_with(fragment(build_footer()))

    floating = soup.select_one(".site-floating-actions")
    if floating is None:
        raise RuntimeError("Floating actions are missing")
    floating["aria-label"] = "Kontakta och boka Villa Almale"
    whatsapp = floating.select_one(".site-floating-action--whatsapp")
    booking = floating.select_one(".site-floating-action--booking")
    if whatsapp is None or booking is None:
        raise RuntimeError("Floating WhatsApp or booking action is missing")
    whatsapp["href"] = WHATSAPP_URL
    whatsapp["aria-label"] = "Fråga Villa Almale på WhatsApp"
    whatsapp.find("span").string = "WhatsApp"
    booking["href"] = BOOKING
    booking["aria-label"] = "Se tillgänglighet och boka Villa Almale"
    booking.find("span").string = "Boka"

    action_script = soup.find(id="villa-almale-v7-4-global-actions-script")
    if action_script and action_script.string:
        action_script.string = action_script.string.replace(
            "villa-almale-spanish-september-offer-v2",
            "villa-almale-swedish-september-offer-v1",
        )

    update_json_ld(soup)
    write_html(destination, soup)


def validate(root: Path) -> None:
    sv = root / "off-season/sv/index.html"
    soup = parse(sv.read_text(encoding="utf-8"))
    text = soup.get_text(" ", strip=True)
    assert soup.html.get("lang") == "sv"
    assert len(soup.find_all("h1")) == 1
    assert soup.find("h1").get_text(" ", strip=True) == "En hel villa för golfveckan på Costa de la Luz."
    assert soup.find("link", rel="canonical").get("href") == SV_URL
    assert len(soup.find_all("link", rel="alternate", hreflang="sv")) == 1
    assert len(soup.select('.lang-panel a[hreflang="sv"]')) == 1
    assert len(soup.select(".site-floating-action--whatsapp")) == 1
    assert len(soup.select(".site-floating-action--booking")) == 1
    assert len(soup.select("a[data-analytics-event='booking_click']")) >= 4
    assert len(soup.select("a[data-analytics-event='whatsapp_click']")) == 2
    assert len(soup.select("a[data-analytics-event='golf_club_click']")) == 7
    assert len(soup.select("a[data-analytics-event='transfer_click']")) == 2
    assert "Hela villan från 2 226 € / 7 nätter" in text
    assert "Golf Nuevo Portil till fots" in text
    assert "268 soltimmar" in text and "211 soltimmar" in text
    assert "Minsta vistelse är från fyra nätter" in text
    assert "/es/reservation.html" not in str(soup)
    assert "Hola," not in str(soup)
    assert "Septiembre" not in text
    assert "Välkommen" not in text
    for block in soup.find_all("script", attrs={"type": "application/ld+json"}):
        json.loads(block.string or block.get_text())

    for relative in (*LANGUAGE_PAGES, "off-season/sv/index.html"):
        page = parse((root / relative).read_text(encoding="utf-8"))
        assert len(page.find_all("link", rel="alternate", hreflang="sv")) == 1, relative
        assert len(page.select('.lang-panel a[hreflang="sv"]')) == 1, relative

    print("Villa Almale V7.8 Swedish golf campaign landing page validated.")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: v78-swedish-golf-campaign.py /path/to/site-root")
    root = Path(sys.argv[1])
    source = root / "off-season/es/index.html"
    if not source.is_file():
        raise RuntimeError(f"Missing Spanish source page: {source}")
    transform_spanish_to_swedish(source, root / "off-season/sv/index.html")
    for relative in LANGUAGE_PAGES:
        path = root / relative
        if not path.is_file():
            raise RuntimeError(f"Missing language page: {path}")
        add_swedish_discovery(path)
    add_swedish_discovery(root / "off-season/sv/index.html")
    validate(root)


if __name__ == "__main__":
    main()
