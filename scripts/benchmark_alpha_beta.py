"""Benchmark de l'impact de l'elagage alpha-beta + move ordering.

Compare :
  - Minimax brut (sans alpha-beta, sans ordering)
  - Minimax + alpha-beta seul
  - Minimax + alpha-beta + move ordering

Sur 1 partie complete avec eval = f_pip, profondeur = 4.
Genere un graphique comparatif.

Usage :
    python -m scripts.benchmark_alpha_beta
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt

from src.ia.evaluation import f_pip
from src.ia.ia_minimax import IAMinimax
from src.partie import Partie
from src.tournoi.configurations import generer_configurations


def benchmark_une_partie(profondeur: int, alpha_beta: bool, ordering: bool, configs):
    """Joue 1 partie complete et accumule les stats sur tous les coups."""
    cfg = configs[0]
    var = cfg.variantes[0]
    main_a = list(var.main_alpha)
    main_b = list(var.main_beta)
    ia_a = IAMinimax("A", main_a, profondeur=profondeur, eval_fn=f_pip,
                    alpha_beta=alpha_beta, ordering=ordering)
    ia_b = IAMinimax("B", main_b, profondeur=profondeur, eval_fn=f_pip,
                    alpha_beta=alpha_beta, ordering=ordering)
    p = Partie(ia_a, ia_b)

    nodes_total = 0
    cuts_total = 0
    t0 = time.perf_counter()
    while not p.est_terminee():
        # Avant le coup, on memorise quel joueur va jouer
        courant = p.joueur_courant
        cont = p.jouer_tour()
        if not cont:
            break
        # Apres le coup, on additionne les stats du joueur qui vient de jouer
        if hasattr(courant, "_noeuds_explores"):
            nodes_total += courant._noeuds_explores
            cuts_total += courant._coups_elagues
    duree = time.perf_counter() - t0
    return duree, nodes_total, cuts_total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sortie", type=Path, default=Path("resultats/impact_alpha_beta.png"))
    parser.add_argument("--profondeur", type=int, default=4)
    args = parser.parse_args()

    configs = generer_configurations(seed=42)
    print(f"Benchmark Minimax profondeur {args.profondeur}, eval=f_pip\n")

    configs_test = [
        ("Minimax brut\n(pas d'optim)", False, False),
        ("Minimax + alpha-beta", True, False),
        ("Minimax + alpha-beta\n+ move ordering", True, True),
    ]

    resultats = []
    for label, ab, ord_ in configs_test:
        label_court = label.replace("\n", " ")
        print(f"--- {label_court} ---")
        duree, nodes, cuts = benchmark_une_partie(args.profondeur, ab, ord_, configs)
        print(f"    Temps          : {duree:.2f}s")
        print(f"    Noeuds explores: {nodes:,}")
        print(f"    Elagages       : {cuts:,}")
        resultats.append((label, duree, nodes, cuts))
        print()

    # Graphique : 3 sous-plots cote a cote
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))

    labels = [r[0] for r in resultats]
    temps = [r[1] for r in resultats]
    nodes = [r[2] for r in resultats]
    cuts = [r[3] for r in resultats]

    couleurs = ["#e74c3c", "#f39c12", "#27ae60"]

    # Plot 1 : temps
    ax = axes[0]
    ax.bar(range(len(labels)), temps, color=couleurs)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("Temps total (secondes)")
    ax.set_title("Temps d'execution")
    for i, v in enumerate(temps):
        ax.text(i, v + max(temps) * 0.02, f"{v:.2f}s", ha="center", fontweight="bold")

    # Plot 2 : noeuds explores
    ax = axes[1]
    ax.bar(range(len(labels)), nodes, color=couleurs)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("Nombre total de noeuds explores")
    ax.set_title("Noeuds explores")
    for i, v in enumerate(nodes):
        ax.text(i, v + max(nodes) * 0.02, f"{v:,}", ha="center", fontweight="bold")

    # Plot 3 : elagages
    ax = axes[2]
    ax.bar(range(len(labels)), cuts, color=couleurs)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("Nombre d'elagages declenches")
    ax.set_title("Elagages effectues")
    for i, v in enumerate(cuts):
        ax.text(i, v + max(cuts) * 0.02 + 1, f"{v:,}", ha="center", fontweight="bold")

    fig.suptitle(f"Impact de alpha-beta et move ordering (Minimax profondeur {args.profondeur})",
                fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(args.sortie, dpi=120)
    plt.close(fig)
    print(f"\nGraphique sauvegarde : {args.sortie}")

    # Tableau recap
    print("\n=== Tableau recap ===")
    print(f"{'Configuration':<40} {'Temps':>10} {'Noeuds':>12} {'Elagages':>12}")
    print("-" * 76)
    for label, t, n, c in resultats:
        l = label.replace("\n", " ")
        print(f"{l:<40} {t:>9.2f}s {n:>12,} {c:>12,}")


if __name__ == "__main__":
    main()
