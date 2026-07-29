# Villa ALMALE V6.6 — golf, confort et consolidation SEO

Livraison du 29 juillet 2026, construite à partir du package V6.5 validé et du `.htaccess` de production.

## Contenu

- informations exactes sur les trois climatiseurs mobiles et les deux ventilateurs de plafond ;
- produit **Atlantic Golf House at Villa Almale** en français, anglais et espagnol ;
- accès piéton officiel au Golf Nuevo Portil annoncé à moins d’une minute ;
- mention explicite que la petite porte privée en limite de propriété n’est pas un accès voyageurs ;
- redirection HTTP, `www` et `index.html` consolidée en un seul saut ;
- sitemap limité aux neuf pages d’intention indexables ;
- conservation des canoniques, `hreflang`, JSON-LD, images héro responsives et liens `sameAs`.

## Déploiement

Le workflow V6.6 télécharge les douze fichiers de production ciblés, en conserve une sauvegarde, applique un correctif idempotent, valide les contenus et les métadonnées, téléverse les fichiers, compare les octets distants et vérifie les URL publiques. Une restauration automatique des fichiers ciblés s’exécute si la vérification post-déploiement échoue.

## Périmètre exclu

Aucune modification des pages de réservation, du guide privé, des images, d’OwnerRez, de Chekin, des tarifs ou de GA4/consentement.
