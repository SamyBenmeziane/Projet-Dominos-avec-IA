"""Génère les graphiques matplotlib à partir du CSV du tournoi.

Usage :
    python -m scripts.tracer_graphes --csv resultats/tournoi.csv
"""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import math

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def charger_csv(chemin: Path) -> list[dict]:
    with open(chemin, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _ic_95_proportion(p: float, n: int) -> float:
    """Demi-largeur de l'intervalle de confiance a 95% (approximation normale)."""
    if n <= 0:
        return 0.0
    return 1.96 * math.sqrt(p * (1 - p) / n)


def matrice_taux_victoire(rows: list[dict]) -> tuple[list[str], list[list[float]]]:
    """Construit la matrice taux de victoire : cellule (i, j) = taux victoire de i contre j.

    On remplit a la fois (a, b) et (b, a) par symetrie : si A gagne 34% contre B,
    alors B gagne (1 - 34% - taux_nul) contre A.
    """
    couples = defaultdict(lambda: {"n": 0, "A": 0, "B": 0})
    niveaux: set[str] = set()
    for r in rows:
        a, b = r["couple"].split("__vs__")
        niveaux.add(a)
        niveaux.add(b)
        couples[(a, b)]["n"] += 1
        if r["vainqueur"] == "A":
            couples[(a, b)]["A"] += 1
        elif r["vainqueur"] == "B":
            couples[(a, b)]["B"] += 1
    niveaux_l = sorted(niveaux)
    n = len(niveaux_l)
    mat = [[float("nan")] * n for _ in range(n)]
    idx = {nv: i for i, nv in enumerate(niveaux_l)}
    for (a, b), data in couples.items():
        if data["n"] == 0:
            continue
        # cellule (a, b) : taux victoire de a (= role A dans ce couple)
        mat[idx[a]][idx[b]] = data["A"] / data["n"]
        # cellule (b, a) : taux victoire de b (= role B dans ce couple)
        mat[idx[b]][idx[a]] = data["B"] / data["n"]
    return niveaux_l, mat


def tracer_heatmap_victoires(rows: list[dict], sortie: Path):
    niveaux, mat = matrice_taux_victoire(rows)
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(mat, cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks(range(len(niveaux)))
    ax.set_yticks(range(len(niveaux)))
    ax.set_xticklabels(niveaux, rotation=45, ha="right")
    ax.set_yticklabels(niveaux)
    ax.set_xlabel("Adversaire (B)")
    ax.set_ylabel("Joueur (A)")
    ax.set_title("Taux de victoire de A vs B")
    for i in range(len(niveaux)):
        for j in range(len(niveaux)):
            v = mat[i][j]
            if v == v:  # not nan
                ax.text(j, i, f"{v:.0%}", ha="center", va="center", color="black")
    fig.colorbar(im, ax=ax, label="Taux de victoire de A")
    fig.tight_layout()
    fig.savefig(sortie, dpi=120)
    plt.close(fig)


def tracer_avantage_premier(rows: list[dict], sortie: Path):
    par_couple = defaultdict(lambda: {"n": 0, "starter_wins": 0})
    for r in rows:
        c = r["couple"]
        par_couple[c]["n"] += 1
        if r["vainqueur"] == r["starter"]:
            par_couple[c]["starter_wins"] += 1
    couples = sorted(par_couple.keys())
    taux = [par_couple[c]["starter_wins"] / par_couple[c]["n"] for c in couples]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(len(couples)), taux, color="steelblue")
    ax.axhline(0.5, color="red", linestyle="--", label="50% (pas d'avantage)")
    moyenne = sum(taux) / len(taux)
    ax.axhline(moyenne, color="green", linestyle=":", label=f"Moyenne globale = {moyenne:.1%}")
    ax.set_xticks(range(len(couples)))
    ax.set_xticklabels([c.replace("__vs__", "\nvs\n") for c in couples], fontsize=8)
    ax.set_ylabel("Taux de victoire du starter")
    ax.set_title("Avantage du premier joueur (starter) par couple")
    ax.legend()
    # zoom pour voir les differences (les valeurs sont entre ~0.55 et 0.60)
    ax.set_ylim(0.45, 0.70)
    for i, t in enumerate(taux):
        ax.text(i, t + 0.005, f"{t:.1%}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(sortie, dpi=120)
    plt.close(fig)


def tracer_duree_moyenne(rows: list[dict], sortie: Path):
    par_couple = defaultdict(list)
    for r in rows:
        par_couple[r["couple"]].append(float(r["duree_s"]))
    couples = sorted(par_couple.keys())
    moy = [sum(par_couple[c]) / len(par_couple[c]) for c in couples]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(couples)), moy, color="orange")
    ax.set_xticks(range(len(couples)))
    ax.set_xticklabels([c.replace("__vs__", "\nvs\n") for c in couples], fontsize=8)
    ax.set_ylabel("Durée moyenne (s) — échelle log")
    ax.set_yscale("log")
    ax.set_title("Temps moyen par partie")
    for i, t in enumerate(moy):
        ax.text(i, t * 1.1, f"{t:.2f}s", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(sortie, dpi=120)
    plt.close(fig)


def tracer_classement_global(rows: list[dict], sortie: Path):
    """Bar chart du taux de victoire global de chaque IA (toutes oppositions confondues)."""
    victoires = defaultdict(int)
    parties = defaultdict(int)
    for r in rows:
        a, b = r["couple"].split("__vs__")
        parties[a] += 1
        parties[b] += 1
        if r["vainqueur"] == "A":
            victoires[a] += 1
        elif r["vainqueur"] == "B":
            victoires[b] += 1
    niveaux = sorted(parties.keys())
    taux = [victoires[n] / parties[n] for n in niveaux]
    ic = [_ic_95_proportion(victoires[n] / parties[n], parties[n]) for n in niveaux]

    # Tri decroissant
    pairs = sorted(zip(niveaux, taux, ic), key=lambda x: -x[1])
    niveaux_t, taux_t, ic_t = zip(*pairs)

    fig, ax = plt.subplots(figsize=(11, 6))
    couleurs = ["#27ae60" if t >= 0.5 else "#e74c3c" if t < 0.3 else "#f39c12" for t in taux_t]
    bars = ax.bar(range(len(niveaux_t)), taux_t, color=couleurs, yerr=ic_t, capsize=6, ecolor="black")
    ax.axhline(0.5, color="gray", linestyle=":", linewidth=1, label="50% (parite)")
    ax.set_xticks(range(len(niveaux_t)))
    ax.set_xticklabels(niveaux_t, rotation=20, ha="right", fontsize=10)
    ax.set_ylabel("Taux de victoire global (toutes oppositions confondues)")
    ax.set_title("Classement global des IA — taux de victoire ± IC 95%")
    ax.set_ylim(0, 1)
    for i, (t, ci) in enumerate(zip(taux_t, ic_t)):
        ax.text(i, t + ci + 0.02, f"{t:.1%}\n±{ci:.1%}", ha="center", va="bottom", fontsize=9)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(sortie, dpi=120)
    plt.close(fig)


def tracer_triangle_non_transitif(rows: list[dict], sortie: Path):
    """Visualisation du triangle Pip → Blocage → Protect → Pip (rock-paper-scissors)."""
    couples_data = defaultdict(lambda: {"n": 0, "wins": defaultdict(int)})
    for r in rows:
        a, b = r["couple"].split("__vs__")
        cle = frozenset({a, b})
        couples_data[cle]["n"] += 1
        if r["vainqueur"] == "A":
            couples_data[cle]["wins"][a] += 1
        elif r["vainqueur"] == "B":
            couples_data[cle]["wins"][b] += 1

    # Cherche specifiquement IA2_pip, IA3_blocage, IA4_protect
    cibles = ["IA2_pip", "IA3_blocage", "IA4_protect"]
    if not all(any(c in r["couple"] for r in rows) for c in cibles):
        return

    # Calcul des taux de chaque opposition
    def taux(a, b):
        cle = frozenset({a, b})
        if cle not in couples_data:
            return 0.0, 0
        d = couples_data[cle]
        n = d["n"]
        wa = d["wins"].get(a, 0)
        return wa / n if n else 0.0, n

    fig, ax = plt.subplots(figsize=(9, 8))
    ax.set_aspect("equal")
    ax.axis("off")

    # Positions en triangle
    positions = {
        "IA2_pip": (0.5, 0.85),
        "IA3_blocage": (0.15, 0.25),
        "IA4_protect": (0.85, 0.25),
    }
    couleurs_strat = {
        "IA2_pip": "#3498db",
        "IA3_blocage": "#e74c3c",
        "IA4_protect": "#27ae60",
    }

    # Cercles pour chaque IA
    for nom, (x, y) in positions.items():
        circle = plt.Circle((x, y), 0.10, color=couleurs_strat[nom], zorder=2)
        ax.add_patch(circle)
        ax.text(x, y, nom.split("_")[1], ha="center", va="center",
                color="white", fontsize=12, fontweight="bold", zorder=3)

    # Fleches : pour chaque paire, on dessine une fleche du gagnant vers le perdant
    paires = [("IA2_pip", "IA3_blocage"), ("IA3_blocage", "IA4_protect"), ("IA4_protect", "IA2_pip")]
    for a, b in paires:
        ta, n = taux(a, b)
        tb = 1 - ta - 0  # approximatif : on suppose peu de nuls
        if ta >= 0.5:
            gagnant, perdant = a, b
            taux_g = ta
        else:
            gagnant, perdant = b, a
            taux_g = 1 - ta
        x1, y1 = positions[gagnant]
        x2, y2 = positions[perdant]
        # vecteur normalise pour partir/arriver au bord du cercle
        dx, dy = x2 - x1, y2 - y1
        d = (dx ** 2 + dy ** 2) ** 0.5
        rx, ry = dx / d, dy / d
        x1b, y1b = x1 + 0.10 * rx, y1 + 0.10 * ry
        x2b, y2b = x2 - 0.13 * rx, y2 - 0.13 * ry

        # Couleur fleche : verte si significatif (ecart >= 13%), grise sinon
        ecart = abs(taux_g - 0.5) * 2
        couleur_fleche = "#16a085" if ecart >= 0.13 else "#7f8c8d"
        style = "-" if ecart >= 0.13 else "--"

        ax.annotate(
            "", xy=(x2b, y2b), xytext=(x1b, y1b),
            arrowprops=dict(arrowstyle="-|>", color=couleur_fleche, lw=2.5, linestyle=style)
        )
        # Label sur la fleche
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        signif = "✓" if ecart >= 0.13 else "≈ bruit"
        ax.text(mx, my, f"{taux_g:.1%}\n{signif}", ha="center", va="center",
                fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black"))

    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("Triangle non-transitif (rock-paper-scissors) entre les 3 stratégies pures\n"
                 "(flèche = direction de victoire ; vert = significatif, gris pointillé = bruit statistique)",
                 fontsize=11)
    legend_items = [
        mpatches.Patch(color="#16a085", label="Domination significative (écart ≥ 13%)"),
        mpatches.Patch(color="#7f8c8d", label="Bruit statistique (écart < 13%)"),
    ]
    ax.legend(handles=legend_items, loc="lower center", bbox_to_anchor=(0.5, -0.02), ncol=2)
    fig.tight_layout()
    fig.savefig(sortie, dpi=120)
    plt.close(fig)


def tracer_significativite(rows: list[dict], sortie: Path):
    """Heatmap des ecarts d'IA (taux A − 50%), avec hachures pour les resultats non significatifs."""
    couples = defaultdict(lambda: {"n": 0, "A": 0})
    niveaux: set[str] = set()
    for r in rows:
        a, b = r["couple"].split("__vs__")
        niveaux.add(a)
        niveaux.add(b)
        couples[(a, b)]["n"] += 1
        if r["vainqueur"] == "A":
            couples[(a, b)]["A"] += 1
    niveaux_l = sorted(niveaux)
    n_lvl = len(niveaux_l)
    idx = {nv: i for i, nv in enumerate(niveaux_l)}
    mat = [[float("nan")] * n_lvl for _ in range(n_lvl)]
    sig = [[False] * n_lvl for _ in range(n_lvl)]
    for (a, b), d in couples.items():
        if d["n"] == 0:
            continue
        taux_a = d["A"] / d["n"]
        ic = _ic_95_proportion(taux_a, d["n"])
        mat[idx[a]][idx[b]] = taux_a
        mat[idx[b]][idx[a]] = 1 - taux_a
        # significatif si l'IC ne contient pas 0.5
        signif = (taux_a - ic > 0.5) or (taux_a + ic < 0.5)
        sig[idx[a]][idx[b]] = signif
        sig[idx[b]][idx[a]] = signif

    fig, ax = plt.subplots(figsize=(9, 7))
    im = ax.imshow(mat, cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks(range(n_lvl))
    ax.set_yticks(range(n_lvl))
    ax.set_xticklabels(niveaux_l, rotation=30, ha="right")
    ax.set_yticklabels(niveaux_l)
    ax.set_xlabel("Adversaire (B)")
    ax.set_ylabel("Joueur (A)")
    ax.set_title("Matrice de domination — vert = significatif à 95%, hachures = bruit statistique")
    for i in range(n_lvl):
        for j in range(n_lvl):
            v = mat[i][j]
            if v != v:  # NaN
                continue
            if not sig[i][j]:
                # Ajout de hachures pour les non-significatifs
                rect = mpatches.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                          fill=False, hatch="///", edgecolor="black", linewidth=0)
                ax.add_patch(rect)
            ax.text(j, i, f"{v:.0%}", ha="center", va="center",
                    color="black", fontsize=10, fontweight="bold")
    fig.colorbar(im, ax=ax, label="Taux victoire de A")
    fig.tight_layout()
    fig.savefig(sortie, dpi=120)
    plt.close(fig)


def tracer_par_type_config(rows: list[dict], sortie: Path):
    """Performances de chaque IA selon le type de configuration (ouverte/fermee/etc.)."""
    types = sorted(set(r["type_config"] for r in rows))
    niveaux = sorted(set(n for r in rows for n in r["couple"].split("__vs__")))

    # Pour chaque (niveau, type), taux victoire global
    data = defaultdict(lambda: defaultdict(lambda: {"n": 0, "wins": 0}))
    for r in rows:
        a, b = r["couple"].split("__vs__")
        t = r["type_config"]
        data[a][t]["n"] += 1
        data[b][t]["n"] += 1
        if r["vainqueur"] == "A":
            data[a][t]["wins"] += 1
        elif r["vainqueur"] == "B":
            data[b][t]["wins"] += 1

    fig, ax = plt.subplots(figsize=(12, 6))
    largeur = 0.15
    x = list(range(len(types)))
    couleurs_iaf = ["#95a5a6", "#3498db", "#e74c3c", "#27ae60", "#9b59b6"]
    for i, niveau in enumerate(niveaux):
        taux = [
            data[niveau][t]["wins"] / data[niveau][t]["n"] if data[niveau][t]["n"] > 0 else 0
            for t in types
        ]
        positions = [xi + (i - len(niveaux) / 2) * largeur for xi in x]
        ax.bar(positions, taux, largeur, label=niveau, color=couleurs_iaf[i % len(couleurs_iaf)])
    ax.axhline(0.5, color="gray", linestyle=":", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(types, rotation=15, ha="right")
    ax.set_xlabel("Type de configuration")
    ax.set_ylabel("Taux de victoire")
    ax.set_title("Performance de chaque IA selon le type de configuration")
    ax.set_ylim(0, 1)
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(sortie, dpi=120)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Trace les graphiques du tournoi")
    parser.add_argument("--csv", type=Path, default=Path("resultats/tournoi.csv"))
    parser.add_argument("--sortie-dir", type=Path, default=Path("resultats"))
    args = parser.parse_args()

    rows = charger_csv(args.csv)
    args.sortie_dir.mkdir(parents=True, exist_ok=True)
    tracer_heatmap_victoires(rows, args.sortie_dir / "heatmap_victoires.png")
    tracer_avantage_premier(rows, args.sortie_dir / "avantage_premier_joueur.png")
    tracer_duree_moyenne(rows, args.sortie_dir / "duree_moyenne.png")
    tracer_classement_global(rows, args.sortie_dir / "classement_global.png")
    tracer_triangle_non_transitif(rows, args.sortie_dir / "triangle_non_transitif.png")
    tracer_significativite(rows, args.sortie_dir / "significativite_statistique.png")
    tracer_par_type_config(rows, args.sortie_dir / "performance_par_type_config.png")
    print(f"Graphiques sauvegardés dans {args.sortie_dir}/")


if __name__ == "__main__":
    main()
