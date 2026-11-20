/* Outils partagés par les maquettes : éléments SVG, données inventées, fond de carte. */
;(function () {
  const NS = 'http://www.w3.org/2000/svg'

  const C = {
    fond: '#eceae4',
    trait: '#d3d0c8',
    marque: '#6b6b6b',
    clair: '#b8b5ad',
    pale: '#e3e0d8',
    texte: '#666',
    accent: '#d9480f',
  }

  function el(parent, tag, attrs = {}, texte) {
    const noeud = document.createElementNS(NS, tag)
    for (const [cle, valeur] of Object.entries(attrs)) noeud.setAttribute(cle, valeur)
    if (texte !== undefined) noeud.textContent = texte
    parent.appendChild(noeud)
    return noeud
  }

  // Graine fixe : la maquette est identique à chaque ouverture
  function alea(graine) {
    let etat = graine
    return () => (etat = (etat * 16807) % 2147483647) / 2147483647
  }

  // Gris du clair (t = 0) au foncé (t = 1), pour les encodages par luminance
  function gris(t) {
    const v = Math.round(240 - t * 190)
    return `rgb(${v},${v},${v - 4})`
  }

  // Secteur d'anneau, angles en radians, 0 en haut, sens horaire
  function secteur(cx, cy, r0, r1, a0, a1) {
    const point = (r, a) => `${(cx + r * Math.sin(a)).toFixed(2)} ${(cy - r * Math.cos(a)).toFixed(2)}`
    const grand = a1 - a0 > Math.PI ? 1 : 0
    return (
      `M${point(r1, a0)} A${r1} ${r1} 0 ${grand} 1 ${point(r1, a1)} ` +
      `L${point(r0, a1)} A${r0} ${r0} 0 ${grand} 0 ${point(r0, a0)} Z`
    )
  }

  function chemin(points) {
    return points.map((p, i) => `${i ? 'L' : 'M'}${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')
  }

  const VILLES = [
    { x: 150, y: 140, nom: 'Ville A', poids: 1 },
    { x: 290, y: 100, nom: 'Ville B', poids: 0.5 },
    { x: 80, y: 205, nom: 'Ville C', poids: 0.35 },
  ]

  // Carte de 400 × 260 : un lac, une frontière, trois villes
  function fondCarte(svg) {
    el(svg, 'rect', { width: 400, height: 260, fill: C.fond })
    el(svg, 'path', {
      d: 'M24 236 C 70 208, 120 244, 168 224 S 232 214, 240 252',
      fill: 'none',
      stroke: C.trait,
      'stroke-width': 12,
      'stroke-linecap': 'round',
    })
    el(svg, 'path', {
      d: 'M0 58 L 70 50 L 140 74 L 225 40 L 315 62 L 400 32',
      fill: 'none',
      stroke: C.trait,
      'stroke-dasharray': '5 4',
    })
    for (const v of VILLES) {
      el(svg, 'text', { x: v.x + 10, y: v.y - 24, 'font-size': 10, fill: C.clair }, v.nom)
    }
  }

  // Lieux inventés autour des villes ; artiste = indice de l'artiste dominant
  function lieux() {
    const r = alea(11)
    return VILLES.flatMap((v) =>
      Array.from({ length: Math.round(12 * v.poids) + 2 }, (_, i) => ({
        x: v.x + (i ? (r() - 0.5) * 90 * Math.sqrt(v.poids) : 0),
        y: v.y + (i ? (r() - 0.5) * 60 * Math.sqrt(v.poids) : 0),
        heures: (i ? 4 + r() * 50 : 260) * v.poids,
        artiste: Math.floor(r() * 10),
      })),
    )
  }

  // Trajets inventés entre les villes, 13 points chacun
  function trajets() {
    const r = alea(23)
    const paires = [
      [0, 1],
      [0, 2],
      [0, 1],
      [1, 2],
      [0, 2],
    ]
    return paires.map(([a, b], k) => {
      const depart = VILLES[a]
      const arrivee = VILLES[b]
      const courbure = (k - 2) * 14
      return Array.from({ length: 13 }, (_, i) => {
        const t = i / 12
        const bosse = Math.sin(t * Math.PI) * courbure
        return {
          x: depart.x + (arrivee.x - depart.x) * t + bosse + (r() - 0.5) * 4,
          y: depart.y + (arrivee.y - depart.y) * t - bosse + (r() - 0.5) * 4,
        }
      })
    })
  }

  window.M = { C, el, alea, gris, secteur, chemin, fondCarte, lieux, trajets }
})()
