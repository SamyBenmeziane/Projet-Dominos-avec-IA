"""Plateau linéaire de dominos avec extrémités gauche / droite."""
from typing import Optional

from .domino import Domino

Coup = tuple[Domino, str]  # (domino, position) où position ∈ {"gauche", "droite"}


class Plateau:
    def __init__(self):
        self._dominos: list[Domino] = []
        self._gauche: Optional[int] = None
        self._droite: Optional[int] = None

    @property
    def vide(self) -> bool:
        return len(self._dominos) == 0

    @property
    def extremite_gauche(self) -> Optional[int]:
        return self._gauche

    @property
    def extremite_droite(self) -> Optional[int]:
        return self._droite

    @property
    def dominos_poses(self) -> list[Domino]:
        return list(self._dominos)

    def coups_possibles(self, main: list[Domino]) -> list[Coup]:
        if self.vide:
            return [(d, "gauche") for d in main]
        coups: list[Coup] = []
        for d in main:
            if d.contient(self._gauche):
                coups.append((d, "gauche"))
            if d.contient(self._droite):
                coups.append((d, "droite"))
        return coups

    def poser(self, domino: Domino, position: str) -> bool:
        if self.vide:
            self._dominos.append(domino)
            self._gauche = domino.a
            self._droite = domino.b
            return True
        if position == "gauche":
            if not domino.contient(self._gauche):
                return False
            self._dominos.insert(0, domino)
            self._gauche = domino.autre_cote(self._gauche)
            return True
        if position == "droite":
            if not domino.contient(self._droite):
                return False
            self._dominos.append(domino)
            self._droite = domino.autre_cote(self._droite)
            return True
        return False

    def simuler(self, domino: Domino, position: str) -> "Plateau":
        copie = self._cloner_simulation()
        copie.poser(domino, position)
        return copie

    def _cloner_simulation(self) -> "Plateau":
        """Clone leger : nouvelle liste de dominos (refs partagees, Domino immuable)."""
        clone = object.__new__(Plateau)
        clone._dominos = list(self._dominos)  # COPY explicite de la liste
        clone._gauche = self._gauche  # int : valeur primitive
        clone._droite = self._droite
        return clone

    def __repr__(self) -> str:
        if self.vide:
            return "Plateau(vide)"
        chaine = " ".join(repr(d) for d in self._dominos)
        return f"Plateau([{self._gauche}] {chaine} [{self._droite}])"
