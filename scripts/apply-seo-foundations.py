#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("live")
LASTMOD = "2026-07-28"
BASE = "https://villanuevoportil.com"
HERO = "/assets/images/current/hero-villa-piscine-jardin.webp"
HERO_768 = "/assets/images/current/hero-villa-piscine-jardin-768.webp"
HERO_1280 = "/assets/images/current/hero-villa-piscine-jardin-1280.webp"
AIRBNB = "https://www.airbnb.com/rooms/880876896761619102"
VRBO = "https://www.vrbo.com/8160054ha"

SEO_PAGES: dict[str, dict[str, Any]] = {
    "index.html": {
        "canonical": f"{BASE}/",
        "lang": "fr",
        "home": True,
        "alternates": {"fr": f"{BASE}/", "en": f"{BASE}/en/", "es": f"{BASE}/es/", "x-default": f"{BASE}/"},
    },
    "en/index.html": {
        "canonical": f"{BASE}/en/",
        "lang": "en",
        "home": True,
        "alternates": {"fr": f"{BASE}/", "en": f"{BASE}/en/", "es": f"{BASE}/es/", "x-default": f"{BASE}/"},
    },
    "es/index.html": {
        "canonical": f"{BASE}/es/",
        "lang": "es",
        "home": True,
        "alternates": {"fr": f"{BASE}/", "en": f"{BASE}/en/", "es": f"{BASE}/es/", "x-default": f"{BASE}/"},
    },
    "villa-nuevo-portil/index.html": {
        "canonical": f"{BASE}/villa-nuevo-portil/",
        "lang": "fr",
        "alternates": {"fr": f"{BASE}/villa-nuevo-portil/", "en": f"{BASE}/en/holiday-villa-nuevo-portil/", "es": f"{BASE}/es/alquiler-vacacional-nuevo-portil/", "x-default": f"{BASE}/en/holiday-villa-nuevo-portil/"},
    },
    "en/holiday-villa-nuevo-portil/index.html": {
        "canonical": f"{BASE}/en/holiday-villa-nuevo-portil/",
        "lang": "en",
        "alternates": {"fr": f"{BASE}/villa-nuevo-portil/", "en": f"{BASE}/en/holiday-villa-nuevo-portil/", "es": f"{BASE}/es/alquiler-vacacional-nuevo-portil/", "x-default": f"{BASE}/en/holiday-villa-nuevo-portil/"},
    },
    "es/alquiler-vacacional-nuevo-portil/index.html": {
        "canonical": f"{BASE}/es/alquiler-vacacional-nuevo-portil/",
        "lang": "es",
        "alternates": {"fr": f"{BASE}/villa-nuevo-portil/", "en": f"{BASE}/en/holiday-villa-nuevo-portil/", "es": f"{BASE}/es/alquiler-vacacional-nuevo-portil/", "x-default": f"{BASE}/en/holiday-villa-nuevo-portil/"},
    },
    "off-season/index.html": {
        "canonical": f"{BASE}/off-season/",
        "lang": "en",
        "alternates": {"en": f"{BASE}/off-season/", "fr": f"{BASE}/off-season/fr/", "es": f"{BASE}/off-season/es/", "x-default": f"{BASE}/off-season/"},
    },
    "off-season/fr/index.html": {
        "canonical": f"{BASE}/off-season/fr/",
        "lang": "fr",
        "alternates": {"en": f"{BASE}/off-season/", "fr": f"{BASE}/off-season/fr/", "es": f"{BASE}/off-season/es/", "x-default": f"{BASE}/off-season/"},
    },
    "off-season/es/index.html": {
        "canonical": f"{BASE}/off-season/es/",
        "lang": "es",
        "alternates": {"en": f"{BASE}/off-season/", "fr": f"{BASE}/off-season/fr/", "es": f"{BASE}/off-season/es/", "x-default": f"{BASE}/off-season/"},
    },
}

NOINDEX_PAGES = [
    "reservation.html",
    "en/reservation.html",
    "es/reservation.html",
    "legal.html",
    "privacy.html",
    "cookies.html",
    "booking-terms.html",
    "guide/index.html",
    "guide/fr/index.html",
    "guide/en/index.html",
    "guide/es/index.html",
]

FAQ_ANSWERS = {
    "fr": "La maison n’est pas entièrement climatisée. Trois climatiseurs mobiles équipent la suite principale, le salon et l’espace couchage du rez-de-chaussée. Deux chambres avec lits simples disposent de ventilateurs de plafond.",
    "en": "The house is not fully air-conditioned. Three portable air-conditioning units serve the main suite, living room and ground-floor sleeping area. Two twin bedrooms have ceiling fans.",
    "es": "La casa no está climatizada por completo. Hay tres equipos portátiles en la suite principal, el salón y la zona de dormitorio de la planta baja. Dos dormitorios con camas individuales tienen ventiladores de techo.",
}

HTACCESS = r'''DirectoryIndex index.html
Options -Indexes

<IfModule mod_rewrite.c>
 RewriteEngine On

 # One secure canonical host.
 RewriteCond %{HTTPS} !=on [OR]
 RewriteCond %{HTTP_HOST} !^villanuevoportil\.com$ [NC]
 RewriteRule ^ https://villanuevoportil.com%{REQUEST_URI} [R=301,L,NE]

 # Remove explicit index.html from all public directory URLs.
 RewriteCond %{THE_REQUEST} \s/+(.*/)?index\.html(?:[?\s]) [NC]
 RewriteRule ^(.*/)?index\.html$ /$1 [R=301,L,NE]

 # Deny deployment archives, diagnostics and private documents left in the web root.
 RewriteRule ^(?:_DEPLOY_[^/]*|web_upload|__MACOSX|content)(?:/|$) - [F,L,NC]
 RewriteRule ^(?:README[^/]*|AUDIENCE-ACTIVATION-CHECKLIST\.md|test-ownerrez[^/]*\.html|ownerrez-diagnostic[^/]*|ownerrez-calendar-[^/]*\.html)$ - [F,L,NC]
 RewriteRule \.(?:zip|docx|md|pdf)$ - [F,L,NC]
</IfModule>

<IfModule mod_headers.c>
 Header always set X-Content-Type-Options "nosniff"
 Header always set Referrer-Policy "strict-origin-when-cross-origin"
 Header always set Permissions-Policy "camera=(), microphone=(), geolocation=()"
 Header always set Strict-Transport-Security "max-age=31536000"
 <FilesMatch "\.(?:webp|avif|jpg|jpeg|png|svg|ico)$">
  Header set Cache-Control "public, max-age=31536000, immutable"
 </FilesMatch>
 <FilesMatch "\.(?:css|js)$">
  Header set Cache-Control "public, max-age=2592000"
 </FilesMatch>
 <FilesMatch "\.(?:html?|xml|txt)$">
  Header set Cache-Control "public, max-age=0, must-revalidate"
 </FilesMatch>
</IfModule>

<IfModule mod_brotli.c>
 AddOutputFilterByType BROTLI_COMPRESS text/html text/plain text/css application/javascript application/json application/ld+json application/xml image/svg+xml
</IfModule>
<IfModule mod_deflate.c>
 AddOutputFilterByType DEFLATE text/html text/plain text/css application/javascript application/json application/ld+json application/xml image/svg+xml
</IfModule>

<IfModule mod_expires.c>
 ExpiresActive On
 ExpiresByType image/webp "access plus 1 year"
 ExpiresByType image/avif "access plus 1 year"
 ExpiresByType image/svg+xml "access plus 1 year"
 ExpiresByType text/css "access plus 30 days"
 ExpiresByType application/javascript "access plus 30 days"
 ExpiresByType text/html "access plus 0 seconds"
</IfModule>
'''

ROBOTS = f'''User-agent: *
Allow: /
Disallow: /_DEPLOY_
Disallow: /web_upload/
Disallow: /__MACOSX/
Disallow: /content/
Disallow: /test-ownerrez
Disallow: /ownerrez-diagnostic
Disallow: /ownerrez-calendar-
Disallow: /*.zip$
Disallow: /*.docx$
Disallow: /*.pdf$

Sitemap: {BASE}/sitemap.xml
'''


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def extract_attr(tag: str, name: str) -> str | None:
    match = re.search(rf'\b{name}\s*=\s*["\']([^"\']+)["\']', tag, flags=re.I)
    return match.group(1) if match else None


def link_tags(text: str) -> list[str]:
    return re.findall(r'<link\b[^>]*>', text, flags=re.I)


def validate_head(text: str, path: str, data: dict[str, Any]) -> None:
    if len(re.findall(r'<h1\b', text, flags=re.I)) != 1:
        raise RuntimeError(f"{path}: expected exactly one H1")
    if not re.search(r'<title>\s*[^<]{10,}\s*</title>', text, flags=re.I):
        raise RuntimeError(f"{path}: missing or empty title")
    if not re.search(r'<meta\b(?=[^>]*\bname=["\']description["\'])[^>]*\bcontent=["\'][^"\']{60,}["\'][^>]*>', text, flags=re.I):
        if not re.search(r'<meta\b(?=[^>]*\bcontent=["\'][^"\']{60,}["\'])(?=[^>]*\bname=["\']description["\'])[^>]*>', text, flags=re.I):
            raise RuntimeError(f"{path}: missing useful meta description")
    canonical = [extract_attr(tag, "href") for tag in link_tags(text) if (extract_attr(tag, "rel") or "").lower() == "canonical"]
    if canonical != [data["canonical"]]:
        raise RuntimeError(f"{path}: canonical mismatch: {canonical!r}")
    found_alternates: dict[str, str] = {}
    for tag in link_tags(text):
        if (extract_attr(tag, "rel") or "").lower() != "alternate":
            continue
        hreflang = extract_attr(tag, "hreflang")
        href = extract_attr(tag, "href")
        if hreflang and href:
            found_alternates[hreflang] = href
    if found_alternates != data["alternates"]:
        raise RuntimeError(f"{path}: hreflang mismatch: {found_alternates!r}")
    for token in ("og:title", "og:description", "og:image", "twitter:card", "twitter:title", "twitter:description", "twitter:image"):
        if token not in text:
            raise RuntimeError(f"{path}: missing social metadata {token}")


def modify_json_node(node: Any, lang: str) -> None:
    if isinstance(node, dict):
        node_type = node.get("@type")
        types = {node_type} if isinstance(node_type, str) else set(node_type or [])
        if "WebPage" in types:
            node["dateModified"] = LASTMOD
        if "Accommodation" in types:
            amenities = node.setdefault("amenityFeature", [])
            existing = {item.get("name") for item in amenities if isinstance(item, dict)}
            for name in (
                "Three portable air-conditioning units in selected rooms",
                "Ceiling fans in two twin bedrooms",
            ):
                if name not in existing:
                    amenities.append({"@type": "LocationFeatureSpecification", "name": name, "value": True})
            same_as = node.setdefault("sameAs", [])
            for url in (AIRBNB, VRBO):
                if url not in same_as:
                    same_as.append(url)
        if "FAQPage" in types:
            for question in node.get("mainEntity", []):
                if not isinstance(question, dict):
                    continue
                name = str(question.get("name", "")).lower()
                if any(key in name for key in ("climatisation", "air conditioning", "aire acondicionado")):
                    answer = question.setdefault("acceptedAnswer", {"@type": "Answer"})
                    answer["text"] = FAQ_ANSWERS[lang]
        for value in node.values():
            modify_json_node(value, lang)
    elif isinstance(node, list):
        for value in node:
            modify_json_node(value, lang)


def update_json_ld(text: str, lang: str, path: str) -> str:
    scripts = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal scripts
        raw = match.group(1).strip()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"{path}: invalid JSON-LD: {exc}") from exc
        modify_json_node(payload, lang)
        scripts += 1
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        return f'<script type="application/ld+json">{encoded}</script>'

    updated = re.sub(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        repl,
        text,
        flags=re.I | re.S,
    )
    if scripts < 1:
        raise RuntimeError(f"{path}: no JSON-LD block found")
    return updated


def ensure_preconnect(text: str) -> str:
    if 'href="https://app.ownerrez.com"' in text or "href='https://app.ownerrez.com'" in text:
        return text
    tag = '<link rel="preconnect" href="https://app.ownerrez.com" crossorigin/>'
    if "</head>" not in text:
        raise RuntimeError("closing head not found")
    return text.replace("</head>", tag + "</head>", 1)


def ensure_responsive_hero(text: str, path: str) -> str:
    hero_pattern = r'<img\b(?=[^>]*\bsrc=["\'][^"\']*hero-villa-piscine-jardin(?:-1280)?\.webp["\'])[^>]*>'
    match = re.search(hero_pattern, text, flags=re.I)
    if not match:
        raise RuntimeError(f"{path}: primary hero image tag not found")
    tag = match.group(0)
    tag = re.sub(r'\s+srcset=["\'][^"\']*["\']', "", tag, flags=re.I)
    tag = re.sub(r'\s+sizes=["\'][^"\']*["\']', "", tag, flags=re.I)
    tag = re.sub(
        r'\bsrc=["\'][^"\']*hero-villa-piscine-jardin(?:-1280)?\.webp["\']',
        f'src="{HERO_1280}"',
        tag,
        count=1,
        flags=re.I,
    )
    ending = "/>" if tag.rstrip().endswith("/>") else ">"
    core = tag.rstrip()[:-len(ending)].rstrip()
    srcset = f'{HERO_768} 768w, {HERO_1280} 1280w, {HERO} 1920w'
    tag = f'{core} srcset="{srcset}" sizes="100vw"{ending}'
    text = text[: match.start()] + tag + text[match.end() :]

    preload = (
        f'<link rel="preload" as="image" href="{HERO_1280}" '
        f'imagesrcset="{srcset}" imagesizes="100vw" type="image/webp" fetchpriority="high"/>'
    )
    preload_pattern = r'<link\b(?=[^>]*\brel=["\']preload["\'])(?=[^>]*hero-villa-piscine-jardin[^>]*>)[^>]*>'
    if re.search(preload_pattern, text, flags=re.I):
        text = re.sub(preload_pattern, preload, text, count=1, flags=re.I)
    elif "</head>" in text:
        text = text.replace("</head>", preload + "</head>", 1)
    else:
        raise RuntimeError(f"{path}: closing head not found")
    return text


def ensure_noindex(text: str, path: str) -> str:
    tag = '<meta name="robots" content="noindex,follow,noarchive"/>'
    pattern = r'<meta\b(?=[^>]*\bname=["\']robots["\'])[^>]*>'
    if re.search(pattern, text, flags=re.I):
        return re.sub(pattern, tag, text, count=1, flags=re.I)
    if "</head>" not in text:
        raise RuntimeError(f"{path}: closing head not found")
    return text.replace("</head>", tag + "</head>", 1)


def build_sitemap() -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for data in SEO_PAGES.values():
        lines.append("  <url>")
        lines.append(f'    <loc>{data["canonical"]}</loc>')
        lines.append(f"    <lastmod>{LASTMOD}</lastmod>")
        for lang, href in data["alternates"].items():
            lines.append(f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{href}"/>')
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


write(ROOT / ".htaccess", HTACCESS)
write(ROOT / "robots.txt", ROBOTS)
write(ROOT / "sitemap.xml", build_sitemap())

for relative, data in SEO_PAGES.items():
    path = ROOT / relative
    if not path.is_file():
        raise RuntimeError(f"missing SEO page: {relative}")
    text = read(path)
    validate_head(text, relative, data)
    text = update_json_ld(text, data["lang"], relative)
    if data.get("home"):
        text = ensure_preconnect(text)
        text = ensure_responsive_hero(text, relative)
    write(path, text)

for relative in NOINDEX_PAGES:
    path = ROOT / relative
    if not path.is_file():
        raise RuntimeError(f"missing utility page: {relative}")
    write(path, ensure_noindex(read(path), relative))

# Final invariants.
sitemap = read(ROOT / "sitemap.xml")
if sitemap.count("<loc>") != len(SEO_PAGES):
    raise RuntimeError("sitemap URL count mismatch")
if "index.html" in sitemap:
    raise RuntimeError("sitemap contains a duplicate index.html URL")
for relative in NOINDEX_PAGES:
    if "noindex,follow,noarchive" not in read(ROOT / relative):
        raise RuntimeError(f"{relative}: noindex was not applied")
for relative, data in SEO_PAGES.items():
    text = read(ROOT / relative)
    if LASTMOD not in text:
        raise RuntimeError(f"{relative}: dateModified was not updated")
    if "Three portable air-conditioning units in selected rooms" not in text:
        raise RuntimeError(f"{relative}: AC structured-data amenity missing")
    if data.get("home") and "hero-villa-piscine-jardin-768.webp 768w" not in text:
        raise RuntimeError(f"{relative}: responsive hero image missing")

print("SEO foundations updated and validated successfully.")
