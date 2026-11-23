"""Tests unitaires de la classe Plateau."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.domino import Domino
from src.plateau import Plateau


def test_plateau_initial_vide():
    p = Plateau()
    assert p.vide
    assert p.extremite_gauche is None
    assert p.extremite_droite is None


def test_pose_initiale_definit_les_deux_extremites():
    p = Plateau()
    p.poser(Domino(10, 10), "gauche")
    assert not p.vide
    assert p.extremite_gauche == 10
    assert p.extremite_droite == 10


def test_coups_possibles_plateau_vide_contient_tous_les_dominos():
    p = Plateau()
    main = [Domino(0, 1), Domino(2, 5)]
    coups = p.coups_possibles(main)
    assert len(coups) == 2


def test_pose_a_gauche_met_a_jour_extremite():
    p = Plateau()
    p.poser(Domino(5, 7), "gauche")  # plateau initial : [5..7]
    assert p.poser(Domino(3, 5), "gauche")  # le 5 raccorde, on garde 3 a gauche
    assert p.extremite_gauche == 3
    assert p.extremite_droite == 7


def test_pose_a_droite_met_a_jour_extremite():
    p = Plateau()
    p.poser(Domino(5, 7), "gauche")
    assert p.poser(Domino(7, 9), "droite")
    assert p.extremite_droite == 9


def test_pose_illegale_refusee():
    p = Plateau()
    p.poser(Domino(5, 7), "gauche")
    assert not p.poser(Domino(2, 4), "gauche")  # ne contient pas 5


def test_simulation_ne_modifie_pas_loriginal():
    p = Plateau()
    p.poser(Domino(5, 7), "gauche")
    p2 = p.simuler(Domino(7, 9), "droite")
    assert p.extremite_droite == 7
    assert p2.extremite_droite == 9
