#!/usr/bin/env bash
set -euo pipefail

: "${DEPLOY_SCHEME:?Missing INFOMANIAK_SCHEME}"
: "${DEPLOY_HOST:?Missing INFOMANIAK_HOST}"
: "${DEPLOY_PORT:?Missing INFOMANIAK_PORT}"
: "${DEPLOY_USER:?Missing INFOMANIAK_USER}"
: "${DEPLOY_PASSWORD:?Missing INFOMANIAK_PASSWORD}"
: "${DEPLOY_PATH:?Missing INFOMANIAK_PATH}"
test "$DEPLOY_PATH" = "sites/PageWebbasique1"
case "$DEPLOY_SCHEME" in
  sftp) EXTRA_SETTINGS="set sftp:auto-confirm yes;" ;;
  ftp) EXTRA_SETTINGS="set ftp:ssl-allow no; set ftp:passive-mode yes;" ;;
  ftps) EXTRA_SETTINGS="set ftp:ssl-force yes; set ftp:ssl-protect-data yes; set ssl:verify-certificate yes; set ftp:passive-mode yes;" ;;
  *) echo "Unsupported scheme"; exit 1 ;;
esac

files=(
  index.html
  en/index.html
  es/index.html
  off-season/index.html
  off-season/fr/index.html
  off-season/es/index.html
  off-season/sv/index.html
)

mkdir -p work/en work/es work/off-season/fr work/off-season/es work/off-season/sv
lftp -c "
  set cmd:fail-exit yes;
  set net:max-retries 2;
  set net:timeout 30;
  $EXTRA_SETTINGS
  open -p $DEPLOY_PORT -u \"$DEPLOY_USER\",\"$DEPLOY_PASSWORD\" $DEPLOY_SCHEME://$DEPLOY_HOST;
  get \"$DEPLOY_PATH/index.html\" -o work/index.html;
  get \"$DEPLOY_PATH/en/index.html\" -o work/en/index.html;
  get \"$DEPLOY_PATH/es/index.html\" -o work/es/index.html;
  get \"$DEPLOY_PATH/off-season/index.html\" -o work/off-season/index.html;
  get \"$DEPLOY_PATH/off-season/fr/index.html\" -o work/off-season/fr/index.html;
  get \"$DEPLOY_PATH/off-season/es/index.html\" -o work/off-season/es/index.html;
  get \"$DEPLOY_PATH/off-season/sv/index.html\" -o work/off-season/sv/index.html;
  bye
"
cat > expected-v85.sha256 <<'EOF'
664961f35033430201ffef7cdcc8ebad76cb15a2a1671e5bbedf9bb42242f661  work/index.html
54aede6307c3d6b4e3b470c65737887f72ce8c0de88c6cb819f3e748a3e3ca69  work/en/index.html
ac4636ed9531eeea7024671c55ed8164446fcf8981bf886b073fa938dc7c2761  work/es/index.html
5176dfd151249c47b5a008267bc181e8622846b10b18888bfdd1be8de1e8bd64  work/off-season/index.html
d5a30d0725fda21cafe26f59e3746ccbe9c40c68a7251d526494dac316e70960  work/off-season/fr/index.html
9c36a9a58c5708cf44cf6032e3593a1d6c3fe0a583cc729220cbd225f8b9de07  work/off-season/es/index.html
1d83cc0a09fa13152cdd60078258a12531a309517c1c12b19e7ab37828539142  work/off-season/sv/index.html
EOF
sha256sum -c expected-v85.sha256
cp -a work backup-before-v86

python3 apply_v86_dedupe.py work
cat > expected-v86.sha256 <<'EOF'
25d0ee6df2503e3137e290326e55df5ab1530306401a41448fbaf0a27d581978  work/index.html
b7df5930a6f151b20b02762a89b87b59d745b963c4fe7ad054c08e1244131ce5  work/en/index.html
f878c5f8b5e3d48d27d1f08fbaca52dfd5cfa693cfdf93aaa8612baf98007983  work/es/index.html
89f6fd58676c8e5c697de9dc696d39c71cd4c7649538685ade4189de160c7cc4  work/off-season/index.html
61f74317f8d3fe97546e469fdaccac73b3384235100d3125f82e71d2d007c58e  work/off-season/fr/index.html
1719c09df6246f9a7908d20c78d288210a2580a2d56581c61836eefc24550dc5  work/off-season/es/index.html
507803e4a769cc751b36091caf2333750039c4ebd8b29b5e3d94156202d7e532  work/off-season/sv/index.html
EOF
sha256sum -c expected-v86.sha256

python3 - <<'PY'
import json
from pathlib import Path
from bs4 import BeautifulSoup
expected={
 'index.html':(4,'De vos dates à votre arrivée'),
 'en/index.html':(4,'From dates to arrival'),
 'es/index.html':(4,'De las fechas a la llegada'),
 'off-season/index.html':(3,'Stay together. Choose your courses.'),
 'off-season/fr/index.html':(3,'Séjournez ensemble. Choisissez vos parcours.'),
 'off-season/es/index.html':(3,'Alojaos juntos. Elegid vuestros recorridos.'),
 'off-season/sv/index.html':(3,'Bo tillsammans. Välj era banor.'),
}
for rel,(faq_n,marker) in expected.items():
    s=BeautifulSoup((Path('work')/rel).read_text(encoding='utf-8'),'html.parser')
    assert len(s.find_all('h1'))==1, rel
    assert not [h for h in s.find_all(['h2','h3']) if not h.get_text(' ',strip=True)], rel
    m=s.find('meta',attrs={'name':'villa-almale-version'}); assert m and m.get('content')=='8.6', rel
    t=s.get_text(' ',strip=True); assert marker in t, (rel,marker)
    faq=s.select_one('#faq'); assert not faq or len(faq.find_all('details'))==faq_n, rel
    for tag in s.find_all('script',attrs={'type':'application/ld+json'}): json.loads(tag.string or tag.get_text())
print('V8.6 local semantic validation OK')
PY

restore() {
  echo "Restoring V8.5 production files..."
  lftp -c "
    set cmd:fail-exit yes;
    set net:max-retries 3;
    set net:timeout 30;
    $EXTRA_SETTINGS
    open -p $DEPLOY_PORT -u \"$DEPLOY_USER\",\"$DEPLOY_PASSWORD\" $DEPLOY_SCHEME://$DEPLOY_HOST;
    put backup-before-v86/index.html -o \"$DEPLOY_PATH/index.html\";
    put backup-before-v86/en/index.html -o \"$DEPLOY_PATH/en/index.html\";
    put backup-before-v86/es/index.html -o \"$DEPLOY_PATH/es/index.html\";
    put backup-before-v86/off-season/index.html -o \"$DEPLOY_PATH/off-season/index.html\";
    put backup-before-v86/off-season/fr/index.html -o \"$DEPLOY_PATH/off-season/fr/index.html\";
    put backup-before-v86/off-season/es/index.html -o \"$DEPLOY_PATH/off-season/es/index.html\";
    put backup-before-v86/off-season/sv/index.html -o \"$DEPLOY_PATH/off-season/sv/index.html\";
    bye
  "
}

lftp -c "
  set cmd:fail-exit yes;
  set net:max-retries 2;
  set net:timeout 30;
  $EXTRA_SETTINGS
  open -p $DEPLOY_PORT -u \"$DEPLOY_USER\",\"$DEPLOY_PASSWORD\" $DEPLOY_SCHEME://$DEPLOY_HOST;
  put work/index.html -o \"$DEPLOY_PATH/index.html.v86tmp\";
  put work/en/index.html -o \"$DEPLOY_PATH/en/index.html.v86tmp\";
  put work/es/index.html -o \"$DEPLOY_PATH/es/index.html.v86tmp\";
  put work/off-season/index.html -o \"$DEPLOY_PATH/off-season/index.html.v86tmp\";
  put work/off-season/fr/index.html -o \"$DEPLOY_PATH/off-season/fr/index.html.v86tmp\";
  put work/off-season/es/index.html -o \"$DEPLOY_PATH/off-season/es/index.html.v86tmp\";
  put work/off-season/sv/index.html -o \"$DEPLOY_PATH/off-season/sv/index.html.v86tmp\";
  bye
"
mkdir -p verify-tmp/en verify-tmp/es verify-tmp/off-season/fr verify-tmp/off-season/es verify-tmp/off-season/sv
lftp -c "
  set cmd:fail-exit yes;
  set net:max-retries 2;
  set net:timeout 30;
  $EXTRA_SETTINGS
  open -p $DEPLOY_PORT -u \"$DEPLOY_USER\",\"$DEPLOY_PASSWORD\" $DEPLOY_SCHEME://$DEPLOY_HOST;
  get \"$DEPLOY_PATH/index.html.v86tmp\" -o verify-tmp/index.html;
  get \"$DEPLOY_PATH/en/index.html.v86tmp\" -o verify-tmp/en/index.html;
  get \"$DEPLOY_PATH/es/index.html.v86tmp\" -o verify-tmp/es/index.html;
  get \"$DEPLOY_PATH/off-season/index.html.v86tmp\" -o verify-tmp/off-season/index.html;
  get \"$DEPLOY_PATH/off-season/fr/index.html.v86tmp\" -o verify-tmp/off-season/fr/index.html;
  get \"$DEPLOY_PATH/off-season/es/index.html.v86tmp\" -o verify-tmp/off-season/es/index.html;
  get \"$DEPLOY_PATH/off-season/sv/index.html.v86tmp\" -o verify-tmp/off-season/sv/index.html;
  bye
"
for p in "${files[@]}"; do cmp "work/$p" "verify-tmp/$p"; done

set +e
lftp -c "
  set cmd:fail-exit yes;
  set net:max-retries 2;
  set net:timeout 30;
  $EXTRA_SETTINGS
  open -p $DEPLOY_PORT -u \"$DEPLOY_USER\",\"$DEPLOY_PASSWORD\" $DEPLOY_SCHEME://$DEPLOY_HOST;
  put work/index.html -o \"$DEPLOY_PATH/index.html\";
  put work/en/index.html -o \"$DEPLOY_PATH/en/index.html\";
  put work/es/index.html -o \"$DEPLOY_PATH/es/index.html\";
  put work/off-season/index.html -o \"$DEPLOY_PATH/off-season/index.html\";
  put work/off-season/fr/index.html -o \"$DEPLOY_PATH/off-season/fr/index.html\";
  put work/off-season/es/index.html -o \"$DEPLOY_PATH/off-season/es/index.html\";
  put work/off-season/sv/index.html -o \"$DEPLOY_PATH/off-season/sv/index.html\";
  bye
"
rc=$?
set -e
if [ "$rc" -ne 0 ]; then restore; exit "$rc"; fi

mkdir -p verify-final/en verify-final/es verify-final/off-season/fr verify-final/off-season/es verify-final/off-season/sv
lftp -c "
  set cmd:fail-exit yes;
  set net:max-retries 2;
  set net:timeout 30;
  $EXTRA_SETTINGS
  open -p $DEPLOY_PORT -u \"$DEPLOY_USER\",\"$DEPLOY_PASSWORD\" $DEPLOY_SCHEME://$DEPLOY_HOST;
  get \"$DEPLOY_PATH/index.html\" -o verify-final/index.html;
  get \"$DEPLOY_PATH/en/index.html\" -o verify-final/en/index.html;
  get \"$DEPLOY_PATH/es/index.html\" -o verify-final/es/index.html;
  get \"$DEPLOY_PATH/off-season/index.html\" -o verify-final/off-season/index.html;
  get \"$DEPLOY_PATH/off-season/fr/index.html\" -o verify-final/off-season/fr/index.html;
  get \"$DEPLOY_PATH/off-season/es/index.html\" -o verify-final/off-season/es/index.html;
  get \"$DEPLOY_PATH/off-season/sv/index.html\" -o verify-final/off-season/sv/index.html;
  bye
"
bad=0
for p in "${files[@]}"; do cmp "work/$p" "verify-final/$p" || bad=1; done
if [ "$bad" -ne 0 ]; then restore; exit 1; fi

mkdir -p public/en public/es public/off-season/fr public/off-season/es public/off-season/sv
curl -fsSL --retry 3 -H 'Cache-Control: no-cache' "https://villanuevoportil.com/?v86=${GITHUB_RUN_ID}" -o public/index.html
curl -fsSL --retry 3 -H 'Cache-Control: no-cache' "https://villanuevoportil.com/en/?v86=${GITHUB_RUN_ID}" -o public/en/index.html
curl -fsSL --retry 3 -H 'Cache-Control: no-cache' "https://villanuevoportil.com/es/?v86=${GITHUB_RUN_ID}" -o public/es/index.html
curl -fsSL --retry 3 -H 'Cache-Control: no-cache' "https://villanuevoportil.com/off-season/?v86=${GITHUB_RUN_ID}" -o public/off-season/index.html
curl -fsSL --retry 3 -H 'Cache-Control: no-cache' "https://villanuevoportil.com/off-season/fr/?v86=${GITHUB_RUN_ID}" -o public/off-season/fr/index.html
curl -fsSL --retry 3 -H 'Cache-Control: no-cache' "https://villanuevoportil.com/off-season/es/?v86=${GITHUB_RUN_ID}" -o public/off-season/es/index.html
curl -fsSL --retry 3 -H 'Cache-Control: no-cache' "https://villanuevoportil.com/off-season/sv/?v86=${GITHUB_RUN_ID}" -o public/off-season/sv/index.html
python3 - <<'PY'
from pathlib import Path
from bs4 import BeautifulSoup
expected={
 'index.html':'De vos dates à votre arrivée',
 'en/index.html':'From dates to arrival',
 'es/index.html':'De las fechas a la llegada',
 'off-season/index.html':'Stay together. Choose your courses.',
 'off-season/fr/index.html':'Séjournez ensemble. Choisissez vos parcours.',
 'off-season/es/index.html':'Alojaos juntos. Elegid vuestros recorridos.',
 'off-season/sv/index.html':'Bo tillsammans. Välj era banor.',
}
for rel,marker in expected.items():
    s=BeautifulSoup((Path('public')/rel).read_text(encoding='utf-8'),'html.parser')
    m=s.find('meta',attrs={'name':'villa-almale-version'}); assert m and m.get('content')=='8.6', rel
    assert marker in s.get_text(' ',strip=True), (rel,marker)
print('V8.6 public HTTPS verification OK')
PY

lftp -c "
  set cmd:fail-exit no;
  set net:max-retries 1;
  set net:timeout 20;
  $EXTRA_SETTINGS
  open -p $DEPLOY_PORT -u \"$DEPLOY_USER\",\"$DEPLOY_PASSWORD\" $DEPLOY_SCHEME://$DEPLOY_HOST;
  rm \"$DEPLOY_PATH/index.html.v86tmp\";
  rm \"$DEPLOY_PATH/en/index.html.v86tmp\";
  rm \"$DEPLOY_PATH/es/index.html.v86tmp\";
  rm \"$DEPLOY_PATH/off-season/index.html.v86tmp\";
  rm \"$DEPLOY_PATH/off-season/fr/index.html.v86tmp\";
  rm \"$DEPLOY_PATH/off-season/es/index.html.v86tmp\";
  rm \"$DEPLOY_PATH/off-season/sv/index.html.v86tmp\";
  bye
" || true

echo "V8.6 deployed, byte-checked and publicly verified."
