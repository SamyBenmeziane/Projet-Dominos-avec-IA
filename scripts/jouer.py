"""Lance une partie Humain vs IA (en ligne de commande).

Usage :
    python -m scripts.jouer --niveau IA2_pip
    python -m scripts.jouer --niveau IA5_mixte --joueur-commence
"""
import argparse
import sys
from pathlib import Path

# Permet l'import en lançant depuis la racine
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ia.factory import creer_ia, NIVEAUX
from src.joueur import JoueurHumain
from src.partie import Partie
from src.tournoi.configurations import configurations_par_defaut


def main():
    parser = argparse.ArgumentParser(description="Domino 10|10 — Humain vs IA")
    parser.add_argument(
        "--niveau",
        choices=NIVEAUX,
        default="IA2_pip",
        help="Niveau de l'IA adversaire",
    )
    parser.add_argument(
        "--config-idx",
        type=int,
        default=0,
        help="Index de la configuration à jouer (0-14)",
    )
    parser.add_argument(
        "--variante",
        type=str,
        default="v0",
        help="Variante (v0/v1/v2)",
    )
    parser.add_argument(
        "--joueur-commence",
        action="store_true",
        help="Force l'humain à recevoir Main_alpha (donc à commencer)",
    )
    args = parser.parse_args()

    chemin_cfg = Path("resultats") / "configurations.json"
    configs = configurations_par_defaut(chemin_cfg)
    cfg = configs[args.config_idx]
    var = next(v for v in cfg.variantes if v.id == args.variante)

    if args.joueur_commence:
        main_h, main_ia = list(var.main_alpha), list(var.main_beta)
    else:
        main_h, main_ia = list(var.main_beta), list(var.main_alpha)

    humain = JoueurHumain("Humain", main_h)
    ia = creer_ia(args.niveau, args.niveau, main_ia)

    print(f"=== Partie : Humain vs {args.niveau} ===")
    print(f"Configuration : {cfg.id} ({cfg.type}), variante {var.id}")
    print(f"Votre main contient {len(main_h)} dominos.")
    print(f"Pips initiaux : Humain={sum(d.pips() for d in main_h)} | IA={sum(d.pips() for d in main_ia)}")

    partie = Partie(humain, ia)
    print(f"\n{partie.joueur_courant.nom} commence.\n")
    u = partie.jouer_jusqua_fin(verbose=True)

    print("\n=== Fin de partie ===")
    print(f"Plateau final : {partie.plateau}")
    print(f"Pips restants : Humain={humain.somme_pips()} | IA={ia.somme_pips()}")
    if u == 1:
        gagnant = humain.nom if humain is partie.joueur1 else ia.nom
    elif u == -1:
        gagnant = ia.nom if ia is partie.joueur2 else humain.nom
    else:
        gagnant = None
    print("Vainqueur :", gagnant if gagnant else "égalité")


if __name__ == "__main__":
    main()
