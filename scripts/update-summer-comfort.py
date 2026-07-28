#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("production-content")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected exactly one occurrence, found {count}: {old[:90]!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def replace_all(path: Path, old: str, new: str, minimum: int = 1) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count < minimum:
        raise RuntimeError(f"{path}: expected at least {minimum} occurrences, found {count}: {old[:90]!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main multilingual home page
# ---------------------------------------------------------------------------
root = ROOT / "index.html"
replace_all(root, '"dateModified":"2026-07-27"', '"dateModified":"2026-07-28"')
replace_once(
    root,
    '"amenityFeature":[{"@type":"LocationFeatureSpecification","name":"Private fenced saltwater pool","value":true},{"@type":"LocationFeatureSpecification","name":"Private garden","value":true},{"@type":"LocationFeatureSpecification","name":"Fibre internet","value":true},{"@type":"LocationFeatureSpecification","name":"Equipped kitchen","value":true},{"@type":"LocationFeatureSpecification","name":"On-site parking","value":true}]',
    '"amenityFeature":[{"@type":"LocationFeatureSpecification","name":"Private fenced saltwater pool","value":true},{"@type":"LocationFeatureSpecification","name":"Private garden","value":true},{"@type":"LocationFeatureSpecification","name":"Fibre internet","value":true},{"@type":"LocationFeatureSpecification","name":"Equipped kitchen","value":true},{"@type":"LocationFeatureSpecification","name":"On-site parking","value":true},{"@type":"LocationFeatureSpecification","name":"Three mobile air-conditioning units in selected rooms","value":true},{"@type":"LocationFeatureSpecification","name":"Ceiling fans in both twin bedrooms","value":true}]',
)
replace_once(
    root,
    'Il n’y a pas de climatisation fixe. Un climatiseur mobile, deux ventilateurs et des ventilateurs supplémentaires sur demande sont disponibles.',
    'La maison n’est pas entièrement climatisée. Trois climatiseurs mobiles équipent la suite principale, le salon et l’espace nuit du rez-de-chaussée. Les deux chambres à lits simples disposent également de ventilateurs de plafond.',
)
replace_once(
    root,
    '<article class="practical-card"><strong data-i="comfort">Pas de climatisation fixe</strong><span data-i="comfortT">1 climatiseur mobile, 2 ventilateurs, d’autres sur demande et moustiquaires aux fenêtres équipées.</span></article>',
    '<article class="practical-card"><strong data-i="comfort">Climatisation mobile ciblée</strong><span data-i="comfortT">3 climatiseurs mobiles : suite principale, salon et espace nuit du rez-de-chaussée. Ventilateurs de plafond dans les 2 chambres à lits simples.</span></article>',
)
replace_once(
    root,
    '<details><summary data-i="fq3">La maison dispose-t-elle de la climatisation ?</summary><p data-i="fa3">Il n’y a pas de climatisation fixe. Un climatiseur mobile, deux ventilateurs et des ventilateurs supplémentaires sur demande sont disponibles.</p></details>',
    '<details><summary data-i="fq3">La maison dispose-t-elle de la climatisation ?</summary><p data-i="fa3">La maison n’est pas entièrement climatisée. Trois climatiseurs mobiles équipent la suite principale, le salon et l’espace nuit du rez-de-chaussée. Deux ventilateurs de plafond équipent les chambres à lits simples.</p></details>',
)
replace_all(root, "comfort:'Pas de climatisation fixe'", "comfort:'Climatisation mobile ciblée'")
replace_all(root, "comfortT:'1 climatiseur mobile, 2 ventilateurs, d’autres sur demande et moustiquaires aux fenêtres équipées.'", "comfortT:'3 climatiseurs mobiles : suite principale, salon et espace nuit du rez-de-chaussée. Ventilateurs de plafond dans les 2 chambres à lits simples.'")
replace_all(root, "fa3:'Il n’y a pas de climatisation fixe. Un climatiseur mobile, deux ventilateurs et des ventilateurs supplémentaires sur demande sont disponibles.'", "fa3:'La maison n’est pas entièrement climatisée. Trois climatiseurs mobiles équipent la suite principale, le salon et l’espace nuit du rez-de-chaussée. Deux ventilateurs de plafond équipent les chambres à lits simples.'")
replace_all(root, "comfort:'No fixed air conditioning'", "comfort:'Targeted mobile air conditioning'")
replace_all(root, "comfortT:'1 mobile air-conditioning unit, 2 fans, more on request and mosquito screens on equipped windows.'", "comfortT:'3 mobile air-conditioning units: main suite, living room and ground-floor sleeping area. Ceiling fans in both twin bedrooms.'")
replace_all(root, "fa3:'There is no fixed air conditioning. One mobile unit, two fans and additional fans on request are available.'", "fa3:'The house is not fully air-conditioned. Three mobile units serve the main suite, living room and ground-floor sleeping area. Both twin bedrooms also have ceiling fans.'")
replace_all(root, "comfort:'Sin aire acondicionado fijo'", "comfort:'Climatización portátil en zonas concretas'")
replace_all(root, "comfortT:'1 climatizador portátil, 2 ventiladores, más bajo petición y mosquiteras en las ventanas equipadas.'", "comfortT:'3 climatizadores portátiles: suite principal, salón y zona de descanso de la planta baja. Ventiladores de techo en los 2 dormitorios con camas individuales.'")
replace_all(root, "fa3:'No hay aire acondicionado fijo. Hay un climatizador portátil, dos ventiladores y ventiladores adicionales bajo petición.'", "fa3:'La casa no está climatizada por completo. Hay tres aparatos portátiles en la suite principal, el salón y la zona de descanso de la planta baja. Los dos dormitorios con camas individuales tienen ventiladores de techo.'")

# ---------------------------------------------------------------------------
# Stand-alone English and Spanish pages
# ---------------------------------------------------------------------------
en = ROOT / "en" / "index.html"
replace_all(en, '"dateModified":"2026-07-27"', '"dateModified":"2026-07-28"')
replace_once(en, 'There is no fixed air conditioning. One mobile unit, two fans and additional fans on request are available.', 'The house is not fully air-conditioned. Three mobile units serve the main suite, living room and ground-floor sleeping area. Both twin bedrooms also have ceiling fans.')
replace_once(en, '<article class="practical-card"><h3>No fixed air conditioning</h3><p>One mobile air-conditioning unit, two fans, additional fans on request and mosquito screens on equipped windows.</p></article>', '<article class="practical-card"><h3>Targeted mobile air conditioning</h3><p>Three mobile units serve the main suite, living room and ground-floor sleeping area. Both twin bedrooms have ceiling fans.</p></article>')
replace_once(en, '<details><summary>Does the house have air conditioning?</summary><p>There is no fixed air conditioning. One mobile unit, two fans and additional fans on request are available.</p></details>', '<details><summary>Does the house have air conditioning?</summary><p>The house is not fully air-conditioned. Three mobile units serve the main suite, living room and ground-floor sleeping area. Both twin bedrooms also have ceiling fans.</p></details>')

es = ROOT / "es" / "index.html"
replace_all(es, '"dateModified":"2026-07-27"', '"dateModified":"2026-07-28"')
replace_once(es, 'No hay aire acondicionado fijo. Hay un aparato portátil, dos ventiladores y ventiladores adicionales bajo petición.', 'La casa no está climatizada por completo. Hay tres aparatos portátiles en la suite principal, el salón y la zona de descanso de la planta baja. Los dos dormitorios con camas individuales tienen ventiladores de techo.')
replace_once(es, '<article class="practical-card"><h3>Sin aire acondicionado fijo</h3><p>Un aparato portátil, dos ventiladores, ventiladores adicionales bajo petición y mosquiteras en las ventanas equipadas.</p></article>', '<article class="practical-card"><h3>Climatización portátil en zonas concretas</h3><p>Tres aparatos portátiles en la suite principal, el salón y la zona de descanso de la planta baja. Ventiladores de techo en los dos dormitorios con camas individuales.</p></article>')
replace_once(es, '<details><summary>¿La casa tiene aire acondicionado?</summary><p>No hay aire acondicionado fijo. Hay un aparato portátil, dos ventiladores y ventiladores adicionales bajo petición.</p></details>', '<details><summary>¿La casa tiene aire acondicionado?</summary><p>La casa no está climatizada por completo. Hay tres aparatos portátiles en la suite principal, el salón y la zona de descanso de la planta baja. Los dos dormitorios con camas individuales tienen ventiladores de techo.</p></details>')

# ---------------------------------------------------------------------------
# Interactive guide — French
# ---------------------------------------------------------------------------
frg = ROOT / "guide" / "fr" / "index.html"
replace_once(frg, '<p class="section-intro"><span>La maison n’est pas équipée d’une climatisation générale. Son confort d’été repose sur l’aération aux bonnes heures, l’ombre et les moustiquaires.</span></p>', '<p class="section-intro"><span>La maison n’est pas entièrement climatisée. Trois climatiseurs mobiles et deux ventilateurs de plafond améliorent le confort des pièces équipées, en complément de l’aération aux bonnes heures, de l’ombre et des moustiquaires.</span></p>')
replace_once(frg, '<article class="card half"><div class="tag"><span>Chambres</span></div><h3><span>Moustiquaires et climatisation mobile</span></h3><p>Toutes les fenêtres disposent de moustiquaires : utilisez-les plutôt que de laisser les ouvertures sans protection. Une climatisation mobile est disponible dans la suite parentale. Utilisez-la portes et fenêtres fermées et éteignez-la en quittant la pièce.</p></article>', '<article class="card half"><div class="tag"><span>Pièces équipées</span></div><h3><span>Trois climatiseurs mobiles et deux ventilateurs de plafond</span></h3><p>Un climatiseur mobile de 7 000 BTU est installé dans la suite principale. Deux appareils de 9 000 BTU équipent le salon et l’espace nuit du rez-de-chaussée. Les deux chambres à lits simples disposent de ventilateurs de plafond.</p><p class="tip"><span>Pour chaque climatiseur : fermez portes et fenêtres pendant son fonctionnement et éteignez-le dès que vous quittez la pièce ou la maison. Les équipements ne doivent jamais fonctionner en l’absence des occupants.</span></p></article>')
replace_once(frg, '<div class="key"><b>💬 Assistance pendant le séjour</b><p>Pour toute question concernant la maison, utilisez la messagerie de votre réservation. Les numéros directs sont communiqués uniquement aux voyageurs enregistrés.</p></div>', '<div class="key"><b>💬 Assistance pendant le séjour</b><p>Pour toute question concernant la maison, utilisez la messagerie de votre réservation. Les numéros directs sont communiqués uniquement aux voyageurs enregistrés.</p></div><div class="key"><b>📄 Hoja de Reclamaciones</b><p>La feuille officielle de réclamation de la Junta de Andalucía est disponible dans le logement. Contactez-nous si vous souhaitez l’utiliser.</p></div>')
replace_once(frg, '<article class="card half"><div class="tag"><span>Incident</span></div><h3><span>Prévenir, ne pas réparer</span></h3><p>Signalez rapidement toute casse, fuite, panne, accident ou objet manquant. Une information précoce permet souvent une solution simple et limite les dommages.</p></article>', '<article class="card half"><div class="tag"><span>Incident</span></div><h3><span>Prévenir, ne pas réparer</span></h3><p>Signalez rapidement toute casse, fuite, panne, accident ou objet manquant. Une information précoce permet souvent une solution simple et limite les dommages.</p></article><article class="card half"><div class="tag"><span>Premiers soins</span></div><h3><span>Trousse à pharmacie</span></h3><p>Une trousse de premiers soins est disponible dans le WC du rez-de-chaussée. En cas d’urgence médicale, appelez le <strong>112</strong>.</p></article>')

# Interactive guide — English
eg = ROOT / "guide" / "en" / "index.html"
replace_once(eg, '<p class="section-intro"><span>The house does not have whole-house air conditioning. Summer comfort relies on ventilation at the right times, shade and mosquito screens.</span></p>', '<p class="section-intro"><span>The house is not fully air-conditioned. Three mobile air-conditioning units and two ceiling fans improve comfort in the equipped rooms, together with ventilation at the right times, shade and mosquito screens.</span></p>')
replace_once(eg, '<article class="card half"><div class="tag"><span>Bedrooms</span></div><h3><span>Mosquito screens and mobile air conditioning</span></h3><p>All windows have mosquito screens: use them rather than leaving openings unprotected. A mobile air-conditioning unit is available in the main suite. Use it with doors and windows closed and switch it off when leaving the room.</p></article>', '<article class="card half"><div class="tag"><span>Equipped rooms</span></div><h3><span>Three mobile air-conditioning units and two ceiling fans</span></h3><p>A 7,000 BTU mobile unit is installed in the main suite. Two 9,000 BTU units serve the living room and the ground-floor sleeping area. Both twin bedrooms have ceiling fans.</p><p class="tip"><span>For every air-conditioning unit: keep doors and windows closed while it is running and switch it off whenever you leave the room or the house. Never leave these appliances running while the property is unoccupied.</span></p></article>')
replace_once(eg, '<div class="key"><b>💬 Assistance during your stay</b><p>For any question about the house, use your booking message thread. Direct telephone numbers are shared only with registered guests.</p></div>', '<div class="key"><b>💬 Assistance during your stay</b><p>For any question about the house, use your booking message thread. Direct telephone numbers are shared only with registered guests.</p></div><div class="key"><b>📄 Official complaints form</b><p>The official Junta de Andalucía Hoja de Reclamaciones is available in the property. Contact us if you wish to use it.</p></div>')
replace_once(eg, '<article class="card half"><div class="tag"><span>Incident</span></div><h3><span>Report it, do not repair it</span></h3><p>Promptly report any breakage, leak, fault, accident or missing item. Early notice often allows a simple solution and limits damage.</p></article>', '<article class="card half"><div class="tag"><span>Incident</span></div><h3><span>Report it, do not repair it</span></h3><p>Promptly report any breakage, leak, fault, accident or missing item. Early notice often allows a simple solution and limits damage.</p></article><article class="card half"><div class="tag"><span>First aid</span></div><h3><span>First-aid kit</span></h3><p>A first-aid kit is kept in the ground-floor WC. In a medical emergency, call <strong>112</strong>.</p></article>')

# Interactive guide — Spanish
esg = ROOT / "guide" / "es" / "index.html"
replace_once(esg, '<p class="section-intro"><span>La casa no dispone de aire acondicionado general. El confort en verano depende de ventilar a las horas adecuadas, de la sombra y de las mosquiteras.</span></p>', '<p class="section-intro"><span>La casa no está climatizada por completo. Tres aparatos portátiles y dos ventiladores de techo mejoran el confort de las estancias equipadas, junto con la ventilación a las horas adecuadas, la sombra y las mosquiteras.</span></p>')
replace_once(esg, '<article class="card half"><div class="tag"><span>Dormitorios</span></div><h3><span>Mosquiteras y aire acondicionado portátil</span></h3><p>Todas las ventanas tienen mosquiteras: utilízalas en lugar de dejar las aberturas sin protección. Hay un aparato de aire acondicionado portátil en la suite principal. Úsalo con puertas y ventanas cerradas y apágalo al salir de la habitación.</p></article>', '<article class="card half"><div class="tag"><span>Estancias equipadas</span></div><h3><span>Tres aparatos portátiles y dos ventiladores de techo</span></h3><p>La suite principal dispone de un aparato portátil de 7.000 BTU. Otros dos aparatos de 9.000 BTU equipan el salón y la zona de descanso de la planta baja. Los dos dormitorios con camas individuales tienen ventiladores de techo.</p><p class="tip"><span>Para cada aparato: mantén puertas y ventanas cerradas mientras funciona y apágalo al salir de la estancia o de la casa. Nunca dejes estos equipos funcionando cuando no haya nadie en la vivienda.</span></p></article>')
replace_once(esg, '<div class="key"><b>💬 Asistencia durante la estancia</b><p>Para cualquier consulta sobre la casa, utiliza la mensajería de tu reserva. Los teléfonos directos se facilitan únicamente a los huéspedes registrados.</p></div>', '<div class="key"><b>💬 Asistencia durante la estancia</b><p>Para cualquier consulta sobre la casa, utiliza la mensajería de tu reserva. Los teléfonos directos se facilitan únicamente a los huéspedes registrados.</p></div><div class="key"><b>📄 Hoja de Reclamaciones</b><p>La Hoja de Reclamaciones oficial de la Junta de Andalucía está disponible en el alojamiento. Contacta con nosotros si deseas utilizarla.</p></div>')
replace_once(esg, '<article class="card half"><div class="tag"><span>Incidencia</span></div><h3><span>Avisar, no reparar</span></h3><p>Comunica rápidamente cualquier rotura, fuga, avería, accidente u objeto que falte. Avisar pronto suele permitir una solución sencilla y limita los daños.</p></article>', '<article class="card half"><div class="tag"><span>Incidencia</span></div><h3><span>Avisar, no reparar</span></h3><p>Comunica rápidamente cualquier rotura, fuga, avería, accidente u objeto que falte. Avisar pronto suele permitir una solución sencilla y limita los daños.</p></article><article class="card half"><div class="tag"><span>Primeros auxilios</span></div><h3><span>Botiquín</span></h3><p>Hay un botiquín de primeros auxilios en el aseo de la planta baja. En caso de urgencia médica, llama al <strong>112</strong>.</p></article>')

print("Summer comfort, first-aid and complaints information updated successfully.")
