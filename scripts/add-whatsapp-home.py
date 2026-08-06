#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

MARKER = "villa-almale-whatsapp-float-v1"
CANONICAL_MARKER = "site-floating-action--whatsapp"
PHONE = "33687174067"

MESSAGES = {
    "fr": "Bonjour, je souhaite obtenir des informations sur les disponibilités de Villa Almale.",
    "en": "Hello, I would like information about Villa Almale availability.",
    "es": "Hola, me gustaría recibir información sobre la disponibilidad de Villa Almale.",
}

LABELS = {
    "fr": "Contacter Villa Almale sur WhatsApp",
    "en": "Contact Villa Almale on WhatsApp",
    "es": "Contactar con Villa Almale por WhatsApp",
}

URLS = {
    lang: f"https://wa.me/{PHONE}?text={quote(message, safe='')}"
    for lang, message in MESSAGES.items()
}

CSS_TEMPLATE = r'''
<style id="__MARKER__-style">
/* __MARKER__ */
.__MARKER__{
  position:fixed;
  right:max(22px,env(safe-area-inset-right));
  bottom:max(24px,env(safe-area-inset-bottom));
  z-index:2147483000;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap:10px;
  min-height:54px;
  padding:0 19px 0 15px;
  border:1px solid rgba(224,179,104,.72);
  border-radius:999px;
  background:rgba(13,70,72,.96);
  color:#fff;
  box-shadow:0 12px 34px rgba(0,31,34,.30);
  font:700 15px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  letter-spacing:.01em;
  text-decoration:none;
  -webkit-backdrop-filter:blur(10px);
  backdrop-filter:blur(10px);
  -webkit-tap-highlight-color:transparent;
  transition:transform .18s ease,box-shadow .18s ease,background .18s ease;
}
.__MARKER__:hover,
.__MARKER__:focus-visible{
  transform:translateY(-2px);
  background:#0a3d40;
  box-shadow:0 16px 40px rgba(0,31,34,.36);
  outline:2px solid rgba(255,255,255,.85);
  outline-offset:3px;
}
.__MARKER__ svg{width:28px;height:28px;display:block;fill:currentColor;flex:0 0 28px}
.__MARKER__ span{white-space:nowrap}
@media(max-width:760px){
  .__MARKER__{
    right:max(15px,env(safe-area-inset-right));
    bottom:calc(92px + env(safe-area-inset-bottom));
    width:56px;
    height:56px;
    min-height:56px;
    padding:0;
    border-radius:50%;
  }
  .__MARKER__ span{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
}
@media print{.__MARKER__{display:none!important}}
@media(prefers-reduced-motion:reduce){.__MARKER__{transition:none}}
</style>
'''.strip()

HTML_TEMPLATE = r'''
<a class="__MARKER__" data-whatsapp-contact="villa-almale" href="__FR_URL__" target="_blank" rel="noopener noreferrer" aria-label="Contacter Villa Almale sur WhatsApp" title="WhatsApp">
  <svg viewBox="0 0 32 32" aria-hidden="true" focusable="false">
    <path d="M19.11 17.2c-.26-.13-1.54-.76-1.78-.85-.24-.09-.41-.13-.59.13-.17.26-.67.85-.82 1.02-.15.17-.3.2-.56.07-.26-.13-1.09-.4-2.08-1.29-.77-.68-1.29-1.53-1.44-1.79-.15-.26-.02-.4.11-.53.12-.12.26-.3.39-.46.13-.15.17-.26.26-.43.09-.17.04-.33-.02-.46-.07-.13-.59-1.42-.8-1.94-.21-.51-.43-.44-.59-.45h-.5c-.17 0-.46.07-.69.33-.24.26-.91.89-.91 2.18 0 1.28.94 2.52 1.07 2.69.13.17 1.84 2.81 4.46 3.94.62.27 1.11.43 1.49.55.63.2 1.2.17 1.65.1.5-.07 1.54-.63 1.76-1.24.22-.61.22-1.13.15-1.24-.06-.11-.24-.17-.5-.3z"/>
    <path d="M16.04 3.2A12.55 12.55 0 0 0 5.18 22.03L3.2 28.8l6.94-1.82a12.56 12.56 0 1 0 5.9-23.78zm0 22.83c-2.05 0-4.05-.55-5.79-1.59l-.41-.24-4.12 1.08 1.1-4.01-.27-.42a10.27 10.27 0 1 1 9.49 5.18z"/>
  </svg>
  <span>WhatsApp</span>
</a>
<script id="__MARKER__-script">
(() => {
  'use strict';
  const button = document.querySelector('.__MARKER__');
  if (!button) return;
  const links = __LINKS_JSON__;
  const labels = __LABELS_JSON__;
  const update = () => {
    const declared = (document.documentElement.lang || '').toLowerCase().slice(0,2);
    const active = document.querySelector('[data-lang].active,[data-lang][aria-current="true"],.lang-switch .active');
    const selected = ((active && active.getAttribute('data-lang')) || declared || 'fr').toLowerCase().slice(0,2);
    const lang = links[selected] ? selected : 'fr';
    button.href = links[lang];
    button.setAttribute('aria-label', labels[lang]);
  };
  update();
  new MutationObserver(update).observe(document.documentElement, {attributes:true,attributeFilter:['lang']});
  document.addEventListener('click', event => {
    if (event.target.closest('[data-lang],.lang-switch button,.langs button')) setTimeout(update,0);
  });
})();
</script>
'''.strip()

CSS = CSS_TEMPLATE.replace("__MARKER__", MARKER)
HTML = (
    HTML_TEMPLATE
    .replace("__MARKER__", MARKER)
    .replace("__FR_URL__", URLS["fr"])
    .replace("__LINKS_JSON__", json.dumps(URLS, ensure_ascii=False))
    .replace("__LABELS_JSON__", json.dumps(LABELS, ensure_ascii=False))
)


LEGACY_BLOCKS = (
    re.compile(
        rf'<style\b[^>]*\bid=["\']{re.escape(MARKER)}-style["\'][^>]*>.*?</style\s*>',
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        rf'<a\b[^>]*\bclass=["\'][^"\']*\b{re.escape(MARKER)}\b[^"\']*["\'][^>]*>.*?</a\s*>',
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        rf'<script\b[^>]*\bid=["\']{re.escape(MARKER)}-script["\'][^>]*>.*?</script\s*>',
        re.IGNORECASE | re.DOTALL,
    ),
)


def remove_legacy_button(text: str) -> tuple[str, int]:
    removed = 0
    for pattern in LEGACY_BLOCKS:
        text, count = pattern.subn("", text)
        removed += count
    return text, removed


def patch(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    # The V7.4 shared action bar supersedes the former standalone WhatsApp
    # button. When the canonical action exists, make this older workflow a
    # cleanup operation so rerunning it can never recreate the duplicate.
    if CANONICAL_MARKER in text:
        text, removed = remove_legacy_button(text)
        if MARKER in text:
            raise SystemExit("Legacy WhatsApp fragments remain after cleanup.")
        if text.count(f'class="site-floating-action {CANONICAL_MARKER}"') != 1:
            raise SystemExit("Expected exactly one canonical WhatsApp action.")
        path.write_text(text, encoding="utf-8")
        print(f"Removed {removed} legacy WhatsApp fragment(s); canonical action retained.")
        return

    if MARKER in text:
        print("WhatsApp marker already present; no duplicate inserted.")
        return
    lower = text.lower()
    if "</head>" not in lower or "</body>" not in lower:
        raise SystemExit("Expected closing </head> and </body> tags were not found.")

    head_pos = lower.rfind("</head>")
    text = text[:head_pos] + CSS + "\n" + text[head_pos:]

    lower = text.lower()
    body_pos = lower.rfind("</body>")
    text = text[:body_pos] + HTML + "\n" + text[body_pos:]

    path.write_text(text, encoding="utf-8")
    print(f"Inserted {MARKER} into {path}.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: add-whatsapp-home.py PATH_TO_INDEX_HTML")
    patch(Path(sys.argv[1]))
