"""Tests unitaires du moteur Partie."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.domino import Domino
from src.partie import Partie
from src.ia.ia_aleatoire import IAAleatoire


def test_premier_joueur_est_celui_avec_le_plus_fort_double():
    main_a = [Domino(10, 10), Domino(0, 1), Domino(2, 3)]
    main_b = [Domino(9, 9), Domino(1, 2), Domino(3, 4)]
    j1 = IAAleatoire("J1", main_a, seed=0)
    j2 = IAAleatoire("J2", main_b, seed=1)
    p = Partie(j1, j2)
    assert p.joueur_courant is j1


def test_coup_force_premier_tour_pose_le_plus_fort_double():
    main_a = [Domino(10, 10), Domino(8, 8), Domino(0, 1)]
    main_b = [Domino(9, 9), Domino(2, 3), Domino(4, 5)]
    j1 = IAAleatoire("J1", main_a, seed=0)
    j2 = IAAleatoire("J2", main_b, seed=1)
    p = Partie(j1, j2)
    forced = p.coup_force()
    assert forced is not None
    assert forced[0] == Domino(10, 10)


def test_partie_terminee_quand_joueur_vide_sa_main():
    main_a = [Domino(5, 5)]
    main_b = [Domino(0, 0), Domino(1, 1)]
    j1 = IAAleatoire("J1", main_a, seed=0)
    j2 = IAAleatoire("J2", main_b, seed=1)
    p = Partie(j1, j2)
    p.jouer_tour()  # j1 pose 5|5
    assert p.est_terminee()
    assert p.utility() == 1


def test_utility_blocage_recompense_le_moins_pips():
    # Construction d'une situation forcee de blocage
    main_a = [Domino(10, 10), Domino(0, 0)]  # 20 pips
    main_b = [Domino(9, 9), Domino(1, 1), Domino(2, 2)]  # 24 pips
    j1 = IAAleatoire("J1", main_a, seed=0)
    j2 = IAAleatoire("J2", main_b, seed=1)
    p = Partie(j1, j2)
    p.jouer_tour()  # J1 force 10|10 -> extremites 10 / 10
    # J2 ne peut pas raccorder (n'a aucun 10)
    # J1 peut-il jouer ? il lui reste 0|0 qui ne contient pas 10 -> non
    # blocage
    while not p.est_terminee():
        cont = p.jouer_tour()
        if not cont:
            break
    assert p.est_terminee()
    # J1 a moins de pips (0+0=0 apres avoir pose 10|10) que J2 (9+9+1+1+2+2=24)
    # mais attention : a la fin J1 a juste 0|0 = 0 pips, J2 a 24 pips -> J1 gagne
    assert p.utility() == 1


def test_clonage_partie_independant():
    main_a = [Domino(10, 10), Domino(5, 5)]
    main_b = [Domino(9, 9), Domino(4, 4)]
    j1 = IAAleatoire("J1", main_a, seed=0)
    j2 = IAAleatoire("J2", main_b, seed=1)
    p = Partie(j1, j2)
    p2 = p.cloner()
    p.jouer_tour()
    assert p.plateau.vide is False
    assert p2.plateau.vide is True


def test_clonage_independance_des_mains():
    """Verifie que muter la main du clone n'affecte pas l'original."""
    main_a = [Domino(10, 10), Domino(5, 5), Domino(3, 7)]
    main_b = [Domino(9, 9), Domino(4, 4)]
    j1 = IAAleatoire("J1", main_a, seed=0)
    j2 = IAAleatoire("J2", main_b, seed=1)
    p = Partie(j1, j2)
    p_clone = p.cloner()
    # Mutation sur le clone
    p_clone.joueur1.retirer(Domino(10, 10))
    # L'original ne doit pas etre affecte
    assert Domino(10, 10) in p.joueur1.main
    assert Domino(10, 10) not in p_clone.joueur1.main
    # Inversement
    p.joueur1.retirer(Domino(5, 5))
    assert Domino(5, 5) in p_clone.joueur1.main


def test_clonage_independance_du_plateau():
    main_a = [Domino(10, 10), Domino(0, 10)]
    main_b = [Domino(9, 9)]
    j1 = IAAleatoire("J1", main_a, seed=0)
    j2 = IAAleatoire("J2", main_b, seed=1)
    p = Partie(j1, j2)
    p.jouer_tour()  # j1 pose le 10|10 force
    p_clone = p.cloner()
    # joueur courant : j2, mais sans coup possible -> changera apres jouer_tour
    p.jouer_tour()  # j2 passe
    p.jouer_tour()  # j1 pose 0|10
    assert len(p.plateau.dominos_poses) == 2
    assert len(p_clone.plateau.dominos_poses) == 1


def test_clonage_courant_pointe_sur_clone():
    main_a = [Domino(10, 10)]
    main_b = [Domino(9, 9)]
    j1 = IAAleatoire("J1", main_a, seed=0)
    j2 = IAAleatoire("J2", main_b, seed=1)
    p = Partie(j1, j2)
    clone = p.cloner()
    # Le courant du clone doit etre le clone du joueur, PAS l'original
    assert clone.joueur_courant is clone.joueur1
    assert clone.joueur_courant is not p.joueur_courant
