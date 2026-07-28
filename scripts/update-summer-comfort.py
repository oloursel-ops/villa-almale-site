#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("production-content")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def sub_one(text: str, pattern: str, replacement: str, label: str, flags: int = re.S) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise RuntimeError(f"Unable to update {label}: structural marker not found")
    return updated


def add_amenities(text: str) -> str:
    if "Three mobile air-conditioning units in selected rooms" in text:
        return text
    marker = '{"@type":"LocationFeatureSpecification","name":"On-site parking","value":true}'
    addition = marker + ',{"@type":"LocationFeatureSpecification","name":"Three mobile air-conditioning units in selected rooms","value":true},{"@type":"LocationFeatureSpecification","name":"Ceiling fans in both twin bedrooms","value":true}'
    if marker not in text:
        raise RuntimeError("Accommodation amenity marker not found")
    return text.replace(marker, addition, 1)


FR_TITLE = "Climatisation mobile ciblée"
FR_CARD = "3 climatiseurs mobiles : 7 000 BTU dans la suite principale, 9 000 BTU dans le salon et 9 000 BTU dans l’espace couchage du rez-de-chaussée. Ventilateurs de plafond dans les 2 chambres à lits simples."
FR_FAQ = "La maison n’est pas entièrement climatisée. Trois climatiseurs mobiles équipent la suite principale, le salon et l’espace couchage du rez-de-chaussée. Deux ventilateurs de plafond équipent les chambres à lits simples."
EN_TITLE = "Targeted mobile air conditioning"
EN_CARD = "3 mobile units: 7,000 BTU in the main suite, 9,000 BTU in the living room and 9,000 BTU in the ground-floor sleeping area. Ceiling fans in both twin bedrooms."
EN_FAQ = "The house is not fully air-conditioned. Three mobile units serve the main suite, living room and ground-floor sleeping area. Both twin bedrooms also have ceiling fans."
ES_TITLE = "Climatización portátil en zonas concretas"
ES_CARD = "3 aparatos portátiles: 7.000 BTU en la suite principal, 9.000 BTU en el salón y 9.000 BTU en la zona de dormitorio de la planta baja. Ventiladores de techo en los 2 dormitorios con camas individuales."
ES_FAQ = "La casa no está climatizada por completo. Hay tres aparatos portátiles en la suite principal, el salón y la zona de dormitorio de la planta baja. Los dos dormitorios con camas individuales tienen ventiladores de techo."


# Main multilingual page
root = ROOT / "index.html"
text = read(root)
text = text.replace('"dateModified":"2026-07-27"', '"dateModified":"2026-07-28"')
text = add_amenities(text)
text = sub_one(
    text,
    r'<article class="practical-card"><strong data-i="comfort">.*?</strong><span data-i="comfortT">.*?</span></article>',
    f'<article class="practical-card"><strong data-i="comfort">{FR_TITLE}</strong><span data-i="comfortT">{FR_CARD}</span></article>',
    "French practical comfort card",
)
text = sub_one(
    text,
    r'<details><summary data-i="fq3">.*?</summary><p data-i="fa3">.*?</p></details>',
    f'<details><summary data-i="fq3">La maison dispose-t-elle de la climatisation ?</summary><p data-i="fa3">{FR_FAQ}</p></details>',
    "French air-conditioning FAQ",
)

# Replace both current and legacy translation values, including straight/curly apostrophe variants.
legacy_replacements = {
    "Pas de climatisation fixe": FR_TITLE,
    "1 climatiseur mobile, 2 ventilateurs, d’autres sur demande et moustiquaires aux fenêtres équipées.": FR_CARD,
    "1 climatiseur mobile, 2 ventilateurs, d'autres sur demande et moustiquaires aux fenêtres équipées.": FR_CARD,
    "Climatisation mobile ciblée": FR_TITLE,
    "3 climatiseurs mobiles : 7 000 BTU dans la suite principale, 9 000 BTU dans le salon et 9 000 BTU dans l’espace nuit du rez-de-chaussée. Ventilateurs de plafond dans les 2 chambres à lits simples.": FR_CARD,
    "La maison n’est pas entièrement climatisée. Trois climatiseurs mobiles équipent la suite principale, le salon et l’espace nuit du rez-de-chaussée. Deux ventilateurs de plafond équipent les chambres à lits simples.": FR_FAQ,
    "No fixed air conditioning": EN_TITLE,
    "1 mobile air-conditioning unit, 2 fans, more on request and mosquito screens on equipped windows.": EN_CARD,
    "Targeted mobile air conditioning": EN_TITLE,
    "3 mobile units: 7,000 BTU in the main suite, 9,000 BTU in the living room and 9,000 BTU in the ground-floor sleeping area. Ceiling fans in both twin bedrooms.": EN_CARD,
    "Sin aire acondicionado fijo": ES_TITLE,
    "1 climatizador portátil, 2 ventiladores, más bajo petición y mosquiteras en las ventanas equipadas.": ES_CARD,
    "Climatización portátil en zonas concretas": ES_TITLE,
    "3 aparatos portátiles: 7.000 BTU en la suite principal, 9.000 BTU en el salón y 9.000 BTU en la zona de descanso de la planta baja. Ventiladores de techo en los 2 dormitorios con camas individuales.": ES_CARD,
    "La casa no está climatizada por completo. Hay tres aparatos portátiles en la suite principal, el salón y la zona de descanso de la planta baja. Los dos dormitorios con camas individuales tienen ventiladores de techo.": ES_FAQ,
}
for old, new in legacy_replacements.items():
    text = text.replace(old, new)
write(root, text)


# Stand-alone English and Spanish pages
for lang, title, card, faq in [
    ("en", EN_TITLE, EN_CARD, EN_FAQ),
    ("es", ES_TITLE, ES_CARD, ES_FAQ),
]:
    path = ROOT / lang / "index.html"
    page = read(path).replace('"dateModified":"2026-07-27"', '"dateModified":"2026-07-28"')
    page = sub_one(
        page,
        r'<article class="practical-card"><h3>.*?(?:air conditioning|aire acondicionado|Climatización).*?</h3><p>.*?</p></article>',
        f'<article class="practical-card"><h3>{title}</h3><p>{card}</p></article>',
        f"{lang} practical comfort card",
        re.S | re.I,
    )
    if lang == "en":
        page = sub_one(page, r'<details><summary>Does the house have air conditioning\?</summary><p>.*?</p></details>', f'<details><summary>Does the house have air conditioning?</summary><p>{faq}</p></details>', "English FAQ")
    else:
        page = sub_one(page, r'<details><summary>¿La casa tiene aire acondicionado\?</summary><p>.*?</p></details>', f'<details><summary>¿La casa tiene aire acondicionado?</summary><p>{faq}</p></details>', "Spanish FAQ")
    page = page.replace("zona de descanso de la planta baja", "zona de dormitorio de la planta baja")
    write(path, page)


GUIDE_BLOCKS = {
    "fr": f'''<section class="section" id="summer-comfort-update"><div class="container"><div class="section-head"><span class="eyebrow">Confort et sécurité</span><h2>Équipements d’été et informations utiles</h2></div><div class="cards"><article class="card half"><div class="tag"><span>Pièces équipées</span></div><h3><span>Trois climatiseurs mobiles et deux ventilateurs de plafond</span></h3><p>Un climatiseur mobile de 7 000 BTU est installé dans la suite principale. Deux appareils de 9 000 BTU équipent le salon et l’espace couchage du rez-de-chaussée. Les deux chambres à lits simples disposent de ventilateurs de plafond.</p><p class="tip"><span>Fermez portes et fenêtres pendant le fonctionnement. Éteignez les appareils dès que vous quittez la pièce ou la maison ; ils ne doivent jamais fonctionner en l’absence des occupants.</span></p></article><article class="card half"><div class="tag"><span>Premiers soins</span></div><h3><span>Trousse à pharmacie</span></h3><p>Une trousse de premiers soins est disponible dans le WC du rez-de-chaussée. En cas d’urgence médicale, appelez le <strong>112</strong>.</p></article></div><div class="key"><b>📄 Hoja de Reclamaciones</b><p>La feuille officielle de réclamation de la Junta de Andalucía est disponible dans le logement. Contactez-nous si vous souhaitez l’utiliser.</p></div></div></section>''',
    "en": '''<section class="section" id="summer-comfort-update"><div class="container"><div class="section-head"><span class="eyebrow">Comfort and safety</span><h2>Summer equipment and useful information</h2></div><div class="cards"><article class="card half"><div class="tag"><span>Equipped rooms</span></div><h3><span>Three mobile air-conditioning units and two ceiling fans</span></h3><p>A 7,000 BTU mobile unit is installed in the main suite. Two 9,000 BTU units serve the living room and the ground-floor sleeping area. Both twin bedrooms have ceiling fans.</p><p class="tip"><span>Keep doors and windows closed while a unit is running. Switch it off whenever you leave the room or the house; never leave these appliances running while the property is unoccupied.</span></p></article><article class="card half"><div class="tag"><span>First aid</span></div><h3><span>First-aid kit</span></h3><p>A first-aid kit is kept in the ground-floor WC. In a medical emergency, call <strong>112</strong>.</p></article></div><div class="key"><b>📄 Official complaints form</b><p>The official Junta de Andalucía Hoja de Reclamaciones is available in the property. Contact us if you wish to use it.</p></div></div></section>''',
    "es": '''<section class="section" id="summer-comfort-update"><div class="container"><div class="section-head"><span class="eyebrow">Confort y seguridad</span><h2>Equipamiento de verano e información útil</h2></div><div class="cards"><article class="card half"><div class="tag"><span>Estancias equipadas</span></div><h3><span>Tres aparatos portátiles y dos ventiladores de techo</span></h3><p>La suite principal dispone de un aparato portátil de 7.000 BTU. Otros dos aparatos de 9.000 BTU equipan el salón y la zona de dormitorio de la planta baja. Los dos dormitorios con camas individuales tienen ventiladores de techo.</p><p class="tip"><span>Mantén puertas y ventanas cerradas mientras funciona cada aparato. Apágalo al salir de la estancia o de la casa; nunca dejes estos equipos funcionando cuando no haya nadie en la vivienda.</span></p></article><article class="card half"><div class="tag"><span>Primeros auxilios</span></div><h3><span>Botiquín</span></h3><p>Hay un botiquín de primeros auxilios en el aseo de la planta baja. En caso de urgencia médica, llama al <strong>112</strong>.</p></article></div><div class="key"><b>📄 Hoja de Reclamaciones</b><p>La Hoja de Reclamaciones oficial de la Junta de Andalucía está disponible en el alojamiento. Contacta con nosotros si deseas utilizarla.</p></div></div></section>''',
}

for lang, block in GUIDE_BLOCKS.items():
    path = ROOT / "guide" / lang / "index.html"
    page = read(path)
    pattern = r'<section class="section" id="summer-comfort-update">.*?</section>'
    if re.search(pattern, page, flags=re.S):
        page = re.sub(pattern, block, page, count=1, flags=re.S)
    elif "</main>" in page:
        page = page.replace("</main>", block + "\n</main>", 1)
    else:
        raise RuntimeError(f"{lang} guide closing marker not found")
    page = page.replace("zona de descanso de la planta baja", "zona de dormitorio de la planta baja")
    write(path, page)

print("Air-conditioning count and sleeping-area wording updated consistently.")
