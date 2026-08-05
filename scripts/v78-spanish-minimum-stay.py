#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup


DATE = "2026-08-05"
PRACTICAL_HEADING = "Llegadas flexibles desde el 12 de septiembre"
OLD_PRACTICAL = (
    "A partir del 12 de septiembre, los días de llegada son flexibles según disponibilidad, "
    "para una estancia mínima de siete noches."
)
NEW_PRACTICAL = (
    "A partir del 12 de septiembre, los días de llegada son flexibles según disponibilidad. "
    "Estancia mínima: desde 4 noches, según la semana."
)
FAQ_QUESTION = "¿Qué flexibilidad hay a partir del 12 de septiembre?"
OLD_FAQ = (
    "A partir del 12 de septiembre, las llegadas son flexibles según disponibilidad, "
    "con una estancia mínima de siete noches. El motor de reserva muestra las fechas aplicables."
)
NEW_FAQ = (
    "A partir del 12 de septiembre, las llegadas son flexibles según disponibilidad. "
    "Estancia mínima: desde 4 noches, según la semana. "
    "El motor de reserva muestra las fechas aplicables."
)


def set_text(node, accepted: set[str], replacement: str, label: str) -> None:
    if node is None:
        raise RuntimeError(f"Missing {label}")
    current = node.get_text(" ", strip=True)
    if current == replacement:
        return
    if current not in accepted:
        raise RuntimeError(f"Unexpected {label}: {current!r}")
    node.string = replacement


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

    practical_article = None
    for article in soup.select("section#practical .rich-grid article"):
        heading = article.find("h3")
        if heading and heading.get_text(" ", strip=True) == PRACTICAL_HEADING:
            practical_article = article
            break
    if practical_article is None:
        raise RuntimeError("Minimum-stay practical card not found")
    set_text(
        practical_article.find("p"),
        {OLD_PRACTICAL, NEW_PRACTICAL},
        NEW_PRACTICAL,
        "minimum-stay practical copy",
    )

    faq_details = None
    for details in soup.select("section#faq details"):
        summary = details.find("summary")
        if summary and summary.get_text(" ", strip=True) == FAQ_QUESTION:
            faq_details = details
            break
    if faq_details is None:
        raise RuntimeError("Minimum-stay FAQ entry not found")
    set_text(
        faq_details.find("p"),
        {OLD_FAQ, NEW_FAQ},
        NEW_FAQ,
        "minimum-stay FAQ answer",
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
    phrase = "Estancia mínima: desde 4 noches, según la semana."
    assert text.count(phrase) == 2
    assert "estancia mínima de siete noches" not in text
    assert len(check.find_all("h1")) == 1
    assert len(check.select(".site-floating-actions .site-floating-action--whatsapp")) == 1
    assert len(check.select(".site-floating-actions .site-floating-action--booking")) == 1

    print("Villa Almale V7.8 Spanish minimum-stay wording validated.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: v78-spanish-minimum-stay.py /path/to/off-season/es/index.html")
    patch(Path(sys.argv[1]))
