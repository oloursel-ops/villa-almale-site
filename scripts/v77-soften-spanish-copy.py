#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString


DATE = "2026-08-05"


def set_text(node, expected: str, replacement: str, label: str) -> None:
    if node is None:
        raise RuntimeError(f"Missing {label}")
    current = node.get_text(" ", strip=True)
    if current == replacement:
        return
    if current != expected:
        raise RuntimeError(f"Unexpected {label}: {current!r}")
    node.string = replacement


def replace_text_node(container, expected: str, replacement: str, label: str) -> None:
    if container is None:
        raise RuntimeError(f"Missing {label}")
    for text_node in container.find_all(string=True):
        if not isinstance(text_node, NavigableString):
            continue
        stripped = str(text_node).strip()
        if stripped == replacement:
            return
        if stripped == expected:
            prefix = " " if str(text_node).startswith(" ") else ""
            suffix = " " if str(text_node).endswith(" ") else ""
            text_node.replace_with(prefix + replacement + suffix)
            return
    raise RuntimeError(f"Unexpected {label}: expected text not found")


def update_date_modified(node) -> None:
    if isinstance(node, dict):
        typ = node.get("@type")
        types = {typ} if isinstance(typ, str) else set(typ or [])
        if "WebPage" in types:
            node["dateModified"] = DATE
        for value in node.values():
            update_date_modified(value)
    elif isinstance(node, list):
        for value in node:
            update_date_modified(value)


def patch(path: Path) -> None:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    if soup.head is None or soup.body is None:
        raise RuntimeError("Spanish landing page is missing head/body")
    if len(soup.find_all("h1")) != 1:
        raise RuntimeError("Spanish landing page must contain exactly one H1")

    canonical = soup.find("link", rel="canonical")
    canonical_before = canonical.get("href") if canonical else None

    golf = soup.select_one("section#golf")
    set_text(
        golf.select_one(".section-heading h2") if golf else None,
        "Acceso, campos, reservas y traslados en un solo bloque.",
        "Golf a pie y varios campos para cambiar de recorrido.",
        "golf heading",
    )
    set_text(
        golf.select_one(".section-heading > p") if golf else None,
        "Villa Almale ofrece únicamente alojamiento. Las salidas, green fees, material y traslados se consultan y pagan directamente a cada proveedor independiente.",
        "Desde Villa Almale, cada grupo puede organizar libremente sus salidas: Golf Nuevo Portil se alcanza a pie y otros campos destacados están a poca distancia en coche.",
        "golf introduction",
    )
    golf_notices = golf.select(".notice-box") if golf else []
    if len(golf_notices) < 2:
        raise RuntimeError("Golf transfer notice is missing")
    set_text(
        golf_notices[-1].find("strong"),
        "Traslados de golf independientes.",
        "Traslados a los campos.",
        "golf transfer heading",
    )
    replace_text_node(
        golf_notices[-1],
        "Un operador local puede presupuestar recorridos a los campos de la zona.",
        "Un operador local puede preparar recorridos a medida para el grupo.",
        "golf transfer copy",
    )

    nautical = soup.select_one("section#nautical")
    set_text(
        nautical.select_one(".section-heading h2") if nautical else None,
        "Ría, mar y actividades según las condiciones.",
        "La Ría, el mar y la Flecha del Rompido desde el agua.",
        "nautical heading",
    )
    nautical_cards = nautical.select(".cards article") if nautical else []
    if len(nautical_cards) != 3:
        raise RuntimeError("Expected three nautical cards")
    set_text(
        nautical_cards[0].find("p"),
        "La Ría ofrece un entorno protegido para salir sobre el agua cuando la marea y la meteorología lo permiten.",
        "La Ría ofrece aguas resguardadas y paisajes abiertos para descubrir la costa en paddle o kayak.",
        "paddle copy",
    )
    set_text(
        nautical_cards[1].find("p"),
        "Desde El Rompido se pueden consultar travesías, excursiones y accesos en barco con los prestadores de la zona.",
        "Desde El Rompido parten travesías y excursiones hacia la Flecha, con distintas opciones para acercarse a sus playas.",
        "boat copy",
    )
    set_text(
        nautical_cards[2].find("h3"),
        "Condiciones antes de salir",
        "El mejor momento del día",
        "nautical conditions heading",
    )
    set_text(
        nautical_cards[2].find("p"),
        "Las horas de marea y el estado del mar cambian cada día; consultar la información oficial forma parte de la salida.",
        "Las mareas transforman el paisaje de la Ría; comprobar los horarios ayuda a elegir el momento más agradable para cada salida.",
        "nautical conditions copy",
    )
    nautical_notice = nautical.select_one(".notice-box") if nautical else None
    set_text(
        nautical_notice.find("strong") if nautical_notice else None,
        "Consulta las condiciones oficiales.",
        "Elige el mejor momento.",
        "nautical notice heading",
    )

    practical = soup.select_one("section#practical")
    set_text(
        practical.select_one(".section-heading h2") if practical else None,
        "Reserva, llegadas y confort — claramente separados de las actividades.",
        "Una estancia sencilla de organizar.",
        "practical heading",
    )
    practical_cards = practical.select(".rich-grid article") if practical else []
    if len(practical_cards) != 4:
        raise RuntimeError("Expected four practical cards")
    set_text(practical_cards[0].find("h3"), "Solo alojamiento", "La villa, a vuestro ritmo", "accommodation heading")
    set_text(
        practical_cards[0].find("p"),
        "La tarifa cubre la villa según las condiciones del motor de reserva. El transporte y las actividades se reservan por separado.",
        "La reserva incluye la villa completa; cada grupo puede añadir libremente transporte, golf, actividades o excursiones según su programa.",
        "accommodation copy",
    )
    set_text(
        practical_cards[2].find("p"),
        "Un operador local independiente puede proponer traslados privados desde Faro o Sevilla.",
        "Es posible solicitar un traslado privado desde Faro o Sevilla para llegar directamente a la villa.",
        "airport transfer copy",
    )
    set_text(
        practical_cards[2].find("a"),
        "Solicitar presupuesto independiente →",
        "Solicitar presupuesto →",
        "airport transfer link",
    )
    set_text(
        practical_cards[3].find("p"),
        "El insert de leña calienta el salón. La casa no dispone de calefacción central ni climatización integral; tres aparatos portátiles y ventiladores complementan algunas estancias.",
        "En las noches más frescas, el insert de leña aporta calidez al salón. La casa cuenta además con tres aparatos portátiles y ventiladores en varias estancias.",
        "seasonal comfort copy",
    )
    practical_notice = practical.select_one(".notice-box") if practical else None
    set_text(
        practical_notice.find("strong") if practical_notice else None,
        "Proveedores independientes.",
        "Actividades a la carta.",
        "practical notice heading",
    )
    replace_text_node(
        practical_notice,
        "Cada operador fija sus precios, disponibilidad, condiciones y formas de pago. La información de esta página no constituye un paquete.",
        "Golf, traslados y experiencias se reservan directamente con cada operador, para que el grupo pueda componer su propio programa.",
        "practical notice copy",
    )

    fireplace_answer = None
    for details in soup.select("section#faq details"):
        summary = details.find("summary")
        if summary and summary.get_text(" ", strip=True) == "¿Se puede utilizar la chimenea?":
            fireplace_answer = details.find("p")
            break
    set_text(
        fireplace_answer,
        "Sí. El salón dispone de un insert de leña funcional y la leña se guarda en el garaje. Es un complemento de confort, no una calefacción integral.",
        "Sí. El salón dispone de un insert de leña funcional y la leña se guarda en el garaje. Aporta un ambiente acogedor en las noches más frescas.",
        "fireplace FAQ answer",
    )

    climate_source = soup.select_one("#clima-septiembre-octubre .es-climate-source")
    replace_text_node(
        climate_source,
        ". Son valores medios de referencia, no una previsión diaria; junto al mar, las condiciones de Nuevo Portil pueden variar.",
        ". Valores medios de referencia; el tiempo diario en Nuevo Portil puede variar.",
        "climate source note",
    )

    for block in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = block.string or block.get_text()
        payload = json.loads(raw)
        update_date_modified(payload)
        block.string = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    output = str(soup)
    if not output.lstrip().lower().startswith("<!doctype"):
        output = "<!DOCTYPE html>\n" + output
    path.write_text(output, encoding="utf-8")

    check = BeautifulSoup(output, "html.parser")
    text = check.get_text(" ", strip=True)
    expected_phrases = (
        "Golf a pie y varios campos para cambiar de recorrido.",
        "La Ría, el mar y la Flecha del Rompido desde el agua.",
        "El mejor momento del día",
        "Una estancia sencilla de organizar.",
        "La villa, a vuestro ritmo",
        "Actividades a la carta.",
        "Aporta un ambiente acogedor en las noches más frescas.",
    )
    defensive_phrases = (
        "ofrece únicamente alojamiento",
        "según las condiciones",
        "claramente separados de las actividades",
        "no constituye un paquete",
        "no una calefacción integral",
        "presupuesto independiente",
    )
    for phrase in expected_phrases:
        assert phrase in text, phrase
    for phrase in defensive_phrases:
        assert phrase not in text, phrase
    assert len(check.find_all("h1")) == 1
    assert len(check.select(".site-floating-actions .site-floating-action--whatsapp")) == 1
    assert len(check.select(".site-floating-actions .site-floating-action--booking")) == 1
    assert len(check.select("section#golf a[data-analytics-event='golf_club_click']")) == 7
    assert len(check.select("a[data-analytics-event='transfer_click']")) >= 2
    canonical_after = check.find("link", rel="canonical")
    assert (canonical_after.get("href") if canonical_after else None) == canonical_before

    print("Villa Almale V7.7 warmer Spanish landing-page copy validated.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: v77-soften-spanish-copy.py /path/to/off-season/es/index.html")
    patch(Path(sys.argv[1]))
