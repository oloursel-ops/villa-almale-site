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


def sub_required(text: str, pattern: str, replacement: str, label: str, flags: int = re.S) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise RuntimeError(f"Unable to update {label}: structural marker not found")
    return updated


def insert_before_main_end(text: str, block: str, marker: str) -> str:
    if marker in text:
        return text
    if "</main>" not in text:
        raise RuntimeError("Guide closing </main> marker not found")
    return text.replace("</main>", block + "\n</main>", 1)


def add_amenities(text: str) -> str:
    if "Three mobile air-conditioning units in selected rooms" in text:
        return text
    marker = '{"@type":"LocationFeatureSpecification","name":"On-site parking","value":true}'
    addition = marker + ',{"@type":"LocationFeatureSpecification","name":"Three mobile air-conditioning units in selected rooms","value":true},{"@type":"LocationFeatureSpecification","name":"Ceiling fans in both twin bedrooms","value":true}'
    if marker not in text:
        raise RuntimeError("Accommodation amenity marker not found")
    return text.replace(marker, addition, 1)


# Main multilingual page
root = ROOT / "index.html"
text = read(root)
text = text.replace('"dateModified":"2026-07-27"', '"dateModified":"2026-07-28"')
text = add_amenities(text)
text = text.replace(
    "Il n’y a pas de climatisation fixe. Un climatiseur mobile, deux ventilateurs et des ventilateurs supplémentaires sur demande sont disponibles.",
    "La maison n’est pas entièrement climatisée. Trois climatiseurs mobiles équipent la suite principale, le salon et l’espace nuit du rez-de-chaussée. Deux ventilateurs de plafond équipent les chambres à lits simples.",
)
text = sub_required(
    text,
    r'<article class="practical-card"><strong data-i="comfort">.*?</strong><span data-i="comfortT">.*?</span></article>',
    '<article class="practical-card"><strong data-i="comfort">Climatisation mobile ciblée</strong><span data-i="comfortT">3 climatiseurs mobiles : 7 000 BTU dans la suite principale, 9 000 BTU dans le salon et 9 000 BTU dans l’espace nuit du rez-de-chaussée. Ventilateurs de plafond dans les 2 chambres à lits simples.</span></article>',
    "French practical comfort card",
)
text = sub_required(
    text,
    r'<details><summary data-i="fq3">.*?</summary><p data-i="fa3">.*?</p></details>',
    '<details><summary data-i="fq3">La maison dispose-t-elle de la climatisation ?</summary><p data-i="fa3">La maison n’est pas entièrement climatisée. Trois climatiseurs mobiles équipent la suite principale, le salon et l’espace nuit du rez-de-chaussée. Deux ventilateurs de plafond équipent les chambres à lits simples.</p></details>',
    "French air-conditioning FAQ",
)
repls = {
    "comfort:'Pas de climatisation fixe'": "comfort:'Climatisation mobile ciblée'",
    "comfortT:'1 climatiseur mobile, 2 ventilateurs, d’autres sur demande et moustiquaires aux fenêtres équipées.'": "comfortT:'3 climatiseurs mobiles : 7 000 BTU dans la suite principale, 9 000 BTU dans le salon et 9 000 BTU dans l’espace nuit du rez-de-chaussée. Ventilateurs de plafond dans les 2 chambres à lits simples.'",
    "fa3:'Il n’y a pas de climatisation fixe. Un climatiseur mobile, deux ventilateurs et des ventilateurs supplémentaires sur demande sont disponibles.'": "fa3:'La maison n’est pas entièrement climatisée. Trois climatiseurs mobiles équipent la suite principale, le salon et l’espace nuit du rez-de-chaussée. Deux ventilateurs de plafond équipent les chambres à lits simples.'",
    "comfort:'No fixed air conditioning'": "comfort:'Targeted mobile air conditioning'",
    "comfortT:'1 mobile air-conditioning unit, 2 fans, more on request and mosquito screens on equipped windows.'": "comfortT:'3 mobile units: 7,000 BTU in the main suite, 9,000 BTU in the living room and 9,000 BTU in the ground-floor sleeping area. Ceiling fans in both twin bedrooms.'",
    "fa3:'There is no fixed air conditioning. One mobile unit, two fans and additional fans on request are available.'": "fa3:'The house is not fully air-conditioned. Three mobile units serve the main suite, living room and ground-floor sleeping area. Both twin bedrooms also have ceiling fans.'",
    "comfort:'Sin aire acondicionado fijo'": "comfort:'Climatización portátil en zonas concretas'",
    "comfortT:'1 climatizador portátil, 2 ventiladores, más bajo petición y mosquiteras en las ventanas equipadas.'": "comfortT:'3 aparatos portátiles: 7.000 BTU en la suite principal, 9.000 BTU en el salón y 9.000 BTU en la zona de descanso de la planta baja. Ventiladores de techo en los 2 dormitorios con camas individuales.'",
    "fa3:'No hay aire acondicionado fijo. Hay un climatizador portátil, dos ventiladores y ventiladores adicionales bajo petición.'": "fa3:'La casa no está climatizada por completo. Hay tres aparatos portátiles en la suite principal, el salón y la zona de descanso de la planta baja. Los dos dormitorios con camas individuales tienen ventiladores de techo.'",
}
for old, new in repls.items():
    text = text.replace(old, new)
write(root, text)


# Stand-alone language pages
for lang, title, body, faq in [
    ("en", "Targeted mobile air conditioning", "Three mobile units: 7,000 BTU in the main suite, 9,000 BTU in the living room and 9,000 BTU in the ground-floor sleeping area. Both twin bedrooms have ceiling fans.", "The house is not fully air-conditioned. Three mobile units serve the main suite, living room and ground-floor sleeping area. Both twin bedrooms also have ceiling fans."),
    ("es", "Climatización portátil en zonas concretas", "Tres aparatos portátiles: 7.000 BTU en la suite principal, 9.000 BTU en el salón y 9.000 BTU en la zona de descanso de la planta baja. Los dos dormitorios con camas individuales tienen ventiladores de techo.", "La casa no está climatizada por completo. Hay tres aparatos portátiles en la suite principal, el salón y la zona de descanso de la planta baja. Los dos dormitorios con camas individuales tienen ventiladores de techo."),
]:
    path = ROOT / lang / "index.html"
    t = read(path).replace('"dateModified":"2026-07-27"', '"dateModified":"2026-07-28"')
    t = sub_required(t, r'<article class="practical-card"><h3>.*?(?:air conditioning|aire acondicionado).*?</h3><p>.*?</p></article>', f'<article class="practical-card"><h3>{title}</h3><p>{body}</p></article>', f"{lang} practical comfort card", re.S | re.I)
    if lang == "en":
        t = sub_required(t, r'<details><summary>Does the house have air conditioning\?</summary><p>.*?</p></details>', f'<details><summary>Does the house have air conditioning?</summary><p>{faq}</p></details>', "English FAQ")
    else:
        t = sub_required(t, r'<details><summary>¿La casa tiene aire acondicionado\?</summary><p>.*?</p></details>', f'<details><summary>¿La casa tiene aire acondicionado?</summary><p>{faq}</p></details>', "Spanish FAQ")
    write(path, t)


GUIDE_BLOCKS = {
    "fr": '''<section class="section" id="summer-comfort-update"><div class="container"><div class="section-head"><span class="eyebrow">Confort et sécurité</span><h2>Équipements d’été et informations utiles</h2></div><div class="cards"><article class="card half"><div class="tag"><span>Pièces équipées</span></div><h3><span>Trois climatiseurs mobiles et deux ventilateurs de plafond</span></h3><p>Un climatiseur mobile de 7 000 BTU est installé dans la suite principale. Deux appareils de 9 000 BTU équipent le salon et l’espace nuit du rez-de-chaussée. Les deux chambres à lits simples disposent de ventilateurs de plafond.</p><p class="tip"><span>Fermez portes et fenêtres pendant le fonctionnement. Éteignez les appareils dès que vous quittez la pièce ou la maison ; ils ne doivent jamais fonctionner en l’absence des occupants.</span></p></article><article class="card half"><div class="tag"><span>Premiers soins</span></div><h3><span>Trousse à pharmacie</span></h3><p>Une trousse de premiers soins est disponible dans le WC du rez-de-chaussée. En cas d’urgence médicale, appelez le <strong>112</strong>.</p></article></div><div class="key"><b>📄 Hoja de Reclamaciones</b><p>La feuille officielle de réclamation de la Junta de Andalucía est disponible dans le logement. Contactez-nous si vous souhaitez l’utiliser.</p></div></div></section>''',
    "en": '''<section class="section" id="summer-comfort-update"><div class="container"><div class="section-head"><span class="eyebrow">Comfort and safety</span><h2>Summer equipment and useful information</h2></div><div class="cards"><article class="card half"><div class="tag"><span>Equipped rooms</span></div><h3><span>Three mobile air-conditioning units and two ceiling fans</span></h3><p>A 7,000 BTU mobile unit is installed in the main suite. Two 9,000 BTU units serve the living room and the ground-floor sleeping area. Both twin bedrooms have ceiling fans.</p><p class="tip"><span>Keep doors and windows closed while a unit is running. Switch it off whenever you leave the room or the house; never leave these appliances running while the property is unoccupied.</span></p></article><article class="card half"><div class="tag"><span>First aid</span></div><h3><span>First-aid kit</span></h3><p>A first-aid kit is kept in the ground-floor WC. In a medical emergency, call <strong>112</strong>.</p></article></div><div class="key"><b>📄 Official complaints form</b><p>The official Junta de Andalucía Hoja de Reclamaciones is available in the property. Contact us if you wish to use it.</p></div></div></section>''',
    "es": '''<section class="section" id="summer-comfort-update"><div class="container"><div class="section-head"><span class="eyebrow">Confort y seguridad</span><h2>Equipamiento de verano e información útil</h2></div><div class="cards"><article class="card half"><div class="tag"><span>Estancias equipadas</span></div><h3><span>Tres aparatos portátiles y dos ventiladores de techo</span></h3><p>La suite principal dispone de un aparato portátil de 7.000 BTU. Otros dos aparatos de 9.000 BTU equipan el salón y la zona de descanso de la planta baja. Los dos dormitorios con camas individuales tienen ventiladores de techo.</p><p class="tip"><span>Mantén puertas y ventanas cerradas mientras funciona cada aparato. Apágalo al salir de la estancia o de la casa; nunca dejes estos equipos funcionando cuando no haya nadie en la vivienda.</span></p></article><article class="card half"><div class="tag"><span>Primeros auxilios</span></div><h3><span>Botiquín</span></h3><p>Hay un botiquín de primeros auxilios en el aseo de la planta baja. En caso de urgencia médica, llama al <strong>112</strong>.</p></article></div><div class="key"><b>📄 Hoja de Reclamaciones</b><p>La Hoja de Reclamaciones oficial de la Junta de Andalucía está disponible en el alojamiento. Contacta con nosotros si deseas utilizarla.</p></div></div></section>''',
}

for lang, block in GUIDE_BLOCKS.items():
    path = ROOT / "guide" / lang / "index.html"
    t = read(path)
    t = insert_before_main_end(t, block, 'id="summer-comfort-update"')
    write(path, t)

print("Summer comfort, first-aid and complaints information updated successfully.")
