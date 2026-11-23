"""Fonctions d'evaluation pour Minimax — du point de vue du joueur MAX.

4 fonctions distinctes, chacune incarnant une strategie pure ou combinee :

  - f_pip      : differentiel de pips (course classique)
  - f_blocage  : recompense le blocage de l'adversaire (3 cas avec priorite)
  - f_protect  : miroir de f_blocage, penalise le fait d'etre soi-meme bloque
  - f_mixte    : somme des 3 (pip + attaque + defense)

Toutes les fonctions appellent en debut un helper `_resolution_terminale`
qui ecrase tout score heuristique avec ±10000 quand la partie est finie,
afin que Minimax priorise toujours gagner sur n'importe quelle situation.
"""
from typing import Callable

from ..partie import Partie

GAIN_TERMINAL = 10_000

EvalFn = Callable[[Partie, int], float]


# ----------- Helpers communs -----------

def _resolution_terminale(partie: Partie, max_id: int) -> float:
    """Retourne ±GAIN_TERMINAL si la partie est terminee, sinon 0 (a ignorer).

    Convention : max_id = 1 si MAX = joueur1, sinon 2.
    L'utility() retourne +1 si J1 gagne, -1 si J2 gagne, 0 si nul.
    """
    u = partie.utility()
    if u is None:
        return 0.0
    if max_id == 1:
        return float(u * GAIN_TERMINAL)
    return float(-u * GAIN_TERMINAL)


def _max_min(partie: Partie, max_id: int):
    """Retourne (joueur_max, joueur_min) selon max_id."""
    if max_id == 1:
        return partie.joueur1, partie.joueur2
    return partie.joueur2, partie.joueur1


# ----------- f_pip : differentiel de pips -----------

def f_pip(partie: Partie, max_id: int) -> float:
    """Score = pips(adversaire) − pips(MAX).

    Plus l'adversaire garde de pips et plus MAX en a depense, mieux c'est.
    Bornes : [−pips_initiaux(MAX), +pips_initiaux(MIN)]
    """
    if partie.est_terminee():
        return _resolution_terminale(partie, max_id)
    j_max, j_min = _max_min(partie, max_id)
    return float(j_min.somme_pips() - j_max.somme_pips())


# ----------- f_blocage : bloquer l'adversaire (3 cas avec priorite) -----------

def f_blocage(partie: Partie, max_id: int) -> float:
    """Recompense le blocage de l'adversaire avec 3 cas hierarchises :

      CAS 1 (les 2 extremites bloquent l'adv)  → score = somme pips main adv
      CAS 2 (UNE extremite bloque l'adv)       → score = somme pips main adv − 1
      CAS 3 (aucune extremite ne bloque l'adv) → score = somme pips des dominos
                                                  adverses qui ne matchent
                                                  ni gauche ni droite

    Bornes : [0, pips_initiaux(MIN)]
    Priorite respectee : CAS 1 > CAS 2 > CAS 3 (toujours).
    """
    if partie.est_terminee():
        return _resolution_terminale(partie, max_id)

    plateau = partie.plateau
    if plateau.vide:
        return 0.0  # pas d'extremites encore -> pas de blocage possible

    _, j_min = _max_min(partie, max_id)
    g = plateau.extremite_gauche
    d_ext = plateau.extremite_droite

    adv_has_g = any(dom.contient(g) for dom in j_min.main)
    adv_has_d = any(dom.contient(d_ext) for dom in j_min.main)

    total_pips_adv = j_min.somme_pips()

    # CAS 1 — blocage TOTAL
    if not adv_has_g and not adv_has_d:
        return float(total_pips_adv)

    # CAS 2 — blocage PARTIEL (une seule extremite fermee a l'adv)
    if not adv_has_g or not adv_has_d:
        return float(total_pips_adv - 1)

    # CAS 3 — aucune extremite ne bloque l'adv : on compte au domino pres
    pips_isoles = sum(
        dom.pips() for dom in j_min.main
        if not dom.contient(g) and not dom.contient(d_ext)
    )
    return float(pips_isoles)


# ----------- f_protect : miroir de f_blocage (eviter d'etre bloque) -----------

def f_protect(partie: Partie, max_id: int) -> float:
    """Miroir de f_blocage applique a NOTRE main, signe negatif.

      CAS 1 (les 2 extremites NOUS bloquent)   → −somme pips MA main
      CAS 2 (UNE extremite NOUS bloque)        → −(somme pips MA main − 1)
                                                 = −somme pips MA main + 1
      CAS 3 (aucune ne nous bloque)            → −somme pips des MES dominos
                                                  qui ne matchent ni g ni d

    Bornes : [−pips_initiaux(MAX), 0]
    """
    if partie.est_terminee():
        return _resolution_terminale(partie, max_id)

    plateau = partie.plateau
    if plateau.vide:
        return 0.0

    j_max, _ = _max_min(partie, max_id)
    g = plateau.extremite_gauche
    d_ext = plateau.extremite_droite

    me_has_g = any(dom.contient(g) for dom in j_max.main)
    me_has_d = any(dom.contient(d_ext) for dom in j_max.main)

    total_pips_me = j_max.somme_pips()

    # CAS 1 — JE suis totalement bloque
    if not me_has_g and not me_has_d:
        return float(-total_pips_me)

    # CAS 2 — UNE de mes extremites est fermee
    if not me_has_g or not me_has_d:
        return float(-(total_pips_me - 1))

    # CAS 3 — pas de blocage d'extremite, on compte les dominos isoles
    pips_isoles = sum(
        dom.pips() for dom in j_max.main
        if not dom.contient(g) and not dom.contient(d_ext)
    )
    return float(-pips_isoles)


# ----------- f_mixte : somme des 3 -----------

def f_mixte(partie: Partie, max_id: int) -> float:
    """Combine f_pip + f_blocage + f_protect (course pip + attaque + defense).

    Bornes approximatives : [−2 × pips_initiaux(MAX), +2 × pips_initiaux(MIN)]
    """
    if partie.est_terminee():
        return _resolution_terminale(partie, max_id)
    return f_pip(partie, max_id) + f_blocage(partie, max_id) + f_protect(partie, max_id)


EVALUATIONS: dict[str, EvalFn] = {
    "f_pip": f_pip,
    "f_blocage": f_blocage,
    "f_protect": f_protect,
    "f_mixte": f_mixte,
}
