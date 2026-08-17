#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from bs4 import BeautifulSoup

NEW_URL = "https://open.teeone.golf/es/rompido/disponibilidad"
OLD_HOSTS = (
    "www.teetimesbooking.com/club/golf-el-rompido",
    "teetimesbooking.com/club/golf-el-rompido",
)


def is_el_rompido_booking(href: str) -> bool:
    href_l = (href or "").lower()
    return any(host in href_l for host in OLD_HOSTS) or (
        "open.teeone.golf" in href_l and "/rompido/disponibilidad" in href_l
    )


def patch(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(text, "html.parser")
    matches = []
    for a in soup.find_all("a", href=True):
        if is_el_rompido_booking(a.get("href", "")):
            matches.append(a)

    if not matches:
        raise RuntimeError(f"No Golf El Rompido booking link found in {path}")

    for a in matches:
        a["href"] = NEW_URL
        a["target"] = "_blank"
        rel = set(a.get("rel", []))
        rel.update(["noopener", "noreferrer"])
        a["rel"] = sorted(rel)
        a["data-golf-el-rompido-booking"] = "direct"

    out = str(soup)
    if not out.lstrip().lower().startswith("<!doctype"):
        out = "<!DOCTYPE html>\n" + out
    path.write_text(out, encoding="utf-8")

    check = BeautifulSoup(out, "html.parser")
    updated = check.select('a[data-golf-el-rompido-booking="direct"]')
    if len(updated) != len(matches):
        raise RuntimeError(f"Unexpected number of updated links in {path}")
    for a in updated:
        assert a.get("href") == NEW_URL
        assert a.get("target") == "_blank"
        rel = set(a.get("rel", []))
        assert {"noopener", "noreferrer"}.issubset(rel)
    if "teetimesbooking.com/club/golf-el-rompido" in out.lower():
        raise RuntimeError(f"Old El Rompido booking URL still present in {path}")
    print(f"Updated {len(updated)} Golf El Rompido booking link(s) in {path} -> {NEW_URL}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: update-el-rompido-direct-booking.py PATH_TO_HTML")
    patch(Path(sys.argv[1]))
