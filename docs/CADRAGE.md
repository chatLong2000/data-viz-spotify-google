# Cadrage

Nous partons d'une question : où, quand, et en mouvement ou à l'arrêt, qu'écoute-t-on ?

## Tâches

| Tâche (Munzner, 2014) | Question | Vue envisagée |
|---|---|---|
| Localiser | Quels lieux ont une signature musicale ? | Carte des lieux |
| Comparer | Écoute-t-on autrement en mouvement ? | Petits multiples par contexte |
| Repérer des tendances | Quels rythmes heure × jour ? | Vue radiale |
| Parcourir | Quels morceaux pour quels jours, quels voyages ? | Frise et replay |
| Résumer | Combien, qui, quelle part en mouvement ? | Indicateurs |

## Données

Spotify donne une ligne par écoute. `ts` marque la fin (UTC), donc le début vaut
`ts − ms_played`. Nous gardons aussi l'artiste, le titre et `skipped`.

Timeline contient des visites (lieu, type, fuseau) et des déplacements (mode, tracé GPS, distance).

Une écoute prend le segment Timeline qui contient son milieu. Si un déplacement chevauche une
visite, c'est le déplacement qui l'emporte.

## Dérivations

- heure locale, tirée du segment ou du pays de connexion ;
- lieux regroupés sur une grille d'environ 220 m, sans adresse exacte ;
- trajets découpés aux changements de morceau ;
- voyages : séjours à plus de 150 km du domicile ;
- diversité raréfiée, pour comparer des contextes de tailles différentes.
