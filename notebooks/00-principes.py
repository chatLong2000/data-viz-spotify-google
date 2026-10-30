import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    return mo, pl


@app.cell
def _(mo):
    mo.md("""
    # 00 · Principes de visualisation

    Grille de critères pour évaluer les maquettes.
    Question de départ : *où, quand, et en mouvement ou non, qu'est-ce que j'écoute ?*
    """)
    return


@app.cell
def _(pl):
    COLONNES = ["famille", "principe", "question", "reference"]
    LIGNES = [
        ("Gestalt", "Figure/fond", "Les données se détachent-elles du fond ?", "Koffka, 1935"),
        ("Gestalt", "Proximité", "Ce qui est proche est-il réellement lié ?", "Wertheimer, 1923"),
        ("Gestalt", "Similarité", "Une même entité garde-t-elle le même aspect partout ?", "Wertheimer, 1923"),
        ("Gestalt", "Continuité", "L'œil suit-il un parcours sans rupture ?", "Wertheimer, 1923"),
        ("Gestalt", "Clôture", "Les formes fermées se lisent-elles comme un tout ?", "Koffka, 1935"),
        ("Gestalt", "Destin commun", "Ce qui bouge ensemble forme-t-il un groupe pertinent ?", "Wertheimer, 1923"),
        ("Gestalt", "Région commune", "Les groupes sont-ils délimités sans cadres superflus ?", "Koffka, 1935"),
        ("Gestalt", "Connexion", "Le lien entre des marques est-il explicite ?", "Ware, 2012"),
        ("Bertin", "Variables visuelles", "Le canal convient-il au type de donnée ?", "Bertin, 1967"),
        ("Cleveland & McGill", "Précision des canaux", "Position ou longueur sont-elles possibles plutôt qu'angle ou aire ?", "Cleveland & McGill, 1984"),
        ("Tufte", "Data-ink", "Chaque élément porte-t-il une donnée ou un repère utile ?", "Tufte, 1983"),
        ("Tufte", "Lie factor", "L'effet visuel est-il proportionnel à la valeur ?", "Tufte, 1983"),
        ("Tufte", "Petits multiples", "Les comparaisons gardent-elles une structure identique ?", "Tufte, 1983"),
        ("Shneiderman", "Vue d'ensemble d'abord", "Peut-on voir tout, filtrer, puis obtenir le détail ?", "Shneiderman, 1996"),
        ("Munzner", "What–why–how", "Chaque vue répond-elle à une tâche et à une donnée précises ?", "Munzner, 2014"),
        ("Becker & Cleveland", "Brushing & linking", "Une sélection se répercute-t-elle sur les autres vues ?", "Becker & Cleveland, 1987"),
        ("Yi et al.", "Intentions d'interaction", "Chaque interaction sert-elle une intention identifiable ?", "Yi et al., 2007"),
        ("Tversky et al.", "Contrôle de l'animation", "Peut-on suspendre, ralentir ou se passer du mouvement ?", "Tversky et al., 2002"),
        ("Ware", "Luminance ordonnée", "Une magnitude se lit-elle du sombre au clair ?", "Ware, 2012"),
        ("Ware", "Saillance préattentive", "L'essentiel ressort-il sans recherche visuelle ?", "Ware, 2012"),
        ("Brewer", "Type d'échelle", "L'échelle est-elle adaptée : catégorielle, séquentielle ou divergente ?", "Brewer, 1994"),
        ("Accessibilité", "Daltonisme", "Les couleurs restent-elles distinctes en vision altérée ?", "Machado et al., 2009"),
        ("Accessibilité", "Couleur non exclusive", "L'identité est-elle aussi portée par du texte ?", "Ware, 2012"),
        ("Honnêteté", "Lacunes visibles", "Une absence de mesure se distingue-t-elle d'une valeur nulle ?", "Tufte, 1983"),
        ("Honnêteté", "Incertitude visible", "Les petits effectifs sont-ils signalés ?", "Munzner, 2014"),
    ]
    principes = pl.DataFrame(LIGNES, schema=COLONNES, orient="row")
    principes
    return (principes,)


@app.cell
def _(mo, principes):
    mo.vstack([
        mo.md("## Répartition"),
        principes.group_by("famille").len().sort("len", "famille", descending=[True, False]),
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ## Décision

    Chaque maquette compare plusieurs variantes selon cette grille et cite les principes qui justifient son choix.

    Critères prioritaires :

    1. précision du canal ;
    2. séparation figure/fond ;
    3. couleur limitée et lisible par tous ;
    4. honnêteté sur les lacunes et l'incertitude.
    """)
    return


if __name__ == "__main__":
    app.run()
