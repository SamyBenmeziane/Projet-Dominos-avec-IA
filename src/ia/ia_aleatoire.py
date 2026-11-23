"""IA-1 : choisit un coup légal au hasard."""
import random
from typing import Optional

from ..joueur import Joueur
from ..plateau import Coup


class IAAleatoire(Joueur):
    def __init__(self, nom: str, main, seed: Optional[int] = None):
        super().__init__(nom, main)
        self._rng = random.Random(seed)

    def choisir_coup(self, partie) -> Optional[Coup]:
        coups = partie.plateau.coups_possibles(self._main)
        if not coups:
            return None
        return self._rng.choice(coups)
