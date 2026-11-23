"""IA Minimax avec élagage alpha-bêta optionnel et move ordering optionnel."""
import math
from typing import Optional

from ..joueur import Joueur
from ..plateau import Coup
from .evaluation import EvalFn, f_pip


class IAMinimax(Joueur):
    """Minimax (avec ou sans alpha-bêta) à profondeur fixe.

    - profondeur : nombre de demi-coups explorés
    - eval_fn    : fonction d'évaluation (signature (partie, max_id) -> float)
    - alpha_beta : active l'élagage alpha-bêta
    - ordering   : trie les coups (gros pips en premier) pour améliorer l'élagage
    """

    def __init__(
        self,
        nom: str,
        main,
        profondeur: int = 4,
        eval_fn: EvalFn = f_pip,
        alpha_beta: bool = True,
        ordering: bool = False,
    ):
        super().__init__(nom, main)
        self._prof = profondeur
        self._eval = eval_fn
        self._alpha_beta = alpha_beta
        self._ordering = ordering
        self._noeuds_explores = 0
        self._coups_elagues = 0

    @property
    def noeuds_explores(self) -> int:
        return self._noeuds_explores

    @property
    def coups_elagues(self) -> int:
        return self._coups_elagues

    def reinit_stats(self) -> None:
        self._noeuds_explores = 0
        self._coups_elagues = 0

    def _id_dans(self, partie) -> int:
        return 1 if self is partie.joueur1 else 2

    def _ordonner(self, coups: list[Coup]) -> list[Coup]:
        if not self._ordering:
            return coups
        return sorted(coups, key=lambda c: -c[0].pips())

    def choisir_coup(self, partie) -> Optional[Coup]:
        self.reinit_stats()
        coups = partie.plateau.coups_possibles(self._main)
        if not coups:
            return None
        if len(coups) == 1:
            return coups[0]

        max_id = self._id_dans(partie)
        meilleur_coup: Optional[Coup] = None
        meilleure_val = -math.inf
        alpha, beta = -math.inf, math.inf

        for coup in self._ordonner(coups):
            partie_apres = partie.cloner()
            partie_apres.jouer_coup(*coup)
            val = self._minimax(partie_apres, self._prof - 1, alpha, beta, max_id)
            if val > meilleure_val:
                meilleure_val = val
                meilleur_coup = coup
            if self._alpha_beta:
                alpha = max(alpha, val)
                if alpha >= beta:
                    self._coups_elagues += 1
                    break
        return meilleur_coup

    def _minimax(self, partie, prof: int, alpha: float, beta: float, max_id: int) -> float:
        self._noeuds_explores += 1
        if prof == 0 or partie.est_terminee():
            return self._eval(partie, max_id)

        coups = partie.plateau.coups_possibles(partie.joueur_courant.main)
        if not coups:
            partie_pass = partie.cloner()
            partie_pass.changer_joueur()
            if partie_pass.est_terminee():
                return self._eval(partie_pass, max_id)
            return self._minimax(partie_pass, prof - 1, alpha, beta, max_id)

        coups = self._ordonner(coups)
        courant_id = 1 if partie.joueur_courant is partie.joueur1 else 2
        est_max = courant_id == max_id

        if est_max:
            val = -math.inf
            for coup in coups:
                p = partie.cloner()
                p.jouer_coup(*coup)
                val = max(val, self._minimax(p, prof - 1, alpha, beta, max_id))
                if self._alpha_beta:
                    alpha = max(alpha, val)
                    if alpha >= beta:
                        self._coups_elagues += 1
                        break
            return val
        else:
            val = math.inf
            for coup in coups:
                p = partie.cloner()
                p.jouer_coup(*coup)
                val = min(val, self._minimax(p, prof - 1, alpha, beta, max_id))
                if self._alpha_beta:
                    beta = min(beta, val)
                    if alpha >= beta:
                        self._coups_elagues += 1
                        break
            return val
