#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from pathlib import Path
from bs4 import BeautifulSoup

DATE='2026-08-06'; STYLE='villa-almale-v81-offseason-conversion'; REVIEW='https://www.vrbo.com/es-es/p8160054?equalTargetTab=tab-0'
P={'off-season/index.html':'en','off-season/fr/index.html':'fr','off-season/es/index.html':'es','off-season/sv/index.html':'sv'}
C={
'en':dict(book='/en/reservation.html',main='Availability in September & October',detail='Entire villa from €2,226 / 7 nights · €371 per person for the week when shared by 6 adults (€53 per night)',cta='Check prices',
 facts=[('€53','per person/night · 6 adults'),('5','bedrooms · ideal for 4–6 adults'),('Golf access','official walking route starts < 1 min from the residence entrance'),('9.0/10','Vrbo · 13 reviews')],
 eye='Why golfing groups choose Villa Almale',title='The practical alternative to several hotel rooms.',intro='One private base, enough bedrooms for the group and the freedom to organise every round separately.',
 cards=[('One house','Five bedrooms, shared living spaces and secure storage for golf bags and trolleys.'),('Clear group value','From €371 per person for seven nights when six adults share the villa.'),('Golf within walking reach','The official pedestrian route towards Golf Nuevo Portil begins less than one minute from the residence entrance.'),('Book with confidence','Registered accommodation, live OwnerRez availability and payments processed by Stripe.')],
 quote='“The house is spacious and pleasant. The pool is clean.”',qmeta='Verified Vrbo guest · July 2022 · translated from French',qlink='Read the verified reviews',
 access='The official pedestrian route begins less than one minute from the gated residence entrance. This refers to access to the route, not the clubhouse or first tee.',
 mideye='Ready to choose the week?',midtitle='From €371 per person for 7 nights when 6 adults share.',midtext='Check live dates and the total price before arranging tee times with the courses.',midcta='See dates and total price',
 beye='When you are not playing golf',btitle='Keep the rest of the week simple.',bintro='Three easy ways to enjoy the coast without turning the landing page into a destination guide.',
 bc=[('Beach and walks','The Ría beach, pine paths and Atlantic sunsets are within easy reach of the villa.'),('El Rompido','Waterfront terraces, seafood restaurants, the marina and boats towards the Flecha.'),('One day out','Choose Seville, Huelva or the Algarve when the group wants a change of scenery.')],
 nav='Beyond golf',notice='Build the week around your tee times. Golf, transfers and activities are booked separately with each operator, so the group keeps full control of the programme.',heat=('comfort','wood stove','central heating','portable units'),weather=('Check weather and tides','AEMET forecast','Tides and sea conditions')),
'fr':dict(book='/reservation.html',main='Disponibilités en septembre et octobre',detail='Villa entière dès 2 226 € / 7 nuits · 371 € par personne la semaine à 6 adultes (53 € par nuit)',cta='Voir les tarifs',
 facts=[('53 €','par personne/nuit · 6 adultes'),('5','chambres · idéal pour 4 à 6 adultes'),('Accès golf','le chemin piéton débute à < 1 min de l’entrée de la résidence'),('9,0/10','Abritel / Vrbo · 13 avis')],
 eye='Pourquoi les groupes de golfeurs choisissent Villa Almale',title='L’alternative pratique à plusieurs chambres d’hôtel.',intro='Une base privée, assez de chambres pour le groupe et la liberté d’organiser chaque parcours séparément.',
 cards=[('Une seule maison','Cinq chambres, de vrais espaces communs et un garage pour les sacs et chariots de golf.'),('Un prix de groupe lisible','Dès 371 € par personne pour sept nuits lorsque six adultes partagent la villa.'),('Le golf accessible à pied','Le chemin piéton officiel vers Golf Nuevo Portil débute à moins d’une minute de l’entrée de la résidence.'),('Réserver en confiance','Hébergement déclaré, disponibilités OwnerRez en direct et paiements traités par Stripe.')],
 quote='« La maison est grande et agréable. La piscine est propre. »',qmeta='Voyageur vérifié sur Abritel / Vrbo · juillet 2022',qlink='Lire les avis vérifiés',
 access='L’accès au chemin officiel se trouve à moins d’une minute de l’entrée de la résidence. Cette indication concerne le départ du chemin, et non le clubhouse ou le premier tee.',
 mideye='Prêts à choisir la semaine ?',midtitle='Dès 371 € par personne pour 7 nuits à 6 adultes.',midtext='Consultez les dates et le prix total en direct avant d’organiser les départs avec les parcours.',midcta='Voir les dates et le prix total',
 beye='Quand vous ne jouez pas au golf',btitle='Garder le reste de la semaine simple.',bintro='Trois idées faciles pour profiter de la côte sans transformer cette page de campagne en guide touristique.',
 bc=[('Plage et promenades','La plage de la Ría, les chemins sous les pins et les couchers de soleil atlantiques sont faciles d’accès.'),('El Rompido','Terrasses au bord de l’eau, restaurants de poissons, marina et bateaux vers la Flecha.'),('Une journée d’excursion','Séville, Huelva ou l’Algarve lorsque le groupe souhaite changer de décor.')],
 nav='Après le golf',notice='Composez la semaine autour de vos départs. Golf, transferts et activités se réservent séparément auprès de chaque prestataire, afin que le groupe garde la maîtrise de son programme.',heat=('confort','poêle','chauffage central','appareils portables'),weather=('Vérifier la météo et les marées','Prévisions AEMET','Marées et état de la mer')),
'es':dict(book='/es/reservation.html',main='Disponibilidad en septiembre y octubre',detail='Villa completa desde 2.226 € / 7 noches · 371 € por persona la semana para 6 adultos (53 € por noche)',cta='Ver precios',
 facts=[('53 €','por persona/noche · 6 adultos'),('5','dormitorios · ideal para 4–6 adultos'),('Acceso al golf','la ruta peatonal empieza a < 1 min de la entrada de la urbanización'),('9,0/10','Vrbo · 13 opiniones')],
 eye='Por qué los grupos de golf eligen Villa Almale',title='La alternativa práctica a varias habitaciones de hotel.',intro='Una base privada, dormitorios suficientes para el grupo y libertad para organizar cada recorrido por separado.',
 cards=[('Una sola casa','Cinco dormitorios, espacios comunes amplios y garaje para bolsas y carros de golf.'),('Precio de grupo claro','Desde 371 € por persona durante siete noches cuando seis adultos comparten la villa.'),('Golf accesible a pie','La ruta peatonal oficial hacia Golf Nuevo Portil comienza a menos de un minuto de la entrada de la urbanización.'),('Reserva con confianza','Alojamiento registrado, disponibilidad en directo con OwnerRez y pagos procesados por Stripe.')],
 quote='«La casa es amplia y agradable. La piscina está limpia.»',qmeta='Huésped verificado en Vrbo · julio de 2022 · traducido del francés',qlink='Leer las opiniones verificadas',
 access='El acceso a la ruta oficial está a menos de un minuto de la entrada de la urbanización. Esta indicación se refiere al inicio de la ruta, no a la casa club ni al primer tee.',
 mideye='¿Listos para elegir la semana?',midtitle='Desde 371 € por persona durante 7 noches para 6 adultos.',midtext='Consulta las fechas y el precio total en directo antes de organizar las salidas con los campos.',midcta='Ver fechas y precio total',
 beye='Cuando no estáis jugando al golf',btitle='Mantener sencillo el resto de la semana.',bintro='Tres formas fáciles de disfrutar de la costa sin convertir esta página de campaña en una guía turística.',
 bc=[('Playa y paseos','La playa de la Ría, los senderos entre pinos y las puestas de sol atlánticas están al alcance.'),('El Rompido','Terrazas frente al agua, restaurantes de pescado, puerto deportivo y barcos hacia la Flecha.'),('Un día de excursión','Sevilla, Huelva o el Algarve cuando el grupo quiera cambiar de paisaje.')],
 nav='Después del golf',notice='Organizad la semana alrededor de vuestras salidas. Golf, traslados y actividades se reservan por separado con cada operador, para que el grupo mantenga el control del programa.',heat=('confort','insert de leña','calefacción central','aparatos portátiles'),weather=('Consultar el tiempo y las mareas','Previsión de AEMET','Mareas y estado del mar')),
'sv':dict(book='/en/reservation.html',main='Lediga veckor i september och oktober',detail='Hela villan från 2 226 € / 7 nätter · 371 € per person för veckan vid 6 vuxna (53 € per natt)',cta='Se priser',
 facts=[('53 €','per person/natt · 6 vuxna'),('5','sovrum · idealiskt för 4–6 vuxna'),('Golfväg','den officiella gångvägen börjar < 1 min från områdets entré'),('9,0/10','Vrbo · 13 omdömen')],
 eye='Därför väljer golfgrupper Villa Almale',title='Ett praktiskt alternativ till flera hotellrum.',intro='En privat bas, gott om sovrum för gruppen och frihet att boka varje golfrunda separat.',
 cards=[('Ett gemensamt hus','Fem sovrum, generösa sällskapsytor och garage för golfbagar och vagnar.'),('Tydligt gruppvärde','Från 371 € per person för sju nätter när sex vuxna delar villan.'),('Golf inom gångavstånd','Den officiella gångvägen mot Golf Nuevo Portil börjar mindre än en minut från bostadsområdets entré.'),('Trygg direktbokning','Registrerat boende, tillgänglighet via OwnerRez och betalningar som hanteras av Stripe.')],
 quote='”Huset är rymligt och trivsamt. Poolen är ren.”',qmeta='Verifierad Vrbo-gäst · juli 2022 · översatt från franska',qlink='Läs de verifierade omdömena',
 access='Den officiella gångvägen börjar mindre än en minut från bostadsområdets entré. Tidsangivelsen gäller vägens början, inte klubbhuset eller första tee.',
 mideye='Redo att välja vecka?',midtitle='Från 371 € per person för 7 nätter när 6 vuxna delar.',midtext='Se lediga datum och totalpriset innan ni bokar starttider direkt med golfbanorna.',midcta='Se datum och totalpris',
 beye='När ni inte spelar golf',btitle='Håll resten av veckan enkel.',bintro='Tre enkla sätt att uppleva kusten utan att göra kampanjsidan till en fullständig reseguide.',
 bc=[('Strand och promenader','Ría-stranden, stigarna bland pinjeträden och Atlantens solnedgångar ligger nära till hands.'),('El Rompido','Terrasser vid vattnet, fiskrestauranger, småbåtshamn och båtar mot Flecha.'),('En dagsutflykt','Välj Sevilla, Huelva eller Algarve när gruppen vill se något annat.')],
 nav='Efter golfen',notice='Planera veckan efter era starttider. Golf, transfer och aktiviteter bokas separat hos respektive aktör, så att ni själva styr programmet.',heat=('komfort','vedspis','centralvärme','portabla enheter'),weather=('Kontrollera väder och tidvatten','Väderprognos från AEMET','Tidvatten och havsläge'))}

CSS='''
.site-autumn-offer__inner{display:block;padding:.62rem 3.2rem .68rem;text-align:center}.v81-promo{display:flex;flex-direction:column;gap:.08rem;align-items:center}.v81-promo b{font-family:Georgia,serif;font-size:clamp(1.02rem,1.7vw,1.2rem)}.v81-promo small{font-size:.8rem;font-weight:650}.v81-promo a{margin-left:.35rem;font-weight:800;white-space:nowrap}
.v81-why{padding:3.2rem 0;background:#f7f4ed;color:#153f39}.v81-head{display:grid;grid-template-columns:.9fr 1.1fr;gap:2.5rem;align-items:end;margin-bottom:1.1rem}.v81-head h2,.v81-beyond h2{margin:.25rem 0 0;font-size:clamp(1.75rem,3.3vw,2.8rem);line-height:1.08}.v81-head p{margin:0;line-height:1.65}.v81-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.75rem}.v81-card{padding:1rem;border-radius:15px;background:#fff;border:1px solid rgba(20,65,58,.13)}.v81-card h3{margin:0 0 .3rem;font-size:1rem}.v81-card p{margin:0;font-size:.9rem;line-height:1.5}.v81-review{display:grid;grid-template-columns:1fr auto;gap:1rem;align-items:center;margin-top:.9rem;padding:1rem;border-radius:15px;background:#153f39;color:#fff}.v81-review blockquote{margin:0;font-family:Georgia,serif;font-size:1.15rem}.v81-review p{margin:.25rem 0 0;font-size:.78rem;color:#dce5e2}.v81-review a{color:#fff;font-weight:800}
.v81-mid{padding:1.15rem 0;background:#d9b56d;color:#153f39}.v81-mid .shell{display:grid;grid-template-columns:1fr auto;gap:1rem;align-items:center}.v81-mid h2{margin:.15rem 0 .2rem;font-size:clamp(1.35rem,2.7vw,2rem)}.v81-mid p{margin:0}.v81-beyond{padding:3.2rem 0;background:#143e38;color:#fff}.v81-beyond .v81-head p{color:#dce5e2}.v81-beyond .v81-grid{grid-template-columns:repeat(3,1fr)}.v81-beyond .v81-card{background:rgba(255,255,255,.06);border-color:rgba(255,255,255,.15)}.v81-beyond .v81-card h3{color:#fff}.v81-beyond .v81-card p{color:#dce5e2}.v81-links{display:flex;gap:.9rem;flex-wrap:wrap;margin-top:1rem}.v81-links a{color:#fff;text-decoration:underline}
@media(max-width:900px){.v81-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:720px){.site-autumn-offer__inner{padding:.6rem 2.8rem .65rem .7rem}.v81-promo small{font-size:.74rem}.v81-head,.v81-mid .shell,.v81-review{grid-template-columns:1fr}.v81-beyond .v81-grid{grid-template-columns:1fr}.v81-mid .button{width:100%;text-align:center}}@media(max-width:520px){.v81-grid{grid-template-columns:1fr}}
'''

def f(html):
 s=BeautifulSoup(html,'html.parser'); return next(x for x in s.contents if getattr(x,'name',None))
def cards(items): return ''.join(f'<article class="v81-card"><h3>{a}</h3><p>{b}</p></article>' for a,b in items)
def why(c): return f'<section class="v81-why" id="why-golfers"><div class="shell"><div class="v81-head"><div><span class="eyebrow">{c["eye"]}</span><h2>{c["title"]}</h2></div><p>{c["intro"]}</p></div><div class="v81-grid">{cards(c["cards"])}</div><div class="v81-review"><div><blockquote>{c["quote"]}</blockquote><p>{c["qmeta"]}</p></div><a href="{REVIEW}" target="_blank" rel="nofollow noopener noreferrer">{c["qlink"]} →</a></div></div></section>'
def mid(c): return f'<section class="v81-mid" id="golf-booking-cta"><div class="shell"><div><span class="eyebrow">{c["mideye"]}</span><h2>{c["midtitle"]}</h2><p>{c["midtext"]}</p></div><a class="button secondary" data-analytics-event="booking_click" data-booking-position="after-golf" href="{c["book"]}">{c["midcta"]} →</a></div></section>'
def beyond(c):
 w=c['weather']; return f'<section class="v81-beyond" id="beyond-golf"><div class="shell"><div class="v81-head"><div><span class="eyebrow">{c["beye"]}</span><h2>{c["btitle"]}</h2></div><p>{c["bintro"]}</p></div><div class="v81-grid">{cards(c["bc"])}</div><div class="v81-links"><strong>{w[0]}:</strong><a href="https://www.aemet.es/es/eltiempo/prediccion/municipios/cartaya-id21021" target="_blank" rel="nofollow noopener noreferrer">{w[1]} →</a><a href="https://www.puertos.es/servicios/oceanografia" target="_blank" rel="nofollow noopener noreferrer">{w[2]} →</a></div></div></section>'
def norm(x): return re.sub(r'\s+',' ',x.lower()).strip()
def datefix(x):
 if isinstance(x,dict):
  t=x.get('@type'); ts={t} if isinstance(t,str) else set(t or [])
  if 'WebPage' in ts:x['dateModified']=DATE
  for v in x.values():datefix(v)
 elif isinstance(x,list):
  for v in x:datefix(v)
def navfix(s,label):
 for box in s.select('header nav,.footer-links'):
  ls=box.select('a[href="#nautical"],a[href="#tourism"],a[href="#beyond-golf"]')
  if ls:
   ls[0]['href']='#beyond-golf';ls[0].string=label
   for x in ls[1:]:x.decompose()
def patch(path,lang):
 c=C[lang];s=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
 if not s.head or not s.body or len(s.find_all('h1'))!=1:raise RuntimeError(f'{path}: invalid document')
 canon=s.find('link',rel='canonical');before=canon.get('href') if canon else None
 old=s.find(id=STYLE)
 if old:old.decompose()
 st=s.new_tag('style',id=STYLE);st.string=CSS;s.head.append(st)
 o=s.select_one('[data-site-global-offer]');inn=o.select_one('.site-autumn-offer__inner') if o else None
 if not inn:raise RuntimeError(f'{path}: offer missing')
 o['data-offer-version']='september-october-2026-v81';inn.clear();inn.append(f(f'<span class="site-autumn-offer__text v81-promo" data-offseason-promo="v81"><b>{c["main"]}</b><small>{c["detail"]} <a class="site-autumn-offer__cta" data-analytics-event="special_offer_click" href="{c["book"]}">{c["cta"]} →</a></small></span>'))
 hero=s.select_one('section.hero') or s.select_one('.hero');facts=s.select_one('.hero-facts')
 if not hero or not facts:raise RuntimeError(f'{path}: hero missing')
 facts.clear()
 for a,b in c['facts']:facts.append(f(f'<div class="hero-fact"><strong>{a}</strong><span>{b}</span></div>'))
 nw=f(why(c)); ow=s.select_one('#why-golfers'); ow.replace_with(nw) if ow else hero.insert_after(nw)
 golf=s.select_one('#golf');access=golf.select_one('.golf-access') if golf else None
 if not access:raise RuntimeError(f'{path}: golf notice missing')
 access.clear();parts=c['access'].split('. ',1);q=s.new_tag('strong');q.string=parts[0]+'.';access.append(q);access.append(' '+(parts[1] if len(parts)>1 else ''))
 nm=f(mid(c));om=s.select_one('#golf-booking-cta');om.replace_with(nm) if om else golf.insert_after(nm)
 na=s.select_one('#nautical');to=s.select_one('#tourism');ob=s.select_one('#beyond-golf');anchor=na or to or ob;nb=f(beyond(c))
 anchor.replace_with(nb) if anchor else nm.insert_after(nb)
 for x in (na,to,ob):
  if x is not None and x is not anchor and x.parent is not None:x.decompose()
 navfix(s,c['nav'])
 pr=s.select_one('#practical')
 if pr:
  terms=tuple(norm(x) for x in c['heat'])
  for art in list(pr.find_all('article')):
   if any(t in norm(art.get_text(' ',strip=True)) for t in terms):art.decompose()
  ns=pr.select('.notice-box')
  if ns:ns[-1].clear();ns[-1].append(c['notice'])
 for b in s.find_all('script',attrs={'type':'application/ld+json'}):
  data=json.loads(b.string or b.get_text());datefix(data);b.string=json.dumps(data,ensure_ascii=False,separators=(',',':'))
 out=str(s);out=out if out.lstrip().lower().startswith('<!doctype') else '<!DOCTYPE html>\n'+out;path.write_text(out,encoding='utf-8')
 z=BeautifulSoup(out,'html.parser');text=z.get_text(' ',strip=True)
 assert len(z.select('#why-golfers'))==len(z.select('#golf-booking-cta'))==len(z.select('#beyond-golf'))==1
 assert not z.select('#nautical,#tourism') and len(z.select('[data-offseason-promo="v81"]'))==1 and c['detail'] in text and c['access'] in text and len(z.select('.hero-facts .hero-fact'))==4
 assert z.select_one(f'#golf-booking-cta a[href="{c["book"]}"]') and (z.find('link',rel='canonical').get('href') if z.find('link',rel='canonical') else None)==before
 if pr:assert not any(norm(x) in norm(z.select_one('#practical').get_text(' ',strip=True)) for x in c['heat'])
 print('Validated V8.1:',lang)
def main():
 root=Path(sys.argv[1])
 for rel,lang in P.items():
  p=root/rel
  if not p.is_file():raise RuntimeError(f'Missing page: {p}')
  patch(p,lang)
if __name__=='__main__':main()

# Production trigger after workflow registration.
