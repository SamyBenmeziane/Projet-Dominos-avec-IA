"""Tests unitaires des IA et des fonctions d'evaluation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.domino import Domino
from src.partie import Partie
from src.ia.factory import creer_ia, NIVEAUX
from src.ia.evaluation import f_pip, f_blocage, f_protect, f_mixte
from src.ia.ia_aleatoire import IAAleatoire
from src.tournoi.configurations import generer_configurations


def _petite_partie(niveau_a: str, niveau_b: str, seed: int = 0):
    configs = generer_configurations(seed=42)
    cfg = configs[0]
    var = cfg.variantes[0]
    a = creer_ia(niveau_a, "A", list(var.main_alpha), seed=seed)
    b = creer_ia(niveau_b, "B", list(var.main_beta), seed=seed + 1)
    return Partie(a, b)


def _partie_avec_plateau(main_max, main_min, plateau_domino, plateau_pos="gauche"):
    """Construit une partie avec un domino deja pose sur le plateau."""
    j1 = IAAleatoire("J1", main_max, seed=0)
    j2 = IAAleatoire("J2", main_min, seed=1)
    p = Partie(j1, j2)
    p.plateau.poser(plateau_domino, plateau_pos)
    return p


# -------- Tests des IA (integration) --------

def test_chaque_niveau_produit_un_coup_legal_au_premier_tour():
    for niveau in NIVEAUX:
        for niveau_b in NIVEAUX:
            p = _petite_partie(niveau, niveau_b)
            cont = p.jouer_tour()
            assert cont
            assert not p.plateau.vide


def test_partie_complete_aleatoire_vs_aleatoire():
    p = _petite_partie("IA1_aleatoire", "IA1_aleatoire")
    u = p.jouer_jusqua_fin()
    assert u in (-1, 0, 1)


def test_minimax_pip_termine_partie():
    p = _petite_partie("IA2_pip", "IA1_aleatoire", seed=0)
    u = p.jouer_jusqua_fin()
    assert u in (-1, 0, 1)


def test_minimax_blocage_termine_partie():
    p = _petite_partie("IA3_blocage", "IA1_aleatoire", seed=0)
    u = p.jouer_jusqua_fin()
    assert u in (-1, 0, 1)


# -------- Tests des fonctions d'evaluation (unitaires) --------

def test_f_pip_basique():
    """f_pip = pips(adv) − pips(MAX), POV MAX."""
    main_max = [Domino(2, 2), Domino(3, 3)]  # 4 + 6 = 10 pips
    main_min = [Domino(5, 5), Domino(6, 6)]  # 10 + 12 = 22 pips
    j1 = IAAleatoire("J1", main_max, seed=0)
    j2 = IAAleatoire("J2", main_min, seed=1)
    p = Partie(j1, j2)
    # plateau vide -> non-terminal (tout domino jouable)
    assert f_pip(p, 1) == 22 - 10
    assert f_pip(p, 2) == 10 - 22


def test_f_blocage_cas1_blocage_total():
    """CAS 1 : aucun domino adv ne match les 2 extremites -> total adv pips."""
    main_max = [Domino(5, 9), Domino(0, 0)]  # MAX a un 5 -> peut jouer
    main_min = [Domino(0, 1), Domino(2, 3)]  # 6 pips, AUCUN 5
    p = _partie_avec_plateau(main_max, main_min, Domino(5, 5))
    # ext = 5, 5. MIN n'a pas de 5 -> CAS 1
    score = f_blocage(p, 1)
    assert score == 6, f"CAS 1 attendu 6, obtenu {score}"


def test_f_blocage_cas2_blocage_partiel():
    """CAS 2 : UNE extremite ne match aucun domino adv -> total adv pips - 1."""
    main_max = [Domino(5, 9), Domino(7, 9)]  # MAX peut jouer
    main_min = [Domino(7, 8), Domino(2, 3)]  # 20 pips, contient 7 mais pas 5
    p = _partie_avec_plateau(main_max, main_min, Domino(5, 7))
    # ext = 5, 7. MIN a 7 (dans 7|8) mais pas 5 -> CAS 2
    score = f_blocage(p, 1)
    assert score == 20 - 1, f"CAS 2 attendu 19, obtenu {score}"


def test_f_blocage_cas3_pas_de_blocage_extremite():
    """CAS 3 : les 2 extremites accessibles -> granulaire (somme dominos isoles)."""
    main_max = [Domino(5, 9), Domino(7, 9)]
    main_min = [
        Domino(5, 9),   # match 5
        Domino(7, 8),   # match 7
        Domino(2, 3),   # ne match ni 5 ni 7 (pips = 5)
        Domino(4, 6),   # ne match ni 5 ni 7 (pips = 10)
    ]
    p = _partie_avec_plateau(main_max, main_min, Domino(5, 7))
    # ext = 5, 7. adv match 5 (5|9), match 7 (7|8) -> CAS 3
    # dominos isoles : 2|3 (5) + 4|6 (10) = 15
    score = f_blocage(p, 1)
    assert score == 15, f"CAS 3 attendu 15, obtenu {score}"


def test_f_blocage_priorite_cas1_sur_cas2():
    """Verifie : pour le MEME adv, CAS 1 (total) DOIT donner score plus eleve que CAS 2."""
    main_max = [Domino(5, 9), Domino(7, 9), Domino(0, 0)]
    main_min = [Domino(0, 7), Domino(2, 3)]  # 12 pips, contient un 7 mais aucun 5

    # ext = 5, 5 -> adv n'a aucun 5 -> CAS 1 (total)
    p1 = _partie_avec_plateau(main_max, main_min, Domino(5, 5))
    s1 = f_blocage(p1, 1)

    # ext = 5, 7 -> adv contient 7 (dans 0|7) mais pas 5 -> CAS 2 (partiel)
    p2 = _partie_avec_plateau(main_max, main_min, Domino(5, 7))
    s2 = f_blocage(p2, 1)

    assert s1 == 12, f"CAS 1 attendu 12, obtenu {s1}"
    assert s2 == 11, f"CAS 2 attendu 11, obtenu {s2}"
    assert s1 > s2, f"CAS 1 ({s1}) DOIT etre > CAS 2 ({s2})"


def test_f_protect_miroir_de_f_blocage():
    """f_protect : miroir negatif applique a la main de MAX."""
    main_max = [Domino(0, 1), Domino(2, 3)]  # 6 pips, AUCUN 5
    main_min = [Domino(5, 9), Domino(7, 7)]  # contient un 5 -> MIN peut jouer
    p = _partie_avec_plateau(main_max, main_min, Domino(5, 5))
    # ext = 5, 5. MAX (J1) n'a pas de 5 -> CAS 1 mirror -> -6
    score = f_protect(p, 1)
    assert score == -6, f"f_protect attendu -6, obtenu {score}"


def test_f_mixte_egal_somme_des_trois():
    """f_mixte = f_pip + f_blocage + f_protect en non-terminal."""
    main_max = [Domino(3, 5), Domino(8, 9)]  # peut jouer (3 et 8)
    main_min = [Domino(0, 1), Domino(2, 4)]  # ni 3 ni 8 -> bloque
    p = _partie_avec_plateau(main_max, main_min, Domino(3, 8))
    s_pip = f_pip(p, 1)
    s_blocage = f_blocage(p, 1)
    s_protect = f_protect(p, 1)
    s_mixte = f_mixte(p, 1)
    assert s_mixte == s_pip + s_blocage + s_protect


def test_resolution_terminale_quand_partie_finie():
    """Toutes les eval renvoient ±10000 en etat terminal."""
    main_max = [Domino(0, 0)]
    main_min = []  # MIN a vide sa main -> elle a gagne -> MAX perd
    j1 = IAAleatoire("J1", main_max, seed=0)
    j2 = IAAleatoire("J2", main_min, seed=1)
    p = Partie(j1, j2)
    # MAX (J1) perd -> -10000
    assert f_pip(p, 1) == -10000
    assert f_blocage(p, 1) == -10000
    assert f_protect(p, 1) == -10000
    assert f_mixte(p, 1) == -10000


def test_plateau_vide_donne_zero_blocage_et_protect():
    """Avant le 1er coup, pas d'extremites -> f_blocage = f_protect = 0."""
    main_max = [Domino(5, 5), Domino(0, 0)]
    main_min = [Domino(3, 3), Domino(4, 4)]
    j1 = IAAleatoire("J1", main_max, seed=0)
    j2 = IAAleatoire("J2", main_min, seed=1)
    p = Partie(j1, j2)
    # plateau vide
    assert f_blocage(p, 1) == 0.0
    assert f_protect(p, 1) == 0.0
