"""Lance les tournois entre IA et collecte les statistiques."""
import csv
import time
from dataclasses import dataclass, asdict
from itertools import combinations
from pathlib import Path
from typing import Callable, Optional

from ..joueur import Joueur
from ..partie import Partie
from ..ia.factory import creer_ia, NIVEAUX
from .configurations import Configuration


@dataclass
class ResultatPartie:
    couple: str
    config_id: str
    type_config: str
    variante_id: str
    swap: bool  # False : IA_A recoit Main_alpha ; True : IA_B recoit Main_alpha
    starter: str  # "A" ou "B"
    vainqueur: str  # "A", "B" ou "draw"
    pips_restants_A: int
    pips_restants_B: int
    nb_tours: int
    duree_s: float


def _construire_ias(
    niveau_a: str,
    niveau_b: str,
    main_a,
    main_b,
    seed: Optional[int],
) -> tuple[Joueur, Joueur]:
    ia_a = creer_ia(niveau_a, "IA_A", main_a, seed=seed)
    ia_b = creer_ia(niveau_b, "IA_B", main_b, seed=(seed + 1 if seed is not None else None))
    return ia_a, ia_b


def _jouer_une_partie(
    niveau_a: str,
    niveau_b: str,
    main_alpha,
    main_beta,
    swap: bool,
    seed: Optional[int],
) -> ResultatPartie:
    if not swap:
        ia_a, ia_b = _construire_ias(niveau_a, niveau_b, main_alpha, main_beta, seed)
    else:
        ia_a, ia_b = _construire_ias(niveau_a, niveau_b, main_beta, main_alpha, seed)
    partie = Partie(ia_a, ia_b)
    starter = "A" if partie.joueur_courant is ia_a else "B"
    t0 = time.perf_counter()
    u = partie.jouer_jusqua_fin(verbose=False)
    duree = time.perf_counter() - t0
    if u == 1:
        vainqueur = "A"
    elif u == -1:
        vainqueur = "B"
    else:
        vainqueur = "draw"
    return ResultatPartie(
        couple="",  # rempli par l'appelant
        config_id="",
        type_config="",
        variante_id="",
        swap=swap,
        starter=starter,
        vainqueur=vainqueur,
        pips_restants_A=ia_a.somme_pips(),
        pips_restants_B=ia_b.somme_pips(),
        nb_tours=len(partie.historique),
        duree_s=duree,
    )


def jouer_couple(
    niveau_a: str,
    niveau_b: str,
    configurations: list[Configuration],
    seed_base: int = 1000,
    callback: Optional[Callable[[ResultatPartie], None]] = None,
) -> list[ResultatPartie]:
    """Joue toutes les parties pour le couple (niveau_a, niveau_b)."""
    resultats: list[ResultatPartie] = []
    couple = f"{niveau_a}__vs__{niveau_b}"
    for cfg_idx, cfg in enumerate(configurations):
        for var in cfg.variantes:
            for swap in (False, True):
                seed = seed_base + cfg_idx * 100 + hash(var.id) % 50 + (1 if swap else 0)
                r = _jouer_une_partie(
                    niveau_a, niveau_b, var.main_alpha, var.main_beta, swap, seed
                )
                r.couple = couple
                r.config_id = cfg.id
                r.type_config = cfg.type
                r.variante_id = var.id
                resultats.append(r)
                if callback:
                    callback(r)
    return resultats


def jouer_tournoi(
    configurations: list[Configuration],
    niveaux: tuple[str, ...] = NIVEAUX,
    seed_base: int = 1000,
    afficher_progres: bool = True,
) -> list[ResultatPartie]:
    """Tournoi complet : tous les couples uniques de IA jouent l'ensemble des configurations."""
    tous: list[ResultatPartie] = []
    couples = list(combinations(niveaux, 2))
    for idx, (a, b) in enumerate(couples, 1):
        if afficher_progres:
            print(f"[{idx}/{len(couples)}] Couple : {a} vs {b}")
        t0 = time.perf_counter()
        res = jouer_couple(a, b, configurations, seed_base=seed_base)
        if afficher_progres:
            n = len(res)
            wa = sum(1 for r in res if r.vainqueur == "A")
            wb = sum(1 for r in res if r.vainqueur == "B")
            d = sum(1 for r in res if r.vainqueur == "draw")
            dt = time.perf_counter() - t0
            print(
                f"  -> {n} parties en {dt:.1f}s | A: {wa}, B: {wb}, nul: {d}"
            )
        tous.extend(res)
    return tous


def sauvegarder_csv(resultats: list[ResultatPartie], chemin: Path) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(resultats[0]).keys()))
        writer.writeheader()
        for r in resultats:
            writer.writerow(asdict(r))


# ---------- Synthese -----------

def synthese_par_couple(resultats: list[ResultatPartie]) -> dict:
    """Calcule pour chaque couple : taux de victoire, avantage premier joueur, etc."""
    couples: dict[str, list[ResultatPartie]] = {}
    for r in resultats:
        couples.setdefault(r.couple, []).append(r)

    out = {}
    for couple, parties in couples.items():
        n = len(parties)
        wa = sum(1 for r in parties if r.vainqueur == "A")
        wb = sum(1 for r in parties if r.vainqueur == "B")
        nul = sum(1 for r in parties if r.vainqueur == "draw")
        # avantage premier joueur : taux de victoire du starter
        starter_wins = sum(1 for r in parties if r.vainqueur == r.starter)
        # detail par type
        par_type: dict[str, dict] = {}
        for r in parties:
            d = par_type.setdefault(r.type_config, {"n": 0, "A": 0, "B": 0, "nul": 0})
            d["n"] += 1
            d[r.vainqueur if r.vainqueur != "draw" else "nul"] += 1
        out[couple] = {
            "n_parties": n,
            "victoires_A": wa,
            "victoires_B": wb,
            "nuls": nul,
            "taux_A": wa / n if n else 0.0,
            "taux_B": wb / n if n else 0.0,
            "avantage_starter": starter_wins / n if n else 0.0,
            "duree_moyenne_s": sum(r.duree_s for r in parties) / n if n else 0.0,
            "par_type": par_type,
        }
    return out
