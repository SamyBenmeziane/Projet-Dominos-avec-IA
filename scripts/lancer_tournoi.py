"""Lance le tournoi complet entre les 4 IA et sauvegarde les résultats.

Usage :
    python -m scripts.lancer_tournoi
    python -m scripts.lancer_tournoi --niveaux IA1_aleatoire IA2_pip
    python -m scripts.lancer_tournoi --regenerer-configs
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ia.factory import NIVEAUX
from src.tournoi.configurations import configurations_par_defaut
from src.tournoi.tournoi import jouer_tournoi, sauvegarder_csv, synthese_par_couple


def main():
    parser = argparse.ArgumentParser(description="Lance le tournoi entre IA")
    parser.add_argument(
        "--niveaux",
        nargs="+",
        choices=NIVEAUX,
        default=list(NIVEAUX),
    )
    parser.add_argument("--seed-configs", type=int, default=42)
    parser.add_argument("--seed-tournoi", type=int, default=1000)
    parser.add_argument("--regenerer-configs", action="store_true")
    parser.add_argument(
        "--sortie", type=Path, default=Path("resultats/tournoi.csv"),
    )
    parser.add_argument(
        "--max-configs",
        type=int,
        default=None,
        help="Limite le nombre de configurations utilisees (utile pour les tests rapides)",
    )
    args = parser.parse_args()

    chemin_cfg = Path("resultats") / "configurations.json"
    configs = configurations_par_defaut(
        chemin_cfg, seed=args.seed_configs, regenerer=args.regenerer_configs
    )
    if args.max_configs is not None:
        configs = configs[: args.max_configs]
    print(f"Configurations chargées : {len(configs)}")
    for c in configs:
        print(f"  - {c.id} ({c.type}) : {len(c.variantes)} variantes")

    print(f"\nLancement du tournoi entre {len(args.niveaux)} IA...")
    resultats = jouer_tournoi(
        configurations=configs,
        niveaux=tuple(args.niveaux),
        seed_base=args.seed_tournoi,
    )

    sauvegarder_csv(resultats, args.sortie)
    print(f"\n{len(resultats)} parties sauvegardées dans {args.sortie}")

    syn = synthese_par_couple(resultats)
    chemin_syn = args.sortie.with_suffix(".synthese.json")
    with open(chemin_syn, "w", encoding="utf-8") as f:
        json.dump(syn, f, indent=2)
    print(f"Synthèse : {chemin_syn}")

    print("\n=== Résumé ===")
    for couple, s in syn.items():
        print(f"{couple}")
        print(
            f"  n={s['n_parties']} | A={s['victoires_A']} ({s['taux_A']:.1%}) "
            f"| B={s['victoires_B']} ({s['taux_B']:.1%}) "
            f"| nuls={s['nuls']} | avantage starter={s['avantage_starter']:.1%} "
            f"| moy={s['duree_moyenne_s']:.2f}s/partie"
        )


if __name__ == "__main__":
    main()
