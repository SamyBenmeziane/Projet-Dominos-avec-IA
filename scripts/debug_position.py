"""Debug : reproduire la position critique du tour 14 de la partie ouverte_01 / v0
et examiner ce que IA3_blocage calcule pour chaque coup possible."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.domino import Domino
from src.ia.evaluation import f_blocage
from src.ia.ia_aleatoire import IAAleatoire
from src.ia.ia_minimax import IAMinimax
from src.partie import Partie
from src.tournoi.configurations import generer_configurations


def main():
    # Charger la config exacte du screenshot
    configs = generer_configurations(seed=42)
    ouverte_01 = next(c for c in configs if c.id == "ouverte_01")
    v0 = next(v for v in ouverte_01.variantes if v.id == "v0")

    # En mode Humain vs IA3 sans swap : Humain = main_alpha (a le 10|10)
    humain = IAAleatoire("Humain", list(v0.main_alpha), seed=42)
    ia3 = IAMinimax("IA3", list(v0.main_beta), profondeur=6,
                    eval_fn=f_blocage, alpha_beta=True, ordering=True)
    p = Partie(humain, ia3)

    # Reproduire les 13 premiers coups de l'historique
    moves = [
        ("Humain", Domino(10, 10), "gauche"),
        ("IA3", Domino(4, 10), "gauche"),
        ("Humain", Domino(4, 4), "gauche"),
        ("IA3", Domino(8, 10), "droite"),
        ("Humain", Domino(8, 8), "droite"),
        ("IA3", Domino(4, 8), "droite"),
        ("Humain", Domino(4, 5), "gauche"),
        ("IA3", Domino(5, 10), "gauche"),
        ("Humain", Domino(3, 4), "droite"),
        ("IA3", Domino(3, 10), "droite"),
        ("Humain", Domino(1, 10), "gauche"),
        ("IA3", Domino(1, 4), "gauche"),
        ("Humain", Domino(0, 10), "droite"),
    ]
    for nom, d, pos in moves:
        ok = p.jouer_coup(d, pos)
        if not ok:
            print(f"!!! Coup illegal : {nom} {d} {pos}")
            print(f"    plateau ext = {p.plateau.extremite_gauche}, {p.plateau.extremite_droite}")
            print(f"    main de {p.joueur_courant.nom} : {p.joueur_courant.main}")
            return

    print(f"Plateau ext: gauche={p.plateau.extremite_gauche}, droite={p.plateau.extremite_droite}")
    print(f"Joueur courant: {p.joueur_courant.nom}")
    print(f"Main IA3 ({len(ia3.main)} dominos) : {sorted(ia3.main, key=lambda d: (d.a, d.b))}")
    print()

    # Pour chaque coup possible, calculer le score immediat ET le score minimax
    coups = p.plateau.coups_possibles(p.joueur_courant.main)
    print(f"=== {len(coups)} coups possibles pour IA3 ===")
    print(f"{'Coup':<20} {'Immediate':>12} {'Minimax depth 5':>20}")
    print("-" * 60)

    resultats = []
    for d, pos in coups:
        p_test = p.cloner()
        p_test.jouer_coup(d, pos)
        immediate = f_blocage(p_test, 2)  # max_id=2 car IA3 = joueur2
        # Minimax depuis l'etat post-coup avec prof=5 (le coup deja joue)
        ia3_sim = IAMinimax("sim", [], profondeur=5, eval_fn=f_blocage,
                            alpha_beta=True, ordering=True)
        val = ia3_sim._minimax(p_test, 5, -math.inf, math.inf, 2)
        resultats.append((d, pos, immediate, val))
        coup_str = f"{d} a {pos}"
        print(f"{coup_str:<20} {immediate:>12.1f} {val:>20.1f}")

    print()
    # Trier par minimax
    resultats.sort(key=lambda r: -r[3])
    print("=== Classement par score minimax ===")
    for i, (d, pos, imm, val) in enumerate(resultats, 1):
        marker = " <-- choix optimal" if i == 1 else ""
        print(f"{i:2d}. {d} a {pos:7s}  immediate={imm:7.1f}  minimax={val:7.1f}{marker}")


if __name__ == "__main__":
    main()
