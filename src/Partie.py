"""Moteur de jeu : Partie."""
from typing import Optional

from .domino import Domino, VALEUR_MAX
from .joueur import Joueur
from .plateau import Plateau, Coup


class Partie:
    """Etat du jeu = (plateau, mains des joueurs, joueur courant)."""

    def __init__(self, joueur1: Joueur, joueur2: Joueur):
        self._j1 = joueur1
        self._j2 = joueur2
        self._plateau = Plateau()
        self._courant = self._determiner_premier()
        self._historique: list[tuple[str, Optional[Coup]]] = []

    def _determiner_premier(self) -> Joueur:
        for valeur in range(VALEUR_MAX, -1, -1):
            d = Domino(valeur, valeur)
            if d in self._j1.main:
                return self._j1
            if d in self._j2.main:
                return self._j2
        return self._j1

    @property
    def plateau(self) -> Plateau:
        return self._plateau

    @property
    def joueur1(self) -> Joueur:
        return self._j1

    @property
    def joueur2(self) -> Joueur:
        return self._j2

    @property
    def joueur_courant(self) -> Joueur:
        return self._courant

    @property
    def adversaire(self) -> Joueur:
        return self._j2 if self._courant is self._j1 else self._j1

    @property
    def historique(self) -> list[tuple[str, Optional[Coup]]]:
        return list(self._historique)

    def changer_joueur(self) -> None:
        self._courant = self.adversaire

    def est_terminee(self) -> bool:
        if self._j1.a_gagne() or self._j2.a_gagne():
            return True
        coups_j1 = self._plateau.coups_possibles(self._j1.main)
        coups_j2 = self._plateau.coups_possibles(self._j2.main)
        return not coups_j1 and not coups_j2

    def utility(self) -> Optional[int]:
        """+1 si J1 gagne, -1 si J2 gagne, 0 si égalité, None sinon."""
        if not self.est_terminee():
            return None
        if self._j1.a_gagne():
            return 1
        if self._j2.a_gagne():
            return -1
        s1, s2 = self._j1.somme_pips(), self._j2.somme_pips()
        if s1 < s2:
            return 1
        if s2 < s1:
            return -1
        return 0

    def coup_force(self) -> Optional[Coup]:
        """Sur plateau vide : pose forcée du plus fort double du joueur courant."""
        if not self._plateau.vide:
            return None
        for valeur in range(VALEUR_MAX, -1, -1):
            d = Domino(valeur, valeur)
            if d in self._courant.main:
                return (d, "gauche")
        return None

    def jouer_coup(self, domino: Domino, position: str) -> bool:
        ok = self._plateau.poser(domino, position)
        if ok:
            self._courant.retirer(domino)
            self._historique.append((self._courant.nom, (domino, position)))
            self.changer_joueur()
        return ok

    def jouer_tour(self, verbose: bool = False) -> bool:
        if self.est_terminee():
            return False
        coups = self._plateau.coups_possibles(self._courant.main)
        if not coups:
            if verbose:
                print(f"{self._courant.nom} passe son tour (aucun coup possible).")
            self._historique.append((self._courant.nom, None))
            self.changer_joueur()
            return True
        forced = self.coup_force()
        if forced is not None:
            if verbose:
                print(f"{self._courant.nom} pose le double forcé {forced[0]}.")
            self.jouer_coup(*forced)
            return True
        choix = self._courant.choisir_coup(self)
        if choix is None:
            self._historique.append((self._courant.nom, None))
            self.changer_joueur()
            return True
        if verbose:
            print(f"{self._courant.nom} pose {choix[0]} à {choix[1]}.")
        self.jouer_coup(*choix)
        return True

    def jouer_jusqua_fin(self, verbose: bool = False) -> int:
        while self.jouer_tour(verbose=verbose):
            pass
        return self.utility()

    def cloner(self) -> "Partie":
        """Clone leger pour les simulations Minimax.

        Tout etat modifiable est copie : nouvelles listes pour la main de chaque
        joueur, pour le plateau et pour l'historique. Les dominos eux-memes
        sont immuables et peuvent etre partages sans risque.
        """
        clone = object.__new__(Partie)
        clone._j1 = self._j1._cloner_simulation()
        clone._j2 = self._j2._cloner_simulation()
        clone._plateau = self._plateau._cloner_simulation()
        clone._historique = list(self._historique)  # COPY explicite
        clone._courant = clone._j1 if self._courant is self._j1 else clone._j2
        return clone
