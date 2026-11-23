"""Domino non orienté : paire (a, b) avec a <= b par convention."""

VALEUR_MAX = 10


class Domino:
    __slots__ = ("_a", "_b")

    def __init__(self, a: int, b: int):
        if not (0 <= a <= VALEUR_MAX and 0 <= b <= VALEUR_MAX):
            raise ValueError(f"Valeurs invalides : ({a}, {b})")
        self._a = min(a, b)
        self._b = max(a, b)

    @property
    def a(self) -> int:
        return self._a

    @property
    def b(self) -> int:
        return self._b

    def est_double(self) -> bool:
        return self._a == self._b

    def pips(self) -> int:
        return self._a + self._b

    def contient(self, valeur: int) -> bool:
        return valeur == self._a or valeur == self._b

    def autre_cote(self, valeur: int) -> int:
        if valeur == self._a:
            return self._b
        if valeur == self._b:
            return self._a
        raise ValueError(f"Le domino {self} ne contient pas {valeur}")

    def __eq__(self, other) -> bool:
        return isinstance(other, Domino) and self._a == other._a and self._b == other._b

    def __hash__(self) -> int:
        return hash((self._a, self._b))

    def __repr__(self) -> str:
        return f"[{self._a}|{self._b}]"


def jeu_complet() -> list[Domino]:
    """Génère les 66 dominos du jeu double-10 (de 0|0 à 10|10)."""
    return [Domino(i, j) for i in range(VALEUR_MAX + 1) for j in range(i, VALEUR_MAX + 1)]
