#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup


DATE = "2026-08-06"
OFFICIAL_URL = "https://lamonacillagolf.com/en/"
STYLE_ID = "villa-almale-v79-five-golf-courses"
CSS = """
/* Villa Almale V7.9 - balanced layout for five golf courses */
.course-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
@media(max-width:980px){.course-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:620px){.course-grid{grid-template-columns:1fr}}
"""

PAGES = {
    "off-season/index.html": {
        "kicker": "La Monacilla Golf · 18 km / about 20 min",
        "title": "Olazábal design near Huelva",
        "body": (
            "An 18-hole course near Aljaraque, designed by José María Olazábal, "
            "with broad fairways and large greens."
        ),
        "link": "Official website, rates and booking →",
    },
    "off-season/fr/index.html": {
        "kicker": "Golf La Monacilla · 18 km / env. 20 min",
        "title": "Un parcours signé José María Olazábal",
        "body": (
            "Un parcours de 18 trous près d’Aljaraque, dessiné par José María "
            "Olazábal, avec de larges fairways et de grands greens."
        ),
        "link": "Site officiel, tarifs et réservation →",
    },
    "off-season/es/index.html": {
        "kicker": "Golf La Monacilla · 18 km / unos 20 min",
        "title": "Diseño de José María Olazábal",
        "body": (
            "Un recorrido de 18 hoyos cerca de Aljaraque, diseñado por José María "
            "Olazábal, con calles amplias y grandes greenes."
        ),
        "link": "Web oficial, tarifas y reservas →",
    },
    "off-season/sv/index.html": {
        "kicker": "La Monacilla Golf · 18 km / cirka 20 min",
        "title": "Olazábal-design nära Huelva",
        "body": (
            "En 18-hålsbana nära Aljaraque, designad av José María Olazábal, "
            "med breda fairways och stora greener."
        ),
        "link": "Officiell webbplats, priser och bokning →",
    },
}


def parse(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def write_html(path: Path, soup: BeautifulSoup) -> None:
    output = str(soup)
    if not output.lstrip().lower().startswith("<!doctype"):
        output = "<!DOCTYPE html>\n" + output
    path.write_text(output, encoding="utf-8")


def build_card(soup: BeautifulSoup, copy: dict[str, str]):
    article = soup.new_tag("article", attrs={"class": "course-card"})
    kicker = soup.new_tag("span", attrs={"class": "kicker"})
    kicker.string = copy["kicker"]
    title = soup.new_tag("h3")
    title.string = copy["title"]
    body = soup.new_tag("p")
    body.string = copy["body"]
    link_wrap = soup.new_tag("p")
    link = soup.new_tag(
        "a",
        attrs={
            "data-analytics-event": "golf_club_click",
            "href": OFFICIAL_URL,
            "rel": "nofollow noopener noreferrer",
            "target": "_blank",
        },
    )
    link.string = copy["link"]
    link_wrap.append(link)
    article.extend([kicker, title, body, link_wrap])
    return article


def update_modified_date(soup: BeautifulSoup) -> None:
    for node in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(node.string or "")
        except json.JSONDecodeError:
            continue
        changed = False
        candidates = data.get("@graph", []) if isinstance(data, dict) else []
        for item in candidates:
            item_type = item.get("@type") if isinstance(item, dict) else None
            if item_type == "WebPage" or (
                isinstance(item_type, list) and "WebPage" in item_type
            ):
                item["dateModified"] = DATE
                changed = True
        if changed:
            node.string = json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def patch_page(path: Path, copy: dict[str, str]) -> None:
    soup = parse(path.read_text(encoding="utf-8"))
    grid = soup.select_one(".course-grid")
    if grid is None:
        raise RuntimeError(f"Golf course grid not found in {path}")

    for card in list(grid.select("article.course-card")):
        if "monacilla" in card.get_text(" ", strip=True).lower():
            card.decompose()

    cards = grid.select("article.course-card")
    rompido = next(
        (card for card in cards if "rompido" in card.get_text(" ", strip=True).lower()),
        None,
    )
    if rompido is None:
        raise RuntimeError(f"Golf El Rompido card not found in {path}")
    rompido.insert_after(build_card(soup, copy))

    for old_style in soup.find_all("style", id=STYLE_ID):
        old_style.decompose()
    style = soup.new_tag("style", id=STYLE_ID)
    style.string = CSS
    soup.head.append(style)
    update_modified_date(soup)
    write_html(path, soup)

    check = parse(path.read_text(encoding="utf-8"))
    course_cards = check.select(".course-grid article.course-card")
    monacilla_cards = [
        card for card in course_cards if "monacilla" in card.get_text(" ", strip=True).lower()
    ]
    if len(course_cards) != 5 or len(monacilla_cards) != 1:
        raise RuntimeError(f"Unexpected golf-card count in {path}")
    if len(check.select(f"style#{STYLE_ID}")) != 1:
        raise RuntimeError(f"Unexpected layout-style count in {path}")
    if not monacilla_cards[0].select_one(f'a[href="{OFFICIAL_URL}"]'):
        raise RuntimeError(f"Official La Monacilla link missing in {path}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: v79-add-la-monacilla.py ROOT")
    root = Path(sys.argv[1]).resolve()
    for relative, copy in PAGES.items():
        path = root / relative
        if not path.is_file():
            raise RuntimeError(f"Missing production page: {path}")
        patch_page(path, copy)
        print(f"Updated {relative}")


if __name__ == "__main__":
    main()
