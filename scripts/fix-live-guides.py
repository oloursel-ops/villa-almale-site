#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])


def sub_one(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return updated


def replace_comfort_cards(text: str, cards: str, rain_tag: str, label: str) -> str:
    if cards in text:
        return text
    pattern = (
        r'(<section id="confort">.*?<div class="grid">\s*'
        r'<article class="card half">.*?</article>)\s*.*?'
        r'(?=<article class="card half"><div class="tag"><span>'
        + re.escape(rain_tag)
        + r'</span></div>)'
    )
    updated, count = re.subn(
        pattern,
        lambda match: match.group(1) + "\n" + cards + "\n",
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError(f"{label}: stable comfort-section boundaries not found")
    return updated


DATA = {
    "fr": {
        "intro": "La maison n’est pas entièrement climatisée. Trois climatiseurs mobiles équipent la suite principale, le salon et l’espace couchage du rez-de-chaussée. Deux chambres avec lits simples disposent de ventilateurs de plafond. L’aération aux bonnes heures, l’ombre et les moustiquaires restent essentielles.",
        "rain_tag": "Pluie et vent",
        "cards": '<article class="card half"><div class="tag"><span>Climatisation mobile</span></div><h3><span>Trois appareils, usage raisonné</span></h3><p>Un climatiseur mobile de 7 000 BTU se trouve dans la suite principale. Deux appareils de 9 000 BTU équipent le salon et l’espace couchage du rez-de-chaussée. Utilisez-les uniquement portes et fenêtres fermées. Éteignez-les dès que vous quittez la pièce et systématiquement lorsque vous vous absentez de la maison. Ne déplacez pas les appareils sans nécessité.</p></article><article class="card half"><div class="tag"><span>Ventilateurs de plafond</span></div><h3><span>Deux chambres avec lits simples</span></h3><p>Deux chambres avec lits simples sont équipées de ventilateurs de plafond. Éteignez-les en quittant la chambre et avant toute absence de la maison.</p></article>',
        "cooking": "Cuisson",
        "oven": '<article class="card half"><div class="pad"><div class="tag"><span>Cuisson</span></div><h3><span>Plaques de cuisson et four</span></h3><ul><li>Le four et les plaques de cuisson sont disponibles.</li><li>Choisissez le mode et la température adaptés, puis vérifiez que toutes les commandes sont sur arrêt après usage.</li><li>Ne laissez jamais une cuisson sans surveillance et gardez manches, torchons et câbles éloignés des zones chaudes.</li><li>Après refroidissement, nettoyez les projections sans produit abrasif. Évitez d’utiliser simultanément plusieurs appareils électriques très puissants.</li></ul></div></article>',
        "safety": '<section class="section" id="guest-safety-information"><div class="container"><div class="section-head"><span class="eyebrow">Sécurité et recours</span><h2>Informations utiles pendant le séjour</h2></div><div class="cards"><article class="card half"><div class="tag"><span>Premiers soins</span></div><h3><span>Trousse à pharmacie</span></h3><p>Une trousse de premiers soins est disponible dans le WC du rez-de-chaussée. En cas d’urgence médicale, appelez le <strong>112</strong>.</p></article><article class="card half"><div class="tag"><span>Réclamation</span></div><h3><span>Hoja de Reclamaciones</span></h3><p>La feuille officielle de réclamation de la Junta de Andalucía est disponible dans le logement. Contactez-nous si vous souhaitez l’utiliser.</p></article></div></div></section>'
    },
    "en": {
        "intro": "The house is not fully air-conditioned. Three portable air-conditioning units serve the main suite, living room and ground-floor sleeping area. Two twin bedrooms have ceiling fans. Ventilation at the right times, shade and mosquito screens remain important.",
        "rain_tag": "Rain and wind",
        "cards": '<article class="card half"><div class="tag"><span>Portable air conditioning</span></div><h3><span>Three units, responsible use</span></h3><p>A 7,000 BTU portable unit is installed in the main suite. Two 9,000 BTU units serve the living room and the ground-floor sleeping area. Use them only with doors and windows closed. Switch them off whenever you leave the room and always before leaving the house. Do not move the units unless necessary.</p></article><article class="card half"><div class="tag"><span>Ceiling fans</span></div><h3><span>Two twin bedrooms</span></h3><p>Two twin bedrooms have ceiling fans. Switch them off when leaving the bedroom and before leaving the house.</p></article>',
        "cooking": "Cooking",
        "oven": '<article class="card half"><div class="pad"><div class="tag"><span>Cooking</span></div><h3><span>Hob and oven</span></h3><ul><li>The oven and hob are available for use.</li><li>Select the appropriate function and temperature, then make sure every control is switched off after use.</li><li>Never leave cooking unattended and keep handles, cloths and cables away from hot areas.</li><li>Once cool, wipe away splashes without abrasive products. Avoid using several high-power electrical appliances at the same time.</li></ul></div></article>',
        "safety": '<section class="section" id="guest-safety-information"><div class="container"><div class="section-head"><span class="eyebrow">Safety and complaints</span><h2>Useful information during your stay</h2></div><div class="cards"><article class="card half"><div class="tag"><span>First aid</span></div><h3><span>First-aid kit</span></h3><p>A first-aid kit is kept in the ground-floor WC. In a medical emergency, call <strong>112</strong>.</p></article><article class="card half"><div class="tag"><span>Complaints</span></div><h3><span>Official complaints form</span></h3><p>The official Junta de Andalucía Hoja de Reclamaciones is available in the property. Contact us if you wish to use it.</p></article></div></div></section>'
    },
    "es": {
        "intro": "La casa no está climatizada por completo. Hay tres equipos portátiles en la suite principal, el salón y la zona de dormitorio de la planta baja. Dos dormitorios con camas individuales tienen ventiladores de techo. Sigue siendo importante ventilar a las horas adecuadas, mantener la sombra y usar las mosquiteras.",
        "rain_tag": "Lluvia y viento",
        "cards": '<article class="card half"><div class="tag"><span>Aire acondicionado portátil</span></div><h3><span>Tres equipos, uso responsable</span></h3><p>La suite principal dispone de un equipo portátil de 7.000 BTU. Otros dos equipos de 9.000 BTU están en el salón y en la zona de dormitorio de la planta baja. Úsalos solo con puertas y ventanas cerradas. Apágalos al salir de la estancia y siempre antes de ausentarte de la casa. No muevas los equipos salvo necesidad.</p></article><article class="card half"><div class="tag"><span>Ventiladores de techo</span></div><h3><span>Dos dormitorios con camas individuales</span></h3><p>Dos dormitorios con camas individuales tienen ventiladores de techo. Apágalos al salir del dormitorio y antes de ausentarte de la casa.</p></article>',
        "cooking": "Cocina",
        "oven": '<article class="card half"><div class="pad"><div class="tag"><span>Cocina</span></div><h3><span>Placa y horno</span></h3><ul><li>El horno y la placa de cocina están disponibles.</li><li>Selecciona la función y la temperatura adecuadas y comprueba que todos los mandos queden apagados después del uso.</li><li>No dejes nunca la cocción sin vigilancia y mantén mangos, paños y cables alejados de las zonas calientes.</li><li>Cuando se enfríe, limpia las salpicaduras sin productos abrasivos. Evita utilizar al mismo tiempo varios aparatos eléctricos de gran potencia.</li></ul></div></article>',
        "safety": '<section class="section" id="guest-safety-information"><div class="container"><div class="section-head"><span class="eyebrow">Seguridad y reclamaciones</span><h2>Información útil durante la estancia</h2></div><div class="cards"><article class="card half"><div class="tag"><span>Primeros auxilios</span></div><h3><span>Botiquín</span></h3><p>Hay un botiquín de primeros auxilios en el aseo de la planta baja. En caso de urgencia médica, llama al <strong>112</strong>.</p></article><article class="card half"><div class="tag"><span>Reclamaciones</span></div><h3><span>Hoja de Reclamaciones</span></h3><p>La Hoja de Reclamaciones oficial de la Junta de Andalucía está disponible en el alojamiento. Contacta con nosotros si deseas utilizarla.</p></article></div></div></section>'
    }
}

for lang, d in DATA.items():
    path = ROOT / lang / "index.html"
    text = path.read_text(encoding="utf-8")

    if d["intro"] not in text:
        text = sub_one(
            text,
            r'(<section id="confort">\s*<h2>.*?</h2>\s*)<p class="section-intro"><span>.*?</span></p>',
            r'\1<p class="section-intro"><span>' + d["intro"] + r'</span></p>',
            f"{lang} comfort introduction",
        )

    text = replace_comfort_cards(
        text,
        d["cards"],
        d["rain_tag"],
        f"{lang} air-conditioning cards",
    )

    if d["oven"] not in text:
        oven_pattern = (
            r'<article class="card half">\s*<div class="pad">\s*'
            r'<div class="tag"><span>' + re.escape(d["cooking"]) + r'</span></div>\s*'
            r'<h3><span>.*?(?:maintenance|mantenimiento).*?</span></h3>\s*'
            r'<div[^>]*class="maintenance"[^>]*>.*?</div>\s*<ul>.*?</ul>\s*</div>\s*</article>'
        )
        text = sub_one(text, oven_pattern, d["oven"], f"{lang} oven card")

    if 'id="guest-safety-information"' not in text:
        if "</main>" not in text:
            raise RuntimeError(f"{lang}: closing main tag not found")
        text = text.replace("</main>", d["safety"] + "\n</main>", 1)

    text = text.replace("zona de descanso de la planta baja", "zona de dormitorio de la planta baja")
    path.write_text(text, encoding="utf-8")

print("Live guides corrected successfully.")
