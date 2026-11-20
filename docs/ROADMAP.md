# Feuille de route

Nous avançons par étapes : comprendre les données, dessiner les vues, puis coder.
Chaque étape donne un commit.

## Fait

- Principes : grille pour juger les maquettes (`notebooks/00-principes.py`)
- Exploration Spotify (`notebooks/01-spotify.py`)
- Exploration Timeline (`notebooks/02-timeline.py`)
- Cadrage : question, tâches, données ([CADRAGE.md](CADRAGE.md))

## À faire

1. Maquettes des vues
2. Pipeline : lecture des exports
3. Pipeline : jointure écoutes et positions
4. Pipeline : lieux et zones sensibles
5. Pipeline : trajets et voyages
6. Pipeline : export et audit de confidentialité
7. App : socle et décodage
8. App : en-tête
9. App : carte
10. App : horloge, petits multiples, artistes
11. App : frise, replay, voyages
12. Documentation
13. Tests de bout en bout

## Règles

- Les exports bruts restent dans `data/`, hors du dépôt.
- Chaque module arrive avec ses tests, sur des données synthétiques.
- Pas de vue codée sans maquette.
