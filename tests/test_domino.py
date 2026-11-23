"""Tests unitaires de la classe Domino."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from src.domino import Domino, jeu_complet


def test_creation_normalisee():
    d = Domino(7, 3)
    assert d.a == 3 and d.b == 7


def test_pips():
    assert Domino(4, 6).pips() == 10
    assert Domino(0, 0).pips() == 0


def test_est_double():
    assert Domino(5, 5).est_double()
    assert not Domino(5, 6).est_double()


def test_contient_et_autre_cote():
    d = Domino(3, 7)
    assert d.contient(3) and d.contient(7)
    assert not d.contient(5)
    assert d.autre_cote(3) == 7
    assert d.autre_cote(7) == 3
    with pytest.raises(ValueError):
        d.autre_cote(2)


def test_egalite_et_hash():
    assert Domino(2, 5) == Domino(5, 2)
    assert hash(Domino(2, 5)) == hash(Domino(5, 2))
    assert Domino(2, 5) != Domino(2, 6)


def test_valeurs_invalides():
    with pytest.raises(ValueError):
        Domino(-1, 0)
    with pytest.raises(ValueError):
        Domino(0, 11)


def test_jeu_complet_a_66_dominos_uniques():
    jeu = jeu_complet()
    assert len(jeu) == 66
    assert len(set(jeu)) == 66
    assert Domino(0, 0) in jeu
    assert Domino(10, 10) in jeu
    assert Domino(7, 3) in jeu  # Domino(3,7)
