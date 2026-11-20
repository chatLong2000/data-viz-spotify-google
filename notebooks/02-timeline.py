import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    from pathlib import Path

    import altair as alt
    import marimo as mo
    import polars as pl

    FICHIER = Path(__file__).resolve().parent.parent / "data" / "google" / "Timeline.json"
    return FICHIER, alt, json, mo, pl


@app.cell
def _(mo):
    mo.md("""
    # 02 · Exploration Timeline

    Que contient l'historique de positions, et quelle période est exploitable ?
    Les coordonnées et identifiants de lieux ne sont pas chargés ici.
    """)
    return


@app.cell
def _(FICHIER, json, pl):
    if not FICHIER.is_file():
        raise FileNotFoundError(f"Historique Timeline introuvable : {FICHIER}")
    with FICHIER.open(encoding="utf-8") as _flux:
        _segments = json.load(_flux)

    def type_segment(segment: dict) -> str:
        return next(c for c in ("visit", "activity", "timelinePath", "timelineMemory") if c in segment)

    segments = pl.DataFrame(
        [
            {
                "type": type_segment(s),
                "debut": s["startTime"],
                "fin": s["endTime"],
                "niveau": s.get("visit", {}).get("hierarchyLevel"),
                "semantique": s.get("visit", {}).get("topCandidate", {}).get("semanticType"),
                "mode": s.get("activity", {}).get("topCandidate", {}).get("type"),
                "distance_m": s.get("activity", {}).get("distanceMeters"),
                "points": len(s.get("timelinePath", [])),
            }
            for s in _segments
        ],
        infer_schema_length=None,
    ).with_columns(
        pl.col("debut").str.extract(r"(Z|[+-]\d{2}:\d{2})$").alias("decalage"),
        pl.col("debut").str.to_datetime(time_zone="UTC", time_unit="ms"),
        pl.col("fin").str.to_datetime(time_zone="UTC", time_unit="ms"),
        pl.col("distance_m").cast(pl.Float64),
    ).with_columns(
        ((pl.col("fin") - pl.col("debut")).dt.total_seconds() / 3600).alias("heures"),
        pl.col("debut").dt.year().alias("annee"),
    )
    return (segments,)


@app.cell
def _(mo, pl, segments):
    _types = (
        segments.group_by("type")
        .agg(
            pl.len().alias("segments"),
            pl.col("debut").min().dt.date().alias("premier"),
            pl.col("fin").max().dt.date().alias("dernier"),
        )
        .sort("segments", descending=True)
    )
    _annees = (
        segments.pivot(on="type", index="annee", values="points", aggregate_function="len")
        .sort("annee")
        .with_columns(pl.col("annee").cast(pl.String))
    )
    mo.vstack([mo.md("## Volume"), _types, _annees])
    return


@app.cell
def _(pl, segments):
    DEPUIS = pl.datetime(2021, 9, 1, time_zone="UTC")
    commun = segments.filter(pl.col("debut") >= DEPUIS)
    visites = commun.filter((pl.col("type") == "visit") & (pl.col("niveau") == "0"))
    trajets = commun.filter(pl.col("type") == "activity")
    return commun, trajets, visites


@app.cell
def _(alt, mo, pl, trajets, visites):
    def fusionner(intervalles: pl.DataFrame) -> pl.DataFrame:
        """Réunion d'intervalles : les chevauchements ne comptent qu'une fois."""
        return (
            intervalles.sort("debut")
            .with_columns(
                (pl.col("debut") > pl.col("fin").cum_max().shift(1)).fill_null(True).cum_sum().alias("bloc")
            )
            .group_by("bloc")
            .agg(pl.col("debut").min(), pl.col("fin").max())
        )

    _couverts = fusionner(pl.concat([visites.select("debut", "fin"), trajets.select("debut", "fin")]))
    _jours = (
        _couverts.with_columns(
            pl.date_ranges(pl.col("debut").dt.date(), pl.col("fin").dt.date()).alias("jour")
        )
        .explode("jour")
        .with_columns(pl.col("jour").cast(pl.Datetime("ms")).dt.replace_time_zone("UTC").alias("minuit"))
        .with_columns(
            (
                pl.min_horizontal("fin", pl.col("minuit") + pl.duration(days=1))
                - pl.max_horizontal("debut", "minuit")
            ).dt.total_seconds().alias("secondes")
        )
    )
    couverture = (
        _jours.group_by(pl.col("minuit").dt.truncate("1mo").alias("mois"))
        .agg(pl.col("secondes").sum())
        .with_columns(
            (pl.col("secondes") / (pl.col("mois").dt.month_end().dt.day().cast(pl.Int64) * 86400)).alias("part")
        )
        .sort("mois")
    )
    _graphe = (
        alt.Chart(couverture)
        .mark_bar()
        .encode(
            x=alt.X("mois:T", title=None),
            y=alt.Y("part:Q", axis=alt.Axis(format="%"), title="Temps couvert par mois"),
            tooltip=["mois:T", alt.Tooltip("part:Q", format=".0%")],
        )
        .properties(width=620, height=200)
    )
    mo.vstack([
        mo.md("""
    ## Couverture

    Visites et trajets réunis, depuis septembre 2021.
    2024 est presque vide. En 2025, la couverture élevée vient surtout de visites de plusieurs jours : elle ne garantit pas la précision.
    """),
        _graphe,
    ])
    return


@app.cell
def _(alt, mo, pl, trajets):
    _modes = (
        trajets.group_by("mode")
        .agg(
            pl.len().alias("trajets"),
            (pl.col("distance_m").sum() / 1000).round().alias("km"),
            (pl.col("heures").sum()).round().alias("heures"),
            (pl.col("heures").median() * 60).round(1).alias("médiane_min"),
        )
        .sort("trajets", descending=True)
    )
    _graphe = (
        alt.Chart(_modes)
        .mark_bar()
        .encode(
            x=alt.X("trajets:Q", title="Trajets"),
            y=alt.Y("mode:N", sort=None, title=None),
            tooltip=["mode", "trajets", "km", "heures", "médiane_min"],
        )
        .properties(width=560, height=240)
    )
    mo.vstack([mo.md("## Modes de transport\n\nInférés par Google : à regrouper et à prendre avec prudence."), _graphe, _modes])
    return


@app.cell
def _(mo, pl, trajets):
    SEUIL_LONG_H = 12
    _longs = trajets.filter(pl.col("heures") > SEUIL_LONG_H)
    _par_annee = (
        trajets.group_by(pl.col("annee").cast(pl.String).alias("année"))
        .agg(
            pl.len().alias("trajets"),
            (pl.col("heures").median() * 60).round(1).alias("médiane_min"),
            (pl.col("heures") > SEUIL_LONG_H).sum().alias("plus_de_12h"),
        )
        .sort("année")
    )
    mo.vstack([
        mo.md(f"## Trajets aberrants\n\n**{_longs.height}** trajets durent plus de {SEUIL_LONG_H} h."),
        _par_annee,
    ])
    return


@app.cell
def _(commun, mo, pl, visites):
    _semantique = (
        visites.group_by("semantique")
        .agg(pl.len().alias("visites"), (pl.col("heures").sum()).round().alias("heures"))
        .sort("visites", descending=True)
    )
    _visites_annee = (
        visites.group_by(pl.col("annee").cast(pl.String).alias("année"))
        .agg(
            pl.len().alias("visites"),
            pl.col("heures").median().round(2).alias("médiane_h"),
            pl.col("heures").quantile(0.9).round(1).alias("q90_h"),
        )
        .sort("année")
    )
    _points = (
        commun.filter(pl.col("type") == "timelinePath")
        .group_by(pl.col("annee").cast(pl.String).alias("année"))
        .agg(pl.col("points").sum().alias("points_gps"), pl.len().alias("tracés"))
        .sort("année")
    )
    _hierarchie = commun.filter(pl.col("type") == "visit").group_by("niveau").len(name="visites").sort("niveau")
    mo.vstack([
        mo.md("## Visites et points GPS\n\nLes types `Home`, `Inferred Home` et `Inferred Work` désignent des lieux sensibles."),
        _semantique,
        _hierarchie,
        _visites_annee,
        _points,
    ])
    return


@app.cell
def _(mo, pl, segments):
    _decalages = segments.group_by("decalage").len(name="segments").sort("segments", descending=True)
    _par_type = (
        segments.group_by("type")
        .agg((pl.col("decalage") == "Z").mean().round(3).alias("part_utc"))
        .sort("type")
    )
    mo.vstack([
        mo.md("## Fuseaux\n\nVisites et trajets portent leur décalage local. Les tracés GPS sont en UTC."),
        _par_type,
        _decalages,
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ## Décision

    - Garder la période commune avec Spotify, depuis septembre 2021.
    - Visites de niveau 0 uniquement : le niveau 1 compterait deux fois le même temps.
    - Montrer le trou de 2024 comme une absence de mesure, pas comme une valeur nulle.
    - Signaler que les données 2025-2026 sont moins précises : moins de points GPS et visites plus longues.
    - Exclure des tracés les trajets de plus de 12 h : presque tous datent de 2025-2026.
    - Regrouper métro et tram, et garder le mode `unknown` à part.
    - Ignorer `timelineMemory`.
    - Heure locale : décalage du segment. Les tracés GPS, en UTC, se rattachent à leur trajet.
    - Protéger domicile et travail, déclarés ou inférés, et ne jamais publier les `placeID`.
    """)
    return


if __name__ == "__main__":
    app.run()
