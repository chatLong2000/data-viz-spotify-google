import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path

    import altair as alt
    import marimo as mo
    import polars as pl

    DOSSIER = Path(__file__).resolve().parent.parent / "data" / "Spotify Extended Streaming History"
    return DOSSIER, alt, mo, pl


@app.cell
def _(mo):
    mo.md("""
    # 01 · Exploration Spotify

    Que contient l'historique d'écoute, et que peut-on en garder ?
    """)
    return


@app.cell
def _(DOSSIER, pl):
    # ip_addr n'est jamais chargé : seules les colonnes utiles sont lues.
    COLONNES = [
        "ts",
        "ms_played",
        "master_metadata_track_name",
        "master_metadata_album_artist_name",
        "episode_name",
        "audiobook_title",
        "skipped",
        "reason_end",
        "conn_country",
        "platform",
    ]
    fichiers = sorted(DOSSIER.glob("Streaming_History_Audio_*.json"))
    if not fichiers:
        raise FileNotFoundError(f"Aucun historique Spotify dans {DOSSIER}")

    brut = pl.concat(
        [pl.read_json(f, infer_schema_length=None).select(COLONNES) for f in fichiers],
        how="vertical_relaxed",
    ).with_columns(
        pl.col("ts").str.to_datetime(time_zone="UTC"),
        (pl.col("ms_played") / 1000).alias("secondes"),
    )
    return (brut,)


@app.cell
def _(brut, mo, pl):
    _sans_titre = brut.filter(pl.col("master_metadata_track_name").is_null())
    _resume = brut.select(
        pl.len().alias("écoutes"),
        pl.col("ts").min().dt.date().alias("début"),
        pl.col("ts").max().dt.date().alias("fin"),
        (pl.col("secondes").sum() / 3600).round().alias("heures"),
        pl.col("master_metadata_album_artist_name").n_unique().alias("artistes"),
        pl.col("conn_country").n_unique().alias("pays"),
    )
    _qualite = pl.DataFrame({
        "cas": ["sans titre", "dont podcasts", "dont livres audio", "durée nulle"],
        "lignes": [
            _sans_titre.height,
            _sans_titre.filter(pl.col("episode_name").is_not_null()).height,
            _sans_titre.filter(pl.col("audiobook_title").is_not_null()).height,
            brut.filter(pl.col("ms_played") == 0).height,
        ],
    })
    mo.vstack([mo.md("## Volume et qualité"), _resume, _qualite])
    return


@app.cell
def _(brut, pl):
    ecoutes = brut.filter(pl.col("master_metadata_track_name").is_not_null() & (pl.col("ms_played") > 0)).with_columns(
        (pl.col("ts") - pl.duration(milliseconds=pl.col("ms_played"))).alias("debut")
    )
    return (ecoutes,)


@app.cell
def _(alt, ecoutes, mo, pl):
    _classes = ecoutes.with_columns(
        ((pl.col("secondes").log10() * 5).floor() / 5).alias("log10_s")
    ).group_by("log10_s").len(name="écoutes")
    _graphe = (
        alt.Chart(_classes)
        .mark_bar()
        .encode(
            x=alt.X("log10_s:Q", bin="binned", title="Durée écoutée (log10 des secondes)"),
            x2=alt.X2("fin:Q"),
            y=alt.Y("écoutes:Q"),
        )
        .transform_calculate(fin="datum.log10_s + 0.2")
        .properties(width=620, height=220)
    )
    _quantiles = ecoutes.select(
        pl.col("secondes").quantile(q).round(1).alias(f"q{int(q * 100)}") for q in (0.1, 0.25, 0.5, 0.75, 0.9)
    )
    mo.vstack([mo.md("## Durée écoutée\n\nDistribution bimodale : zappées ou écoutées en entier."), _graphe, _quantiles])
    return


@app.cell
def _(alt, ecoutes, mo, pl):
    _mois = ecoutes.group_by(pl.col("ts").dt.truncate("1mo").alias("mois")).agg(
        (pl.col("secondes").sum() / 3600).alias("heures")
    )
    _graphe = (
        alt.Chart(_mois)
        .mark_bar()
        .encode(x=alt.X("mois:T", title=None), y=alt.Y("heures:Q", title="Heures par mois"))
        .properties(width=620, height=180)
    )
    mo.vstack([mo.md("## Couverture temporelle"), _graphe])
    return


@app.cell
def _(ecoutes, mo, pl):
    _par_annee = (
        ecoutes.group_by(pl.col("ts").dt.year().cast(pl.String).alias("année"))
        .agg(
            pl.len().alias("écoutes"),
            pl.col("skipped").mean().round(3).alias("part_skipped"),
            pl.col("secondes").median().round(1).alias("médiane_s"),
        )
        .sort("année")
    )
    _fin = (
        ecoutes.group_by("reason_end", "skipped")
        .agg(pl.len().alias("écoutes"), pl.col("secondes").median().round(1).alias("médiane_s"))
        .sort("écoutes", descending=True)
        .head(8)
    )
    mo.vstack([mo.md("## Fiabilité de `skipped`"), _par_annee, _fin])
    return


@app.cell
def _(ecoutes, pl):
    par_artiste = (
        ecoutes.group_by(pl.col("master_metadata_album_artist_name").alias("artiste"))
        .agg(
            pl.col("secondes").sum().alias("total_s"),
            pl.len().alias("écoutes"),
            pl.col("master_metadata_track_name").n_unique().alias("titres"),
            pl.col("secondes").median().round(1).alias("médiane_s"),
            pl.col("skipped").mean().round(3).alias("part_skipped"),
            pl.col("ts").dt.year().min().alias("première_année"),
        )
        .sort("total_s", "artiste", descending=[True, False])
        .with_row_index("rang", offset=1)
        .with_columns(
            (pl.col("total_s").cum_sum() / pl.col("total_s").sum()).alias("part_cumulée"),
            (pl.col("total_s") / 3600).round(1).alias("heures"),
        )
    )
    return (par_artiste,)


@app.cell
def _(alt, mo, par_artiste, pl):
    _paliers = par_artiste.filter(pl.col("rang").is_in([1, 3, 5, 10, 50, 100, 500])).select(
        "rang", pl.col("part_cumulée").round(3)
    )
    _une_ecoute = par_artiste.filter(pl.col("écoutes") == 1).height
    # Un point sur 20 au-delà du rang 100 : la courbe reste lisible et légère.
    _points = par_artiste.filter((pl.col("rang") <= 100) | (pl.col("rang") % 20 == 0))
    _courbe = (
        alt.Chart(_points.select("rang", "part_cumulée"))
        .mark_line()
        .encode(
            x=alt.X("rang:Q", scale=alt.Scale(type="log"), title="Rang de l'artiste (log)"),
            y=alt.Y("part_cumulée:Q", axis=alt.Axis(format="%"), title="Part cumulée du temps d'écoute"),
        )
        .properties(width=620, height=220)
    )
    mo.vstack([
        mo.md(f"""
    ## Artistes · concentration

    **{par_artiste.height}** artistes, dont **{_une_ecoute}** écoutés une seule fois.
    """),
        _courbe,
        _paliers,
    ])
    return


@app.cell
def _(alt, mo, par_artiste):
    _top = par_artiste.head(15)
    _barres = (
        alt.Chart(_top)
        .mark_bar()
        .encode(
            x=alt.X("heures:Q", title="Heures d'écoute"),
            y=alt.Y("artiste:N", sort=None, title=None),
            tooltip=["artiste", "heures", "écoutes", "titres", "médiane_s"],
        )
        .properties(width=560, height=320)
    )
    mo.vstack([
        mo.md("## Artistes · classement\n\nClassement par temps d'écoute : le nombre d'écoutes favorise les morceaux zappés."),
        _barres,
        _top.select("rang", "artiste", "heures", "écoutes", "titres", "médiane_s", "part_skipped"),
    ])
    return


@app.cell
def _(alt, ecoutes, mo, par_artiste, pl):
    _noms = par_artiste.head(12)["artiste"].to_list()
    _annuel = (
        ecoutes.rename({"master_metadata_album_artist_name": "artiste"})
        .filter(pl.col("artiste").is_in(_noms))
        .group_by("artiste", pl.col("ts").dt.year().cast(pl.String).alias("année"))
        .agg((pl.col("secondes").sum() / 3600).round(1).alias("heures"))
    )
    _carte = (
        alt.Chart(_annuel)
        .mark_rect()
        .encode(
            x=alt.X("année:O", title=None),
            y=alt.Y("artiste:N", sort=_noms, title=None),
            color=alt.Color("heures:Q", scale=alt.Scale(scheme="blues"), title="Heures"),
            tooltip=["artiste", "année", "heures"],
        )
        .properties(width=420, height=300)
    )
    mo.vstack([mo.md("## Artistes · évolution\n\nLes artistes les plus écoutés le sont-ils toutes les années ? 2021 ne couvre que trois mois."), _carte])
    return


@app.cell
def _(ecoutes, mo, par_artiste, pl):
    _premiere = par_artiste.select("artiste", "première_année")
    _renouvellement = (
        ecoutes.rename({"master_metadata_album_artist_name": "artiste"})
        .with_columns(pl.col("ts").dt.year().alias("année"))
        .join(_premiere, on="artiste")
        .group_by("année")
        .agg(
            pl.len().alias("écoutes"),
            pl.col("artiste").n_unique().alias("artistes"),
            pl.col("artiste").filter(pl.col("année") == pl.col("première_année")).n_unique().alias("nouveaux"),
            (
                pl.col("secondes").filter(pl.col("année") == pl.col("première_année")).sum() / pl.col("secondes").sum()
            ).round(3).alias("part_temps_nouveaux"),
        )
        .sort("année")
        .with_columns(pl.col("année").cast(pl.String))
    )
    mo.vstack([
        mo.md("""
    ## Artistes · renouvellement

    Compter les artistes favorise les périodes avec beaucoup d'écoutes : à normaliser pour comparer.
    La part de nouveaux est gonflée au début, car l'historique commence en 2021.
    """),
        _renouvellement,
    ])
    return


@app.cell
def _(alt, mo, par_artiste, pl):
    MIN_ECOUTES = 50
    _reguliers = par_artiste.filter(pl.col("écoutes") >= MIN_ECOUTES)
    _nuage = (
        alt.Chart(_reguliers)
        .mark_circle(opacity=0.6)
        .encode(
            x=alt.X("écoutes:Q", scale=alt.Scale(type="log"), title="Écoutes (log)"),
            y=alt.Y("médiane_s:Q", title="Durée médiane (s)"),
            size=alt.Size("heures:Q", title="Heures"),
            tooltip=["artiste", "écoutes", "heures", "médiane_s", "part_skipped"],
        )
        .properties(width=620, height=280)
    )
    mo.vstack([
        mo.md(f"## Artistes · manière d'écouter\n\nArtistes avec au moins {MIN_ECOUTES} écoutes : souvent lancés ne veut pas dire écoutés longtemps."),
        _nuage,
    ])
    return


@app.cell
def _(ecoutes, mo, pl):
    _doublons =ecoutes.select("ts", "master_metadata_track_name", "ms_played").is_duplicated().sum()
    _pays = ecoutes.group_by("conn_country").len(name="écoutes").sort("écoutes", descending=True)
    mo.vstack([mo.md(f"## Doublons et pays\n\nLignes identiques (fin, titre, durée) : **{_doublons}**."), _pays])
    return


@app.cell
def _(mo):
    mo.md("""
    ## Décision

    - Garder les fichiers `Audio` et les morceaux de musique, de durée non nulle.
    - Début d'écoute = `ts − ms_played`, car `ts` marque la **fin** en UTC.
    - Ne jamais charger `ip_addr` ni les identifiants.
    - Montrer la durée médiane à côté de `skipped`, qui varie fortement selon l'année et contredit parfois `reason_end`.
    - Garder les lignes identiques (0,4 %) : rien ne prouve que ce soient des erreurs.
    - Prévoir une heure locale par pays : `ts` est en UTC et plusieurs pays apparaissent.
    - Classer les artistes par temps d'écoute, pas par nombre d'écoutes.
    - Pas de couleur par artiste : plus de 5 500 artistes, le premier ne pèse que 3 % du temps et le top 10, 16 %. Réserver la couleur à une petite sélection, le reste en neutre.
    - Laisser choisir cette sélection : aucun petit groupe d'artistes ne résume l'écoute.
    - Normaliser toute mesure de diversité : le nombre d'artistes dépend du volume d'écoutes.
    """)
    return


if __name__ == "__main__":
    app.run()
