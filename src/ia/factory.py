"""Factory pour construire les 5 niveaux d'IA du projet.

  - IA1_aleatoire   : joue au hasard (baseline)
  - IA2_pip         : Minimax + α-β profondeur 6, eval = f_pip
  - IA3_blocage     : Minimax + α-β profondeur 6, eval = f_blocage
  - IA4_protect     : Minimax + α-β profondeur 6, eval = f_protect
  - IA5_mixte       : Minimax + α-β profondeur 4, eval = f_mixte (somme des 3)
"""
from typing import Optional

from ..joueur import Joueur
from .evaluation import f_pip, f_blocage, f_protect, f_mixte
from .ia_aleatoire import IAAleatoire
from .ia_minimax import IAMinimax


NIVEAUX = (
    "IA1_aleatoire",
    "IA2_pip",
    "IA3_blocage",
    "IA4_protect",
    "IA5_mixte",
)


def creer_ia(niveau: str, nom: str, main, seed: Optional[int] = None) -> Joueur:
    if niveau == "IA1_aleatoire":
        return IAAleatoire(nom, main, seed=seed)
    if niveau == "IA2_pip":
        return IAMinimax(nom, main, profondeur=6, eval_fn=f_pip, alpha_beta=True, ordering=True)
    if niveau == "IA3_blocage":
        return IAMinimax(nom, main, profondeur=6, eval_fn=f_blocage, alpha_beta=True, ordering=True)
    if niveau == "IA4_protect":
        return IAMinimax(nom, main, profondeur=6, eval_fn=f_protect, alpha_beta=True, ordering=True)
    if niveau == "IA5_mixte":
        return IAMinimax(nom, main, profondeur=4, eval_fn=f_mixte, alpha_beta=True, ordering=True)
    raise ValueError(f"Niveau d'IA inconnu : {niveau}")
