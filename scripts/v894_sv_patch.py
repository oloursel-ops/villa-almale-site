from pathlib import Path
import sys

if len(sys.argv) != 3:
    raise SystemExit('usage: v894_sv_patch.py INDEX_HTML AUDIENCE_JS')

html_path = Path(sys.argv[1])
audience_path = Path(sys.argv[2])
s = html_path.read_text(encoding='utf-8')


def repl(old: str, new: str, expected: int, label: str) -> None:
    global s
    count = s.count(old)
    if count != expected:
        raise SystemExit(f'{label}: expected {expected}, found {count}')
    s = s.replace(old, new)


if '<meta content="8.4" name="villa-release"/>' in s:
    repl('<meta content="8.4" name="villa-release"/>', '<meta content="8.9.4" name="villa-release"/>', 1, 'release')
elif '<meta content="8.4" name="villa-release">' in s:
    repl('<meta content="8.4" name="villa-release">', '<meta content="8.9.4" name="villa-release">', 1, 'release')
else:
    raise SystemExit('release: expected V8.4 marker not found')

repl('"dateModified":"2026-08-08"', '"dateModified":"2026-08-11"', 1, 'dateModified')
repl('/assets/js/audience.js?v=8.4.2', '/assets/js/audience.js?v=8.9.4', 1, 'audience cache bust')
repl('Pris per person baserat på 7 nätter för 6 vuxna.', 'Pris per person beräknat på 7 nätter för 6 vuxna.', 2, 'price wording')

old_h1 = '<h1>En privat villa för golf, kustliv och tid tillsammans.</h1>'
new_h1 = '<h1>En privat villa för golf, kustliv och tid tillsammans.</h1>\n<p class="sv-hero-price"><strong>Från 371 € per person för 7 nätter</strong><span>Pris per person beräknat på 7 nätter för 6 vuxna.</span></p>'
repl(old_h1, new_h1, 1, 'hero price insertion')

repl(
    'Fem sovrum och privat pool. Ingången till Golf Nuevo Portil vid det 18:e hålet ligger precis intill huset; klubbhuset nås på cirka 5 minuter till fots.',
    'Fem sovrum och en privat pool. En ingång till Golf Nuevo Portil vid hål 18 ligger precis intill huset, och klubbhuset ligger cirka fem minuters promenad bort.',
    1,
    'hero lead',
)
repl('Golf till fots', 'Golf på gångavstånd', 1, 'golf fact')
repl('Se lediga datum och pris →', 'Se lediga datum och totalpris →', 2, 'booking CTA')

marker = '</head>'
if s.count(marker) != 1:
    raise SystemExit('head marker unexpected')
style = '''<style id="villa-almale-v894-sv-hero-price">
html[lang="sv"] .sv-hero-price{display:inline-flex;flex-direction:column;gap:.12rem;margin:.8rem 0 .7rem;padding:.55rem .78rem .58rem;border-left:2px solid #f1cd8f;background:rgba(12,48,43,.48);border-radius:0 10px 10px 0;color:#fff}
html[lang="sv"] .sv-hero-price strong{font-family:Georgia,"Times New Roman",serif;font-size:clamp(1.04rem,1.65vw,1.25rem);font-weight:600;line-height:1.2}
html[lang="sv"] .sv-hero-price span{font-size:.76rem;line-height:1.35;color:rgba(255,255,255,.84)}
@media(max-width:720px){html[lang="sv"] .sv-hero-price{margin:.65rem 0 .62rem;padding:.48rem .68rem .5rem}html[lang="sv"] .sv-hero-price strong{font-size:1rem}html[lang="sv"] .sv-hero-price span{font-size:.72rem}}
</style>'''
s = s.replace(marker, style + marker)
html_path.write_text(s, encoding='utf-8')

js = audience_path.read_text(encoding='utf-8')
old = 'Nödvändiga cookies förblir aktiva. Du kan endast tillåta besöksmätning (Google Analytics), eller alla cookies för att även inkludera Metas annonsmätning.'
new = 'Nödvändiga cookies är alltid aktiva. Du kan välja enbart besöksmätning (Google Analytics) eller godkänna alla cookies, inklusive Metas annonsmätning.'
count = js.count(old)
if count != 1:
    raise SystemExit(f'Swedish consent copy: expected 1, found {count}')
js = js.replace(old, new)
audience_path.write_text(js, encoding='utf-8')
