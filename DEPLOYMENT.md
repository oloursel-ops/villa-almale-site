# Publication automatique de Villa Almale

## Objectif

Le dépôt GitHub devient la source unique du site. Après validation et fusion d'une modification dans `main`, GitHub Actions transfère automatiquement les fichiers vers l'hébergement Infomaniak. Aucun ZIP ne doit plus être déposé manuellement.

## Configuration unique à effectuer

Dans GitHub : **Settings → Environments → New environment → `production`**, puis ajouter les secrets suivants dans cet environnement :

| Secret | Valeur attendue |
|---|---|
| `INFOMANIAK_SCHEME` | `sftp` de préférence ; sinon `ftps` ou `ftp` selon l'offre |
| `INFOMANIAK_HOST` | serveur Infomaniak, par exemple `xxxx.ftp.infomaniak.com` |
| `INFOMANIAK_PORT` | `22` pour SFTP, `21` pour FTP/FTPS |
| `INFOMANIAK_USER` | utilisateur FTP/SFTP dédié au site |
| `INFOMANIAK_PASSWORD` | mot de passe de cet utilisateur |
| `INFOMANIAK_PATH` | répertoire racine réellement servi par `villanuevoportil.com`, par exemple `/web` ou `/sites/villanuevoportil.com` |

Créer idéalement chez Infomaniak un utilisateur FTP/SFTP distinct, limité au répertoire du site. Ne jamais inscrire ces identifiants dans un fichier du dépôt.

## Processus courant

1. Une modification est préparée sur une branche dédiée.
2. Une pull request présente clairement les changements.
3. Olivier vérifie la prévisualisation ou le diff et fusionne la pull request.
4. La fusion dans `main` déclenche automatiquement `Deploy Villa Almale to Infomaniak`.
5. Le statut vert dans l'onglet **Actions** confirme la publication.

## Lancement manuel

Dans **Actions → Deploy Villa Almale to Infomaniak → Run workflow**, il est possible de republier la version actuelle de `main` sans modifier le code.

## Sécurité et retour arrière

- Les accès Infomaniak sont stockés dans les secrets GitHub et ne sont pas présents dans le code.
- Le déploiement est sérialisé : deux publications ne peuvent pas se chevaucher.
- Le transfert supprime du serveur les fichiers qui n'existent plus dans le dépôt. Le dépôt doit donc contenir l'intégralité des fichiers publics du site avant la première activation.
- Pour revenir en arrière, restaurer un commit antérieur dans `main`, puis relancer le workflow.
- Avant la première publication automatique, sauvegarder une fois le contenu actuellement en ligne depuis le Web FTP Infomaniak.

## Critère de réussite

Après la première configuration, une modification validée doit passer de GitHub au site en production sans téléchargement, ZIP, décompression ni manipulation FTP par Olivier.
