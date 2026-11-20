# Feuille de route

Nous avançons par étapes : comprendre les données, dessiner les vues, puis coder.
Chaque étape donne un commit.

## Fait

- Principes : grille pour juger les maquettes (`notebooks/00-principes.py`)
- Exploration Spotify (`notebooks/01-spotify.py`)
- Exploration Timeline (`notebooks/02-timeline.py`)
- Cadrage : question, tâches, données ([CADRAGE.md](CADRAGE.md))
- Maquettes : variantes comparées pour chaque vue ([maquettes/index.html](maquettes/index.html))

## À faire

1. Pipeline : lecture des exports
2. Pipeline : jointure écoutes et positions
3. Pipeline : lieux et zones sensibles
4. Pipeline : trajets et voyages
5. Pipeline : export et audit de confidentialité
6. App : socle et décodage
7. App : en-tête
8. App : carte
9. App : horloge, petits multiples, artistes
10. App : frise, replay, voyages
11. Documentation
12. Tests de bout en bout

## Règles

- Les exports bruts restent dans `data/`, hors du dépôt.
- Chaque module arrive avec ses tests, sur des données synthétiques.
- Pas de vue codée sans maquette.
