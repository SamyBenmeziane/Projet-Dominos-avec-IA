"""Joueur abstrait + joueur humain."""
from abc import ABC, abstractmethod
from typing import Optional

from .domino import Domino
from .plateau import Coup


class Joueur(ABC):
    def __init__(self, nom: str, main: list[Domino]):
        self._nom = nom
        self._main: list[Domino] = list(main)

    @property
    def nom(self) -> str:
        return self._nom

    @property
    def main(self) -> list[Domino]:
        return list(self._main)

    def a_gagne(self) -> bool:
        return len(self._main) == 0

    def somme_pips(self) -> int:
        return sum(d.pips() for d in self._main)

    def retirer(self, domino: Domino) -> None:
        self._main.remove(domino)

    @abstractmethod
    def choisir_coup(self, partie) -> Optional[Coup]:
        ...

    def _cloner_simulation(self) -> "Joueur":
        """Clone leger destine aux simulations Minimax.

        Cree une nouvelle instance avec :
          - _main : NOUVELLE liste (copie superficielle, Domino etant immuable)
          - autres attributs : partages superficiellement (RNG, eval_fn, ...)
            car le clone ne servira jamais a choisir un coup.
        """
        clone = object.__new__(type(self))
        clone.__dict__.update(self.__dict__)
        clone._main = list(self._main)  # COPY explicite de la liste
        return clone

    def __repr__(self) -> str:
        return f"{self._nom}({len(self._main)} dominos, {self.somme_pips()} pips)"


class JoueurHumain(Joueur):
    def choisir_coup(self, partie) -> Optional[Coup]:
        coups = partie.plateau.coups_possibles(self._main)
        if not coups:
            return None
        print(f"\n--- Tour de {self._nom} ---")
        print(f"Plateau : {partie.plateau}")
        print(f"Votre main ({len(self._main)} dominos) : {self._main}")
        print("Coups possibles :")
        for i, (d, pos) in enumerate(coups):
            print(f"  [{i}] {d} -> {pos}")
        while True:
            entree = input("Votre choix (numéro) : ").strip()
            try:
                choix = int(entree)
                if 0 <= choix < len(coups):
                    return coups[choix]
            except ValueError:
                pass
            print("Choix invalide, réessayez.")
