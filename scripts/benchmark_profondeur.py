"""Benchmark : nombre de noeuds explores et temps de calcul en fonction
de la profondeur Minimax, avec et sans alpha-beta + move ordering.

On mesure UN SEUL coup d'IA (le premier coup non-force apres le 10|10),
sur la meme position de depart, en faisant varier la profondeur de 2 a 6.

Usage :
    python -m scripts.benchmark_profondeur
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt

from src.domino import Domino
from src.ia.evaluation import f_pip
from src.ia.ia_aleatoire import IAAleatoire
from src.ia.ia_minimax import IAMinimax
from src.partie import Partie
from src.tournoi.configurations import generer_configurations


def setup_partie(profondeur: int, alpha_beta: bool, ordering: bool, configs):
    """Construit une partie a la position juste apres le 10|10 force."""
    cfg = configs[0]
    var = cfg.variantes[0]
    main_alpha = list(var.main_alpha)
    main_beta = list(var.main_beta)
    j1 = IAAleatoire("J1", main_alpha, seed=42)
    ia = IAMinimax("IA", main_beta, profondeur=profondeur, eval_fn=f_pip,
                   alpha_beta=alpha_beta, ordering=ordering)
    p = Partie(j1, ia)
    # Humain pose le 10|10 force
    p.jouer_coup(Domino(10, 10), "gauche")
    return p, ia


def mesure_un_coup(profondeur: int, alpha_beta: bool, ordering: bool, configs):
    p, ia = setup_partie(profondeur, alpha_beta, ordering, configs)
    ia.reinit_stats()
    t0 = time.perf_counter()
    _ = ia.choisir_coup(p)
    duree = time.perf_counter() - t0
    return duree, ia._noeuds_explores, ia._coups_elagues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sortie", type=Path,
                        default=Path("resultats/noeuds_vs_profondeur.png"))
    parser.add_argument("--profondeurs", nargs="+", type=int,
                        default=[2, 3, 4, 5, 6])
    args = parser.parse_args()

    configs = generer_configurations(seed=42)
    print(f"Benchmark : Minimax + f_pip, eval pour 1 coup d'IA\n")

    print(f"{'Prof.':>5} {'Mode':<32} {'Temps':>10} {'Noeuds':>14} {'Cuts':>10}")
    print("-" * 74)

    sans_temps, sans_nodes = [], []
    ab_seul_temps, ab_seul_nodes = [], []
    avec_temps, avec_nodes = [], []

    for prof in args.profondeurs:
        # Sans alpha-beta
        d, n, c = mesure_un_coup(prof, alpha_beta=False, ordering=False, configs=configs)
        sans_temps.append(d); sans_nodes.append(n)
        print(f"{prof:>5} {'sans alpha-beta':<32} {d:>9.3f}s {n:>14,} {c:>10,}")

        # Avec alpha-beta SEULE (sans ordering)
        d, n, c = mesure_un_coup(prof, alpha_beta=True, ordering=False, configs=configs)
        ab_seul_temps.append(d); ab_seul_nodes.append(n)
        print(f"{prof:>5} {'avec alpha-beta seul':<32} {d:>9.3f}s {n:>14,} {c:>10,}")

        # Avec alpha-beta + ordering
        d, n, c = mesure_un_coup(prof, alpha_beta=True, ordering=True, configs=configs)
        avec_temps.append(d); avec_nodes.append(n)
        print(f"{prof:>5} {'avec alpha-beta + ordering':<32} {d:>9.3f}s {n:>14,} {c:>10,}")
        print()

    # ===== Graphique =====
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1 : nombre de noeuds (echelle log)
    ax = axes[0]
    ax.plot(args.profondeurs, sans_nodes, "o-", label="Sans alpha-beta",
            color="#e74c3c", linewidth=2, markersize=10)
    ax.plot(args.profondeurs, ab_seul_nodes, "^-", label="Avec alpha-beta seul",
            color="#f39c12", linewidth=2, markersize=10)
    ax.plot(args.profondeurs, avec_nodes, "s-", label="Avec alpha-beta + ordering",
            color="#27ae60", linewidth=2, markersize=10)
    ax.set_yscale("log")
    ax.set_xlabel("Profondeur Minimax")
    ax.set_ylabel("Nombre de noeuds explores (echelle log)")
    ax.set_title("Explosion exponentielle de l'arbre de recherche")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3, which="both")
    ax.set_xticks(args.profondeurs)
    for x, y in zip(args.profondeurs, sans_nodes):
        ax.annotate(f"{y:,}", xy=(x, y), xytext=(0, 8),
                    textcoords="offset points", ha="center", fontsize=7, color="#e74c3c")
    for x, y in zip(args.profondeurs, ab_seul_nodes):
        ax.annotate(f"{y:,}", xy=(x, y), xytext=(8, 0),
                    textcoords="offset points", ha="left", fontsize=7, color="#f39c12")
    for x, y in zip(args.profondeurs, avec_nodes):
        ax.annotate(f"{y:,}", xy=(x, y), xytext=(0, -14),
                    textcoords="offset points", ha="center", fontsize=7, color="#27ae60")

    # Plot 2 : temps (echelle log)
    ax = axes[1]
    ax.plot(args.profondeurs, sans_temps, "o-", label="Sans alpha-beta",
            color="#e74c3c", linewidth=2, markersize=10)
    ax.plot(args.profondeurs, ab_seul_temps, "^-", label="Avec alpha-beta seul",
            color="#f39c12", linewidth=2, markersize=10)
    ax.plot(args.profondeurs, avec_temps, "s-", label="Avec alpha-beta + ordering",
            color="#27ae60", linewidth=2, markersize=10)
    ax.set_yscale("log")
    ax.set_xlabel("Profondeur Minimax")
    ax.set_ylabel("Temps de calcul (s, echelle log)")
    ax.set_title("Temps de decision pour 1 coup")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3, which="both")
    ax.set_xticks(args.profondeurs)

    fig.suptitle("Impact de la profondeur sur la complexite de Minimax (eval = f_pip)",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(args.sortie, dpi=120)
    plt.close(fig)
    print(f"\nGraphique sauvegarde : {args.sortie}")


if __name__ == "__main__":
    main()
