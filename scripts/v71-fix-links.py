#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('live')
PAGES = [
    ROOT / 'off-season/index.html',
    ROOT / 'off-season/fr/index.html',
    ROOT / 'off-season/es/index.html',
]

OLD_ROMPIDO = 'https://open.imaster.golf/en/rompido/disponibilidad'
NEW_ROMPIDO = 'https://www.teetimesbooking.com/club/golf-el-rompido'
OLD_TRANSFER = 'https://taximarrompido.com/contacto'
NEW_TRANSFER = 'https://taximarrompido.com/'

for path in PAGES:
    if not path.is_file():
        raise RuntimeError(f'Missing page: {path}')
    text = path.read_text(encoding='utf-8')
    text = text.replace(OLD_ROMPIDO, NEW_ROMPIDO)
    text = text.replace(OLD_TRANSFER, NEW_TRANSFER)

    soup = BeautifulSoup(text, 'html.parser')
    links = soup.find_all('a', href=True)
    if not links:
        raise RuntimeError(f'No links found in {path}')

    for link in links:
        link['target'] = '_blank'
        rel = set(link.get('rel', []))
        rel.update({'noopener', 'noreferrer'})
        if str(link['href']).startswith(('http://', 'https://')):
            rel.add('nofollow')
        link['rel'] = sorted(rel)

    output = '<!DOCTYPE html>\n' + str(soup).split('<!DOCTYPE html>', 1)[-1].lstrip()

    if OLD_ROMPIDO in output or OLD_TRANSFER in output:
        raise RuntimeError(f'Stale URL remains in {path}')
    if NEW_ROMPIDO not in output or NEW_TRANSFER not in output:
        raise RuntimeError(f'Corrected URLs missing in {path}')

    check = BeautifulSoup(output, 'html.parser')
    for link in check.find_all('a', href=True):
        if link.get('target') != '_blank':
            raise RuntimeError(f'Link without target blank in {path}: {link.get("href")}')
        rel = set(link.get('rel', []))
        if not {'noopener', 'noreferrer'}.issubset(rel):
            raise RuntimeError(f'Unsafe new-window link in {path}: {link.get("href")}')

    for block in check.find_all('script', attrs={'type': 'application/ld+json'}):
        json.loads(block.string or block.get_text())

    path.write_text(output, encoding='utf-8')

print('Villa Almale V7.1 link correction validated successfully.')
