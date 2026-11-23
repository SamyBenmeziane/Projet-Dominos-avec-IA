"""Génération des 15 configurations stratifiées + 3 variantes chacune.

Stratégie :
  - 5 types de positions : ouverte / fermee / equilibree / avantage_alpha / avantage_beta
  - 3 configurations de base par type (= 15 configurations)
  - 3 variantes par configuration : v0 (originale), v1 et v2 (échanges légers
    de 2 dominos entre les deux mains, en préservant 10|10 dans Main_alpha
    et la classification)
  - Total : 15 x 3 = 45 paires (Main_alpha, Main_beta), jouées 2 fois chacune
    avec inversion de l'attribution des mains entre les 2 IA -> 90 parties.
"""
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..domino import Domino, jeu_complet


TYPES = ("ouverte", "fermee", "equilibree", "avantage_alpha", "avantage_beta")
NB_CONFIGS_PAR_TYPE = 2  # 5 types × 2 = 10 configurations
NB_VARIANTES = 3  # v0 + 2 échanges légers


@dataclass
class Variante:
    id: str  # e.g. "v0", "v1", "v2"
    main_alpha: list[Domino]
    main_beta: list[Domino]


@dataclass
class Configuration:
    id: str
    type: str
    variantes: list[Variante] = field(default_factory=list)


def diversite(main: list[Domino]) -> int:
    return len({v for d in main for v in (d.a, d.b)})


def classifier(main_a: list[Domino], main_b: list[Domino]) -> str:
    """Classifie la paire de mains. main_a contient 10|10."""
    pips_a = sum(d.pips() for d in main_a)
    pips_b = sum(d.pips() for d in main_b)
    diff = pips_a - pips_b
    div_a, div_b = diversite(main_a), diversite(main_b)

    if div_a <= 9 or div_b <= 9:
        return "fermee"
    if abs(diff) < 10:
        return "equilibree"
    if diff <= -20:
        return "avantage_alpha"
    if diff >= 20:
        return "avantage_beta"
    return "ouverte"


def _split_aleatoire(rng: random.Random) -> tuple[list[Domino], list[Domino]]:
    """Distribution aléatoire 33/33 avec 10|10 garanti dans main_alpha."""
    dominos = jeu_complet()
    rng.shuffle(dominos)
    a, b = dominos[:33], dominos[33:]
    d10 = Domino(10, 10)
    if d10 not in a:
        # echange : retire un domino de a, met d10 a la place et inverse
        idx_a = rng.randrange(33)
        idx_b = b.index(d10)
        a[idx_a], b[idx_b] = b[idx_b], a[idx_a]
    return a, b


def _generer_fermee(rng: random.Random) -> tuple[list[Domino], list[Domino]]:
    """Construit deliberement une main_beta concentree (faible diversite)."""
    valeurs_exclues = rng.sample(range(0, 11), k=2)  # 2 valeurs absentes de main_beta
    pool_b: list[Domino] = []
    pool_a: list[Domino] = []
    for d in jeu_complet():
        if d.a in valeurs_exclues or d.b in valeurs_exclues or d == Domino(10, 10):
            pool_a.append(d)
        else:
            pool_b.append(d)
    rng.shuffle(pool_a)
    rng.shuffle(pool_b)
    main_a = pool_a[:33]
    reste = pool_a[33:]
    main_b = pool_b + reste
    main_b = main_b[:33]
    # securite : si depassement, on rectifie
    while len(main_a) < 33:
        main_a.append(main_b.pop())
    while len(main_b) < 33:
        main_b.append(main_a.pop())
    if Domino(10, 10) not in main_a:
        # forcer
        idx_a = next(i for i, d in enumerate(main_a) if d != Domino(10, 10))
        idx_b = main_b.index(Domino(10, 10))
        main_a[idx_a], main_b[idx_b] = main_b[idx_b], main_a[idx_a]
    return main_a, main_b


def _generer_variante(
    main_a: list[Domino], main_b: list[Domino], type_cible: str, rng: random.Random
) -> tuple[list[Domino], list[Domino]]:
    """Genere une variante par echange de 2 dominos en preservant la classification."""
    d10 = Domino(10, 10)
    for _ in range(200):
        new_a = list(main_a)
        new_b = list(main_b)
        candidats_a = [i for i, d in enumerate(new_a) if d != d10]
        if len(candidats_a) < 2:
            break
        i1, i2 = rng.sample(candidats_a, 2)
        j1, j2 = rng.sample(range(len(new_b)), 2)
        new_a[i1], new_b[j1] = new_b[j1], new_a[i1]
        new_a[i2], new_b[j2] = new_b[j2], new_a[i2]
        if d10 in new_a and classifier(new_a, new_b) == type_cible:
            return new_a, new_b
    # fallback : echange minimal qui preserve d10
    return main_a, main_b


def generer_configurations(seed: int = 42) -> list[Configuration]:
    """Genere les 15 configurations + 3 variantes chacune."""
    rng = random.Random(seed)
    par_type: dict[str, list[Configuration]] = {t: [] for t in TYPES}

    # Tentative 1 : echantillonnage aleatoire pour la plupart des types
    for tentative in range(2000):
        if all(len(par_type[t]) >= NB_CONFIGS_PAR_TYPE for t in TYPES):
            break
        a, b = _split_aleatoire(rng)
        t = classifier(a, b)
        if t == "fermee" and len(par_type[t]) >= NB_CONFIGS_PAR_TYPE:
            continue
        if len(par_type[t]) < NB_CONFIGS_PAR_TYPE:
            par_type[t].append(_assembler(a, b, t, len(par_type[t]) + 1, rng))

    # Tentative 2 : si "fermee" ou autre n'a pas atteint le quota, generation deliberee
    while len(par_type["fermee"]) < NB_CONFIGS_PAR_TYPE:
        a, b = _generer_fermee(rng)
        t = classifier(a, b)
        if t == "fermee":
            par_type[t].append(_assembler(a, b, t, len(par_type[t]) + 1, rng))

    # Au cas ou un autre type manque encore, on continue d'echantillonner
    for tentative in range(5000):
        if all(len(par_type[t]) >= NB_CONFIGS_PAR_TYPE for t in TYPES):
            break
        a, b = _split_aleatoire(rng)
        t = classifier(a, b)
        if len(par_type[t]) < NB_CONFIGS_PAR_TYPE:
            par_type[t].append(_assembler(a, b, t, len(par_type[t]) + 1, rng))

    configs: list[Configuration] = []
    for t in TYPES:
        configs.extend(par_type[t][:NB_CONFIGS_PAR_TYPE])
    return configs


def _assembler(
    main_a: list[Domino], main_b: list[Domino], type_cible: str, num: int, rng: random.Random
) -> Configuration:
    cfg = Configuration(id=f"{type_cible}_{num:02d}", type=type_cible)
    cfg.variantes.append(Variante(id="v0", main_alpha=list(main_a), main_beta=list(main_b)))
    for k in range(1, NB_VARIANTES):
        va, vb = _generer_variante(main_a, main_b, type_cible, rng)
        cfg.variantes.append(Variante(id=f"v{k}", main_alpha=va, main_beta=vb))
    return cfg


# ----------- Serialisation JSON pour reproductibilite ------------

def domino_to_list(d: Domino) -> list[int]:
    return [d.a, d.b]


def list_to_domino(p: list[int]) -> Domino:
    return Domino(p[0], p[1])


def configurations_to_dict(configs: list[Configuration]) -> dict:
    return {
        "configurations": [
            {
                "id": c.id,
                "type": c.type,
                "variantes": [
                    {
                        "id": v.id,
                        "main_alpha": [domino_to_list(d) for d in v.main_alpha],
                        "main_beta": [domino_to_list(d) for d in v.main_beta],
                    }
                    for v in c.variantes
                ],
            }
            for c in configs
        ]
    }


def configurations_from_dict(data: dict) -> list[Configuration]:
    configs = []
    for c in data["configurations"]:
        cfg = Configuration(id=c["id"], type=c["type"])
        for v in c["variantes"]:
            cfg.variantes.append(
                Variante(
                    id=v["id"],
                    main_alpha=[list_to_domino(p) for p in v["main_alpha"]],
                    main_beta=[list_to_domino(p) for p in v["main_beta"]],
                )
            )
        configs.append(cfg)
    return configs


def sauvegarder(configs: list[Configuration], chemin: Path) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(configurations_to_dict(configs), f, indent=2)


def charger(chemin: Path) -> list[Configuration]:
    with open(chemin, "r", encoding="utf-8") as f:
        return configurations_from_dict(json.load(f))


def configurations_par_defaut(
    chemin: Optional[Path] = None, seed: int = 42, regenerer: bool = False
) -> list[Configuration]:
    """Charge les configurations depuis le fichier, sinon les genere et les sauve."""
    if chemin and chemin.exists() and not regenerer:
        return charger(chemin)
    configs = generer_configurations(seed=seed)
    if chemin:
        sauvegarder(configs, chemin)
    return configs
